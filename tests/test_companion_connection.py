"""Companion cache polling, identity-preserving migration and repair boundaries."""

from copy import deepcopy
from types import SimpleNamespace
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from homeassistant.config_entries import ConfigEntryState
from homeassistant.exceptions import ConfigEntryAuthFailed
from homeassistant.helpers import issue_registry as ir
from homeassistant.helpers.update_coordinator import UpdateFailed
from pytest_homeassistant_custom_component.common import MockConfigEntry
from test_companion_transport import NOW, VIN, _field, _snapshot

from custom_components.nio_telematics.companion_coordinator import (
    CompanionDataUpdateCoordinator,
    snapshot_to_vehicle,
)
from custom_components.nio_telematics.companion_snapshot import parse_companion_snapshot
from custom_components.nio_telematics.companion_transport import CompanionFetchError
from custom_components.nio_telematics.config_flow import NioConfigFlow
from custom_components.nio_telematics.const import (
    COMPANION_CONNECTIONS_URL,
    CONF_COMPANION_CREDENTIAL,
    CONF_COMPANION_VEHICLE_KEY,
    CONF_CONNECTION_METHOD,
    DOMAIN,
)
from custom_components.nio_telematics.diagnostics import (
    async_get_config_entry_diagnostics,
)
from custom_components.nio_telematics.sensor import (
    SENSORS,
    NioOdometerSensor,
    NioSensor,
    NioSocSensor,
)
from custom_components.nio_telematics.source_switch import (
    SourceSwitchError,
    async_switch_source,
)

TOKEN = "hap1_" + "p" * 43


@pytest.fixture(autouse=True)
def contract_clock(freezer):
    freezer.move_to(NOW)


def snapshot():
    payload = _snapshot()
    payload["fields"]["rangeKm"] = _field(269, "km", "soc_status")
    payload["fields"]["odometerKm"] = _field(6428, "km", "vehicle_status")
    return parse_companion_snapshot(payload)


def entry():
    return MockConfigEntry(
        domain=DOMAIN,
        title="Test car",
        unique_id=VIN,
        data={
            "vin": VIN,
            CONF_CONNECTION_METHOD: "companion",
            CONF_COMPANION_CREDENTIAL: TOKEN,
            CONF_COMPANION_VEHICLE_KEY: "a" * 64,
        },
        options={"vehicle_dashboard": {"model": "auto"}},
    )


async def test_upstream_reauth_keeps_ha_credential_and_recovers(hass):
    car = entry()
    car.add_to_hass(hass)
    client = SimpleNamespace(
        async_fetch=AsyncMock(
            side_effect=[
                CompanionFetchError("upstream_reauthorization_required"),
                snapshot(),
            ]
        )
    )
    coordinator = CompanionDataUpdateCoordinator(hass, car, client)
    with pytest.raises(UpdateFailed, match="upstream_reauthorization_required"):
        await coordinator._async_update_data()
    issue_id = f"companion_source_{car.entry_id}"
    issue = ir.async_get(hass).async_get_issue(DOMAIN, issue_id)
    assert issue is not None
    assert issue.learn_more_url == COMPANION_CONNECTIONS_URL
    assert car.data[CONF_COMPANION_CREDENTIAL] == TOKEN
    assert not list(hass.config_entries.flow.async_progress())
    recovered = await coordinator._async_update_data()
    assert recovered.soc_status.soc == 48.5
    assert ir.async_get(hass).async_get_issue(DOMAIN, issue_id) is None
    assert car.data[CONF_COMPANION_CREDENTIAL] == TOKEN


async def test_revoked_consumer_requires_ha_reauth(hass):
    car = entry()
    client = SimpleNamespace(
        async_fetch=AsyncMock(
            side_effect=CompanionFetchError("consumer_reauthentication_required")
        )
    )
    coordinator = CompanionDataUpdateCoordinator(hass, car, client)
    with pytest.raises(ConfigEntryAuthFailed, match="HA access was revoked"):
        await coordinator._async_update_data()
    assert car.data[CONF_COMPANION_CREDENTIAL] == TOKEN


@pytest.mark.parametrize(
    "kind", ["retry_later", "identity_mismatch", "invalid_response"]
)
async def test_temporary_or_identity_errors_do_not_expose_or_replace_credential(
    hass, kind
):
    car = entry()
    client = SimpleNamespace(
        async_fetch=AsyncMock(side_effect=CompanionFetchError(kind))
    )
    coordinator = CompanionDataUpdateCoordinator(hass, car, client)
    with pytest.raises(UpdateFailed) as caught:
        await coordinator._async_update_data()
    assert TOKEN not in str(caught.value)
    assert car.data[CONF_COMPANION_CREDENTIAL] == TOKEN
    assert not list(hass.config_entries.flow.async_progress())


def test_adapter_preserves_clocks_native_units_zero_and_duplicate_retention():
    initial = snapshot_to_vehicle(snapshot())
    repeated = snapshot_to_vehicle(snapshot(), initial)
    assert repeated.soc_status.soc == 48.5
    assert repeated.soc_status.remaining_range == 269
    assert repeated.telemetry["vehicle_status"]["mileage"] == 6428
    assert repeated.soc_last_valid_at == initial.soc_last_valid_at
    assert repeated.soc_retained
    assert repeated.telemetry["vehicle_status"]["_odometer_retained"]
    assert repeated.soc_last_valid_at != repeated.fetched_at
    assert (
        repeated.field_metadata["socPercent"]["received_at"] == snapshot().snapshot_at
    )
    payload = _snapshot()
    payload["fields"]["socPercent"]["value"] = 0
    assert snapshot_to_vehicle(parse_companion_snapshot(payload)).soc_status.soc == 0


def test_stale_values_and_direct_only_sensors_do_not_reappear_from_restore(freezer):
    car = entry()
    coordinator = MagicMock(config_entry=car, last_update_success=True)
    coordinator.data = snapshot_to_vehicle(snapshot())
    descriptions = {s.key: s for s in SENSORS}
    soc = NioSocSensor(coordinator, descriptions["battery_state_of_charge"])
    assert soc.available
    assert soc.unique_id == f"{VIN}_battery_state_of_charge"
    assert NioOdometerSensor(coordinator, descriptions["odometer"]).available
    assert not NioSensor(coordinator, descriptions["speed"]).available
    freezer.move_to("2026-10-20T19:20:00Z")
    coordinator.data = snapshot_to_vehicle(snapshot())
    soc._restored_soc = 99
    assert not soc.available
    assert not NioOdometerSensor(coordinator, descriptions["odometer"]).available


async def test_companion_diagnostics_redact_credentials_and_vehicle_identity(hass):
    car = entry()
    car.runtime_data = SimpleNamespace(
        data=snapshot_to_vehicle(snapshot()), last_update_success=True
    )
    diagnostics = await async_get_config_entry_diagnostics(hass, car)
    assert TOKEN not in str(diagnostics)
    assert VIN not in str(diagnostics)
    assert "a" * 64 not in str(diagnostics)


@pytest.mark.parametrize("fail", [False, True])
async def test_source_transaction_preserves_entry_and_restores_failed_setup(fail):
    car = SimpleNamespace(
        entry_id="same-entry",
        unique_id=VIN,
        title="Test car",
        data={"vin": VIN, "token": {"access_token": "old-fixture"}},
        options={"vehicle_dashboard": {"model": "auto"}},
        state=ConfigEntryState.LOADED,
    )
    original = deepcopy(car.data)
    manager = SimpleNamespace()
    calls = []

    async def unload(entry_id):
        assert entry_id == car.entry_id
        calls.append("unload")
        car.state = ConfigEntryState.NOT_LOADED
        return True

    async def setup(entry_id):
        calls.append("setup:" + car.data.get(CONF_CONNECTION_METHOD, "direct"))
        if fail and car.data.get(CONF_CONNECTION_METHOD) == "companion":
            car.state = ConfigEntryState.SETUP_RETRY
            return False
        car.state = ConfigEntryState.LOADED
        return True

    def update(target, *, data):
        assert target is car
        target.data = data

    manager.async_unload = unload
    manager.async_setup = setup
    manager.async_update_entry = update
    fake_hass = SimpleNamespace(data={}, config_entries=manager)
    change = {CONF_CONNECTION_METHOD: "companion", CONF_COMPANION_CREDENTIAL: TOKEN}
    if fail:
        with pytest.raises(SourceSwitchError, match="source_switch_failed"):
            await async_switch_source(fake_hass, car, change)
        assert car.data == original
        assert calls == ["unload", "setup:companion", "unload", "setup:direct"]
    else:
        await async_switch_source(fake_hass, car, change)
        assert calls == ["unload", "setup:companion"]
        assert car.data["token"] == original["token"]
    assert car.entry_id == "same-entry"
    assert car.unique_id == VIN
    assert car.options == {"vehicle_dashboard": {"model": "auto"}}


async def test_switch_preflight_rejects_proof_credential_before_mutation(hass):
    handler = NioConfigFlow()
    handler.hass = hass
    handler.context = {"source": "reconfigure"}
    car = entry()
    with (
        patch.object(handler, "_get_reconfigure_entry", return_value=car),
        patch(
            "custom_components.nio_telematics.config_flow.async_switch_source"
        ) as switch,
    ):
        result = await handler.async_step_companion(
            {
                CONF_COMPANION_CREDENTIAL: "ha1_" + "p" * 43,
            }
        )
    assert result["errors"]["base"] == "persistent_credential_required"
    switch.assert_not_called()


async def test_confirm_rechecks_coverage_before_switch_and_preserves_entry(hass):
    handler = NioConfigFlow()
    handler.hass = hass
    handler.context = {"source": "reconfigure"}
    handler._companion_input = {CONF_COMPANION_CREDENTIAL: TOKEN}
    car = entry()
    candidate = SimpleNamespace(snapshot=snapshot())
    with (
        patch.object(handler, "_get_reconfigure_entry", return_value=car),
        patch.object(
            handler,
            "_companion_candidate",
            AsyncMock(
                side_effect=[CompanionFetchError("insufficient_coverage"), candidate]
            ),
        ),
        patch(
            "custom_components.nio_telematics.config_flow.async_switch_source",
            new_callable=AsyncMock,
        ) as switch,
        patch.object(handler, "async_update_reload_and_abort") as finish,
    ):
        rejected = await handler.async_step_confirm_source({})
        assert rejected["errors"]["base"] == "insufficient_coverage"
        switch.assert_not_awaited()
        await handler.async_step_confirm_source({})
        assert switch.await_args.args[1] is car
        finish.assert_called_once_with(car, reload_even_if_entry_is_unchanged=False)


async def test_restart_uses_same_consumer_and_pins_vehicle_key(hass):
    car = entry()
    client = SimpleNamespace(async_fetch=AsyncMock(return_value=snapshot()))
    before = deepcopy(dict(car.data))
    first = CompanionDataUpdateCoordinator(hass, car, client)
    second = CompanionDataUpdateCoordinator(hass, car, client)
    assert (await first._async_update_data()).soc_status.soc == 48.5
    assert (await second._async_update_data()).soc_status.soc == 48.5
    assert car.data == before
    for call in client.async_fetch.await_args_list:
        assert call.kwargs == {"expected_vin": VIN, "expected_vehicle_key": "a" * 64}


async def test_ledger_switch_creates_one_baseline_and_preserves_archive(hass, freezer):
    from custom_components.nio_telematics.car_dashboard.coordinator import (
        CarLedgerCoordinator,
    )
    from custom_components.nio_telematics.car_dashboard.ledger import Ledger

    now = snapshot().snapshot_at.timestamp()
    settings = {
        "capacity_kwh": 90,
        "full_range_km": 557,
        "odometer": "sensor.test_odo",
        "soc": "sensor.test_soc",
        "range": "sensor.test_range",
        "home_history": "sensor.test_history",
        "home_connected": "binary_sensor.test_connected",
    }
    coordinator = CarLedgerCoordinator(
        hass, SimpleNamespace(entry_id="test-ledger", data=settings)
    )
    coordinator.ledger = Ledger(coordinator.settings)
    coordinator.ledger.ingest(now - 300, 6427, None, soc_pct=60)
    coordinator.ledger.add_charge(now - 1000, now - 900, 2, price=0.5)
    archived = deepcopy(coordinator.ledger.data["charges"])
    coordinator.store = SimpleNamespace(async_save=AsyncMock())
    coordinator.cost_recorder = SimpleNamespace(refresh=AsyncMock())
    # Source samples are aligned and the changed percentage is deliberately
    # large: comparing sources would invent >10 kWh of parked/driving energy.
    hass.states.async_set(
        "sensor.test_soc",
        "48.5",
        {
            "last_valid_sample": "2026-10-20T18:59:00Z",
            "telemetry_source": "companion",
            "source_generation": 2,
        },
    )
    hass.states.async_set(
        "sensor.test_odo",
        "6428",
        {
            "source_sample": "2026-10-20T18:59:05Z",
        },
    )
    await coordinator.sample()
    assert coordinator.ledger.data["telemetry_source"] == "companion:2"
    assert coordinator.ledger.data["parked_losses"] == []
    assert coordinator.ledger.data["charges"] == archived
    transitions = deepcopy(coordinator.ledger.data["source_transitions"])
    await coordinator.sample()
    assert coordinator.ledger.data["source_transitions"] == transitions
    assert coordinator.ledger.data["charges"] == archived
