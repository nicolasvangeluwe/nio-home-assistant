"""Companion cache polling, identity-preserving migration and repair boundaries."""

from copy import deepcopy
from types import SimpleNamespace
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from homeassistant import config_entries
from homeassistant.config_entries import ConfigEntryDisabler, ConfigEntryState
from homeassistant.data_entry_flow import AbortFlow, FlowResultType
from homeassistant.exceptions import ConfigEntryAuthFailed
from homeassistant.helpers import issue_registry as ir
from homeassistant.helpers.update_coordinator import UpdateFailed
from pytest_homeassistant_custom_component.common import MockConfigEntry
from test_companion_transport import NOW, VIN, _field, _Response, _Session, _snapshot

from custom_components.nio_telematics import async_setup_entry
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


@pytest.mark.parametrize("soc_value", [48.5, 0])
def test_overnight_stale_core_survives_restart_with_original_clocks(freezer, soc_value):
    payload = _snapshot()
    payload["snapshotAt"] = "2026-10-21T06:00:00.000Z"
    payload["fields"]["rangeKm"] = _field(269, "km", "soc_status")
    payload["fields"]["odometerKm"] = _field(6428, "km", "vehicle_status")
    payload["fields"]["socPercent"]["value"] = soc_value
    for field in payload["fields"].values():
        field["quality"] = "stale"
    freezer.move_to(payload["snapshotAt"])
    parsed = parse_companion_snapshot(payload)
    first = snapshot_to_vehicle(parsed)
    restarted = snapshot_to_vehicle(parsed)
    assert first.soc_status.soc == restarted.soc_status.soc == soc_value
    assert first.soc_last_valid_at == restarted.soc_last_valid_at
    assert first.soc_last_valid_at < first.fetched_at
    coordinator = MagicMock(
        config_entry=entry(), last_update_success=True, data=restarted
    )
    descriptions = {s.key: s for s in SENSORS}
    soc = NioSocSensor(coordinator, descriptions["battery_state_of_charge"])
    assert soc.available
    assert soc.extra_state_attributes["source_quality"] == "stale"
    assert soc.extra_state_attributes["data_retained"] is True
    assert soc.extra_state_attributes["fresh"] is False
    odo = NioOdometerSensor(coordinator, descriptions["odometer"])
    assert odo.available and odo.native_value == 6428
    assert odo.extra_state_attributes["fresh"] is False
    assert not NioSensor(coordinator, descriptions["vehicle_state"]).available
    assert not NioSensor(coordinator, descriptions["charging_state"]).available


@pytest.mark.parametrize(
    "reason",
    ["not_reported", "unit_unverified", "conflicting_same_time", "future_clock"],
)
def test_bad_core_never_revives_direct_restore(reason):
    payload = _snapshot()
    raw = payload["fields"]["socPercent"]
    raw["value"] = None
    raw["quality"] = "future_clock" if reason == "future_clock" else "unavailable"
    raw["reason"] = None if reason == "future_clock" else reason
    if reason in {"not_reported", "conflicting_same_time"}:
        raw.update(sourceTimestamp=None, receivedAt=None, sourceEndpoint=None)
    if reason == "future_clock":
        raw["sourceTimestamp"] = "2026-10-21T19:00:00.000Z"
    data = snapshot_to_vehicle(parse_companion_snapshot(payload))
    coordinator = MagicMock(config_entry=entry(), last_update_success=True, data=data)
    description = next(s for s in SENSORS if s.key == "battery_state_of_charge")
    sensor = NioSocSensor(coordinator, description)
    sensor._restored_soc = 99
    assert sensor.native_value is None
    assert not sensor.available


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


@pytest.mark.parametrize("finish", [False, True])
async def test_native_add_flow_targets_existing_paused_car_without_creating_entry(
    hass, finish
):
    car = MockConfigEntry(
        domain=DOMAIN,
        title="My existing car",
        unique_id=VIN,
        data={"vin": VIN, "token": {"access_token": "direct-fixture"}},
        disabled_by=ConfigEntryDisabler.USER,
    )
    car.add_to_hass(hass)
    before = dict(car.data)
    result = await hass.config_entries.flow.async_init(
        DOMAIN, context={"source": config_entries.SOURCE_USER}
    )
    assert "change_connection" in result["menu_options"]
    result = await hass.config_entries.flow.async_configure(
        result["flow_id"], {"next_step_id": "change_connection"}
    )
    assert result["step_id"] == "change_connection"
    selector_config = (
        result["data_schema"].schema[next(iter(result["data_schema"].schema))].config
    )
    assert selector_config["options"] == [
        {"value": car.entry_id, "label": "My existing car"}
    ]
    result = await hass.config_entries.flow.async_configure(
        result["flow_id"], {"existing_entry_id": car.entry_id}
    )
    assert result["step_id"] == "reconfigure"
    result = await hass.config_entries.flow.async_configure(
        result["flow_id"], {"next_step_id": "companion"}
    )
    assert result["type"] is FlowResultType.FORM
    assert result["step_id"] == "companion"
    assert {key.schema for key in result["data_schema"].schema} == {
        CONF_COMPANION_CREDENTIAL
    }
    assert len(hass.config_entries.async_entries(DOMAIN)) == 1
    assert car.data == before
    assert car.disabled_by is ConfigEntryDisabler.USER
    if not finish:
        await hass.config_entries.flow.async_abort(result["flow_id"])
        assert car.data == before
        assert car.disabled_by is ConfigEntryDisabler.USER
        return

    async def switch_source(hass_arg, selected, changes):
        assert selected is car and hass_arg is hass
        assert selected.disabled_by is ConfigEntryDisabler.USER
        hass.config_entries.async_update_entry(car, data={**car.data, **changes})

    with (
        patch.object(
            NioConfigFlow,
            "_companion_candidate",
            new_callable=AsyncMock,
            return_value=SimpleNamespace(snapshot=snapshot()),
        ),
        patch(
            "custom_components.nio_telematics.config_flow.async_switch_source",
            new_callable=AsyncMock,
            side_effect=switch_source,
        ) as switch,
    ):
        result = await hass.config_entries.flow.async_configure(
            result["flow_id"], {CONF_COMPANION_CREDENTIAL: TOKEN}
        )
        assert result["step_id"] == "confirm_source"
        assert car.data == before
        result = await hass.config_entries.flow.async_configure(result["flow_id"], {})
        assert result["type"] is FlowResultType.ABORT
        assert result["reason"] == "reconfigure_successful"
        switch.assert_awaited_once()
    assert hass.config_entries.async_get_entry(car.entry_id) is car
    assert len(hass.config_entries.async_entries(DOMAIN)) == 1
    assert car.unique_id == VIN
    assert car.data[CONF_CONNECTION_METHOD] == "companion"
    assert car.data["token"] == before["token"]


async def test_existing_vehicle_choice_rejects_wrong_or_removed_entry(hass):
    car = entry()
    car.add_to_hass(hass)
    handler = NioConfigFlow()
    handler.hass = hass
    handler.context = {"source": config_entries.SOURCE_USER}
    result = await handler.async_step_change_connection(
        {"existing_entry_id": "unrelated"}
    )
    assert result["errors"] == {"base": "existing_vehicle_missing"}
    assert handler.context["source"] == config_entries.SOURCE_USER


async def test_selected_entry_is_resolved_again_and_removed_target_aborts(hass):
    car = entry()
    car.add_to_hass(hass)
    handler = NioConfigFlow()
    handler.hass = hass
    handler.context = {
        "source": config_entries.SOURCE_RECONFIGURE,
        "entry_id": car.entry_id,
    }
    with (
        patch.object(handler, "_get_reconfigure_entry", return_value=car),
        patch.object(hass.config_entries, "async_get_entry", return_value=None),
        patch(
            "custom_components.nio_telematics.config_flow.CompanionVehicleClient"
        ) as client,
    ):
        with pytest.raises(AbortFlow, match="existing_vehicle_missing"):
            await handler._companion_candidate({CONF_COMPANION_CREDENTIAL: TOKEN})
        client.assert_not_called()


async def test_commit_rechecks_current_vehicle_identity_after_network_preflight(hass):
    car = entry()
    car.add_to_hass(hass)
    handler = NioConfigFlow()
    handler.hass = hass
    handler.context = {
        "source": config_entries.SOURCE_RECONFIGURE,
        "entry_id": car.entry_id,
    }
    handler._companion_input = {CONF_COMPANION_CREDENTIAL: TOKEN}

    async def candidate(_):
        hass.config_entries.async_update_entry(car, data={**car.data, "vin": "B" * 17})
        return SimpleNamespace(snapshot=snapshot())

    with (
        patch.object(
            handler,
            "_companion_candidate",
            new_callable=AsyncMock,
            side_effect=candidate,
        ),
        patch(
            "custom_components.nio_telematics.config_flow.async_switch_source",
            new_callable=AsyncMock,
        ) as switch,
    ):
        result = await handler.async_step_confirm_source({})
        assert result["errors"]["base"] == "identity_mismatch"
        switch.assert_not_awaited()


@pytest.mark.parametrize("fail", [True, False])
async def test_paused_entry_starts_only_companion_and_rolls_back_to_paused(fail):
    original = {"vin": VIN, "token": {"access_token": "direct-fixture"}}
    car = SimpleNamespace(
        entry_id="paused-car",
        data=deepcopy(original),
        state=ConfigEntryState.NOT_LOADED,
        disabled_by=ConfigEntryDisabler.USER,
    )
    starts = []

    async def unload(_):
        car.state = ConfigEntryState.NOT_LOADED
        return True

    async def set_disabled(_, value):
        car.disabled_by = value
        if value is None:
            starts.append(car.data[CONF_CONNECTION_METHOD])
            car.state = (
                ConfigEntryState.SETUP_RETRY if fail else ConfigEntryState.LOADED
            )
            return not fail
        await unload(car.entry_id)
        return True

    manager = SimpleNamespace(
        async_unload=unload,
        async_set_disabled_by=set_disabled,
        async_setup=AsyncMock(side_effect=AssertionError("Do not start Direct")),
        async_update_entry=lambda target, *, data: setattr(target, "data", data),
    )
    fake_hass = SimpleNamespace(data={}, config_entries=manager)
    change = {CONF_CONNECTION_METHOD: "companion", CONF_COMPANION_CREDENTIAL: TOKEN}
    if fail:
        with pytest.raises(SourceSwitchError, match="source_switch_failed"):
            await async_switch_source(fake_hass, car, change)
        assert car.data == original
        assert car.disabled_by is ConfigEntryDisabler.USER
        assert car.state is ConfigEntryState.NOT_LOADED
    else:
        await async_switch_source(fake_hass, car, change)
        assert car.disabled_by is None
        assert car.state is ConfigEntryState.LOADED
        assert car.data["token"] == original["token"]
    assert starts == ["companion"]
    manager.async_setup.assert_not_awaited()


async def test_confirm_rechecks_coverage_before_switch_and_preserves_entry(hass):
    handler = NioConfigFlow()
    handler.hass = hass
    handler.context = {"source": "reconfigure"}
    handler._companion_input = {CONF_COMPANION_CREDENTIAL: TOKEN}
    car = entry()
    car.add_to_hass(hass)
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


async def test_failed_candidate_cleanup_still_restores_saved_configuration():
    original = {"vin": VIN, "token": {"access_token": "fixture"}}
    car = SimpleNamespace(
        entry_id="car",
        data=deepcopy(original),
        state=ConfigEntryState.LOADED,
    )
    manager = SimpleNamespace(
        async_unload=AsyncMock(side_effect=[True, RuntimeError("private failure")]),
        async_setup=AsyncMock(return_value=False),
    )
    manager.async_update_entry = lambda target, *, data: setattr(target, "data", data)
    fake_hass = SimpleNamespace(data={}, config_entries=manager)
    with pytest.raises(SourceSwitchError, match="source_rollback_failed"):
        await async_switch_source(fake_hass, car, {CONF_CONNECTION_METHOD: "companion"})
    assert car.data == original
    assert manager.async_setup.await_count == 1


async def test_flow_and_setup_survive_shared_owner_admission(
    hass,
):
    payload = _snapshot()
    payload["fields"]["rangeKm"] = _field(269, "km", "soc_status")
    payload["fields"]["odometerKm"] = _field(6428, "km", "vehicle_status")

    class AdmissionSession(_Session):
        ready = True

        def get(self, url, **kwargs):
            if self.ready:
                self.response = _Response(200, payload)
                self.ready = False
            else:
                self.response = _Response(429, {"error": "rate_limited"})
                self.response.headers["Retry-After"] = "1"
            return super().get(url, **kwargs)

    session = AdmissionSession(200, payload)
    car = entry()
    car.add_to_hass(hass)
    hass.config_entries.async_update_entry(
        car,
        data={
            "vin": VIN,
            "token": {"access_token": "direct-fixture"},
        },
    )
    car._async_set_state(hass, ConfigEntryState.LOADED, None)
    handler = NioConfigFlow()
    handler.hass = hass
    handler.context = {"source": "reconfigure"}

    async def unload(_):
        car._async_set_state(hass, ConfigEntryState.NOT_LOADED, None)
        return True

    async def setup(_):
        car._async_set_state(hass, ConfigEntryState.SETUP_IN_PROGRESS, None)
        assert await async_setup_entry(hass, car)
        car._async_set_state(hass, ConfigEntryState.LOADED, None)
        return True

    with (
        patch.object(handler, "_get_reconfigure_entry", return_value=car),
        patch(
            "custom_components.nio_telematics.config_flow.async_get_clientsession",
            return_value=session,
        ),
        patch(
            "custom_components.nio_telematics.async_get_clientsession",
            return_value=session,
        ),
        patch(
            "custom_components.nio_telematics._async_dashboard_options_updated",
            new_callable=AsyncMock,
        ),
        patch.object(
            hass.config_entries, "async_forward_entry_setups", new_callable=AsyncMock
        ),
        patch.object(hass.config_entries, "async_unload", side_effect=unload),
        patch.object(hass.config_entries, "async_setup", side_effect=setup),
        patch(
            "custom_components.nio_telematics.companion_transport.asyncio.sleep",
            new_callable=AsyncMock,
        ) as sleep,
    ):
        sleep.side_effect = lambda _: setattr(session, "ready", True)
        confirm = await handler.async_step_companion({CONF_COMPANION_CREDENTIAL: TOKEN})
        assert confirm["step_id"] == "confirm_source"
        result = await handler.async_step_confirm_source({})
        assert result["reason"] == "reconfigure_successful"
        assert car.runtime_data.data.soc_status.soc == 48.5
        assert car.data["token"]["access_token"] == "direct-fixture"
        assert sleep.await_count == 2
        assert all(call.args == (1,) for call in sleep.await_args_list)
        assert len(session.calls) == 5  # Three cache reads, two bounded 429 retries.
        await car.runtime_data.async_shutdown()


@pytest.mark.parametrize("fresh", [True, False])
async def test_ledger_switch_creates_one_baseline_and_preserves_archive(
    hass, freezer, fresh
):
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
            "fresh": fresh,
        },
    )
    hass.states.async_set(
        "sensor.test_odo",
        "6428",
        {
            "source_sample": "2026-10-20T18:59:05Z",
            "fresh": fresh,
        },
    )
    original_samples = deepcopy(coordinator.ledger.data["samples"])
    original_last = deepcopy(coordinator.ledger.data["last"])
    await coordinator.sample()
    if not fresh:
        # A backend-stale reading inside the legacy 900s age window still
        # cannot establish a baseline or add history/energy evidence.
        assert "telemetry_source" not in coordinator.ledger.data
        assert coordinator.ledger.data["samples"] == original_samples
        assert coordinator.ledger.data["last"] == original_last
        assert not coordinator.ledger.data.get("native_soc_reports")
        assert coordinator.ledger.data["charges"] == archived
        return
    assert coordinator.ledger.data["telemetry_source"] == "companion:2"
    assert coordinator.ledger.data["parked_losses"] == []
    assert coordinator.ledger.data["charges"] == archived
    transitions = deepcopy(coordinator.ledger.data["source_transitions"])
    await coordinator.sample()
    assert coordinator.ledger.data["source_transitions"] == transitions
    assert coordinator.ledger.data["charges"] == archived
