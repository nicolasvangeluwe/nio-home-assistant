"""Exercise durable proof migration through the actual HA Store API."""

from copy import deepcopy
from unittest.mock import AsyncMock, patch

import pytest
from homeassistant.helpers.storage import Store

from custom_components.nio_telematics.car_dashboard import coordinator
from custom_components.nio_telematics.car_dashboard.ledger import Ledger
from custom_components.nio_telematics.dashboard_backup import validate_history


def legacy_history():
    ledger = Ledger({"capacity_kwh": 90, "full_range_km": 557, "currency": "DKK"})
    ledger.preferences({"opening_price_eur_kwh": 2})
    t = 1795500000
    ledger.import_home([[1, t + 100, t + 1000, 10, 0, 40, None, None]])
    for at, odo, energy in (
        (0, 700, 50),
        (100, 700, 50),
        (200, 700, 49.55),
        (1000, 700, 59.55),
        (1200, 700, 59.55),
        (1800, 710, 57.75),
    ):
        ledger.observe_native_sources(
            t + at, odo, t + at, energy / 90 * 100, False, None
        )
    data = deepcopy(ledger.data)
    data.pop("native_cost_anchors")
    for sample in data["samples"]:
        sample.pop("native_source_time", None)
    return ledger.settings, data


async def test_migration_saves_before_any_new_sample_and_survives_store_recreate(hass):
    settings, original = legacy_history()
    key = "nio_native_cost_lifecycle_test"
    store = Store(hass, 1, key, atomic_writes=True)
    await store.async_save(deepcopy(original))
    owner = coordinator.CarLedgerCoordinator.__new__(coordinator.CarLedgerCoordinator)
    owner.hass, owner.settings, owner.store = hass, settings, store
    owner.unsub = []
    owner.sample = AsyncMock()  # Unchanged/unavailable sources add no new revision.
    with (
        patch.object(
            coordinator, "async_track_state_change_event", return_value=lambda: None
        ),
        patch.object(
            coordinator, "async_track_time_interval", return_value=lambda: None
        ),
    ):
        await owner.async_start()
    persisted = await Store(hass, 1, key, atomic_writes=True).async_load()
    assert persisted["native_cost_anchors"]
    assert persisted["revision"] > original["revision"]
    for collection in (
        "trips",
        "active",
        "charges",
        "samples",
        "parked_losses",
        "preferences",
        "measurement_errors",
    ):
        assert persisted[collection] == original[collection]
    validate_history(persisted)
    persisted["samples"], persisted["native_soc_reports"] = [], []
    await store.async_save(persisted)
    recreated = Ledger(
        settings, await Store(hass, 1, key, atomic_writes=True).async_load()
    )
    assert recreated.cost_segments()[-1]["cost_eur"] == pytest.approx(4.2)
    assert recreated.data["charges"] == original["charges"]


@pytest.mark.parametrize(
    "bad",
    [
        {"source_until": 1795502000},
        {"energy": True},
        {"capacity_kwh": -1},
        {"epoch": 9999999999},
        {"home_connected": "on"},
        {"odo": float("nan")},
        {"unexpected": 1},
    ],
)
def test_backup_rejects_invalid_permanent_observations(bad):
    settings, data = legacy_history()
    migrated = Ledger(settings, data).data
    migrated["native_cost_anchors"][0].update(bad)
    with pytest.raises(ValueError):
        validate_history(migrated)
