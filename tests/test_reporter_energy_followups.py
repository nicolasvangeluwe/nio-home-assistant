"""Same-input regressions for reported charging-boundary and joint-zero events."""

import asyncio
import importlib.util
import json
import pathlib
import sys
import types
import unittest
from copy import deepcopy
from datetime import UTC, datetime, timedelta
from types import SimpleNamespace
from unittest.mock import AsyncMock, Mock, patch

from homeassistant.helpers.update_coordinator import UpdateFailed

from custom_components.nio_telematics.api import NioApiError
from custom_components.nio_telematics.car_dashboard import websocket_update
from custom_components.nio_telematics.coordinator import NioDataUpdateCoordinator
from custom_components.nio_telematics.models import NioSocStatus, NioVehicleData
from custom_components.nio_telematics.sensor import (
    SENSORS,
    NioRangeSensor,
    NioSocSensor,
)

ROOT = pathlib.Path(__file__).parents[1] / "custom_components" / "nio_telematics"
package = types.ModuleType("reporter_ledger")
package.__path__ = [str(ROOT / "car_dashboard")]
sys.modules[package.__name__] = package
spec = importlib.util.spec_from_file_location(
    "reporter_ledger.ledger", ROOT / "car_dashboard" / "ledger.py"
)
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)
Ledger = module.Ledger


class ChargingBoundaryTests(unittest.TestCase):
    t = 1795590000

    def ledger(self):
        ledger = Ledger({"capacity_kwh": 90, "full_range_km": 557, "currency": "DKK"})
        ledger.preferences({"opening_price_eur_kwh": 0.3})
        return ledger

    def departure(self):
        ledger = self.ledger()
        ledger.import_home([[1, self.t - 3000, self.t + 5, 10, 0, 4, None, None]])
        for at, odo, soc in (
            (-3600, 1000, 50),
            (0, 1000, 60),
            (117, 1001, 58),
            (717, 1011, 57),
        ):
            ledger.ingest(self.t + at, odo, None, soc_pct=soc)
        return ledger

    def test_priced_overlap_keeps_missing_interval_and_known_book_price(self):
        ledger = self.departure()
        before = deepcopy(ledger.data)
        rows = ledger.cost_segments()
        self.assertEqual(rows[0]["invalid_reason"], "charging")
        self.assertIsNone(rows[0]["kwh"])
        self.assertIsNone(rows[0]["cost_eur"])
        self.assertAlmostEqual(rows[1]["kwh"], 0.9)
        self.assertAlmostEqual(rows[1]["cost_eur"], 0.9 * 17.5 / 55)
        self.assertEqual(
            ledger.statistics(0, self.t + 1000)["unaccounted_distance_km"], 1
        )
        self.assertEqual(ledger.data, before)

    def test_unknown_foreign_ongoing_or_future_charge_cannot_supply_book_price(self):
        for update in (
            {"cost_eur": None},
            {"currency": "EUR"},
            {"confirmed": False},
            {"ongoing": True},
            {"end": self.t + 200},
            {"kind": "candidate"},
        ):
            ledger = self.departure()
            ledger.data["charges"]["home-1"].update(update)
            if update.get("kind") == "candidate":
                ledger.data["charges"]["home-1"]["confirmed"] = False
            self.assertIsNone(ledger.cost_segments()[-1]["cost_eur"], update)
        ledger = self.departure()
        ledger.data["source_transitions"].append(
            {"t": self.t + 30, "energy": 53, "capacity_kwh": 90}
        )
        self.assertIsNone(ledger.cost_segments()[-1]["cost_eur"])

    def test_exact_legacy_charging_anchor_preserves_next_aligned_native_window(self):
        ledger = self.departure()
        raw = ledger.data["active"]["segments"][-1]
        raw["kwh"] = 2.7  # Value produced by dev.6's old pre-charging anchor.
        original = deepcopy(ledger.data)
        row = ledger.cost_segments()[-1]
        self.assertTrue(row["native_anchor_corrected"])
        self.assertAlmostEqual(row["kwh"], 0.9)
        self.assertAlmostEqual(row["cost_eur"], 0.9 * 17.5 / 55)
        self.assertEqual(ledger.data, original)
        ledger.data["active"]["native_alignment_version"] = 1
        self.assertIsNone(ledger.cost_segments()[-1]["kwh"])

    def test_delayed_arrival_odometer_keeps_unknown_km_and_guarded_later_price(self):
        start = datetime(2026, 11, 25, 16, 26, tzinfo=UTC).timestamp()
        for charge_end, can_price_later in (
            (start + 64 * 60, True),
            (start + 84 * 60, False),
        ):
            ledger = self.ledger()
            ledger.preferences({"opening_price_eur_kwh": 2})
            ledger.import_home([[1, start + 2 * 60, charge_end, 5, 0, 15, None, None]])
            # The car reports706 only at17:40 although the cable was connected
            # at16:28. Never turn the16:26–17:40 window into measured driving.
            for at, odo, soc, connected, changed_at in (
                (start - 10 * 60, 700, 61, False, start - 3600),
                (start, 705, 60, False, start - 3600),
                (start + 74 * 60, 706, 63, True, start + 2 * 60),
                # A separate stationary reading after the explicit17:45
                # disconnection establishes the next movement's baseline.
                (start + 80 * 60, 706, 63, False, start + 79 * 60),
                (start + 94 * 60, 716, 61, False, start + 79 * 60),
                (start + 104 * 60, 726, 60, False, start + 79 * 60),
            ):
                ledger.observe_native_sources(at, odo, at, soc, connected, changed_at)
            raw = deepcopy(ledger.data)
            rows = ledger.cost_segments()
            arrival = next(
                r for r in rows if r["start"] == start and r["end"] == start + 74 * 60
            )
            self.assertEqual(arrival["km"], 1)
            self.assertEqual(arrival["invalid_reason"], "charging")
            self.assertIsNone(arrival["kwh"])
            self.assertIsNone(arrival["cost_eur"])
            self.assertAlmostEqual(rows[-1]["kwh"], 0.9)
            if can_price_later:
                self.assertAlmostEqual(rows[-1]["cost_eur"], 0.9 * 123 / 59)
                stat = ledger.statistics(start - 600, start + 104 * 60)
                self.assertEqual(stat["distance_km"], 26)
                self.assertEqual(stat["consumption_distance_km"], 25)
                self.assertEqual(stat["unaccounted_distance_km"], 1)
            else:
                # At17:40 the imported charge has not completed/booked yet;
                # later completion must not backprice its unknown prefix.
                self.assertIsNone(rows[-1]["cost_eur"])
            self.assertEqual(ledger.data, raw)

    def test_dev6_manual_and_ignored_anchor_overlays_survive_upgrade_until_undo(self):
        for status in ("manual", "ignored"):
            ledger = self.ledger()
            ledger.data["opening"] = {"t": self.t, "energy": 54}
            ledger.data["trips"] = [
                {
                    "id": "legacy-trip",
                    "native_alignment_version": 2,
                    "segments": [
                        {
                            "start": self.t,
                            "end": self.t + 100,
                            "km": 1,
                            "kwh": None,
                            "complete": False,
                            "invalid_reason": "gap",
                            "start_energy": 54,
                            "end_energy": 52.2,
                        },
                        {
                            "start": self.t + 100,
                            "end": self.t + 200,
                            "km": 10,
                            "kwh": 2.7,
                            "complete": True,
                            "invalid_reason": None,
                            "start_energy": 52.2,
                            "end_energy": 51.3,
                        },
                    ],
                }
            ]
            # Captured from the real c8edf884/dev.6 Ledger for this raw archive.
            ident = "gap-934e34f931048800c35cf17f"
            fingerprint = (
                "2ffd3e8b118f1e30dc18762fbc7d3f77241a4669e2ccb7890dd021cf28fb0b49"
            )
            record = {"fingerprint": fingerprint, "status": status}
            if status == "manual":
                record.update(energy_kwh=4, cost=7, currency="DKK")
            ledger.data["gap_resolutions"][ident] = record
            original = deepcopy(ledger.data["trips"])
            interval = next(
                r for r in ledger.unaccounted_intervals() if r["id"] == ident
            )
            self.assertEqual(interval["resolution"], status)
            row = ledger.cost_segments()[-1]
            self.assertEqual(row["kwh"], 4 if status == "manual" else None)
            self.assertEqual(row["cost_eur"], 7 if status == "manual" else None)
            self.assertEqual(ledger.data["trips"], original)
            ledger.resolve_gap(ident, fingerprint, "open")
            self.assertAlmostEqual(ledger.cost_segments()[-1]["kwh"], 0.9)
            self.assertAlmostEqual(ledger.cost_segments()[-1]["cost_eur"], 0.27)
            self.assertEqual(ledger.data["trips"], original)


class MeasurementErrorTests(unittest.TestCase):
    t = ChargingBoundaryTests.t
    ledger = ChargingBoundaryTests.ledger

    def excursion(self, dismiss=False):
        ledger = self.ledger()
        # The older positive sample is14minutes before zero, as in the report.
        for at, soc in ((0, 60.5), (840, 0), (860, 60.5)):
            ledger.ingest(self.t + at, 1000, None, soc_pct=soc)
        if dismiss:
            ledger.dismiss_candidate(next(iter(ledger.data["charges"])))
        ledger.ingest(self.t + 1460, 1010, None, soc_pct=58.5)
        return ledger

    def test_explicit_exclusion_and_undo_preserve_raw_data_and_replay_value(self):
        for dismiss in (False, True):
            ledger = self.excursion(dismiss)
            original = deepcopy(ledger.data)
            self.assertAlmostEqual(ledger.parked_periods()[0]["kwh"], 54.45)
            self.assertIsNone(ledger.cost_segments()[-1]["cost_eur"])
            interval = ledger.measurement_error_intervals()[0]
            self.assertIsNotNone(interval["paired_candidate_id"])
            ledger.set_measurement_error(interval["id"], interval["fingerprint"], True)
            self.assertEqual(ledger.parked_periods(), [])
            self.assertAlmostEqual(ledger.cost_segments()[-1]["cost_eur"], 0.54)
            self.assertEqual(ledger.snapshot(self.t + 1500)["charges"], [])
            self.assertTrue(
                ledger.snapshot(self.t + 1500)["measurement_errors"][0][
                    "measurement_error"
                ]
            )
            for key in ("samples", "charges", "parked_losses", "trips", "opening"):
                self.assertEqual(ledger.data[key], original[key])
            restored = Ledger(ledger.settings, json.loads(json.dumps(ledger.data)))
            self.assertAlmostEqual(restored.cost_segments()[-1]["cost_eur"], 0.54)
            ledger.set_measurement_error(interval["id"], interval["fingerprint"], False)
            self.assertAlmostEqual(ledger.parked_periods()[0]["kwh"], 54.45)
            self.assertIsNone(ledger.cost_segments()[-1]["cost_eur"])

    def test_confirmed_receipt_is_never_implicitly_removed(self):
        ledger = self.excursion()
        interval = ledger.measurement_error_intervals()[0]
        ledger.set_measurement_error(interval["id"], interval["fingerprint"], True)
        candidate_id = interval["paired_candidate_id"]
        ledger.edit_charge(candidate_id, receipt=40)
        self.assertEqual(ledger.accounting_charges()[0]["id"], candidate_id)
        self.assertFalse(
            ledger.measurement_error_intervals()[0]["paired_candidate_excluded"]
        )
        self.assertEqual(ledger.snapshot(self.t + 1500)["charges"][0]["cost_eur"], 40)

    def test_unpaired_candidate_and_genuine_zero_remain_raw_without_user_choice(self):
        ledger = self.excursion()
        candidate = next(iter(ledger.data["charges"].values()))
        candidate["estimated_kwh"] -= 1
        interval = ledger.measurement_error_intervals()[0]
        self.assertIsNone(interval["paired_candidate_id"])
        ledger.set_measurement_error(interval["id"], interval["fingerprint"], True)
        self.assertEqual(len(ledger.accounting_charges()), 1)
        untouched = self.ledger()
        untouched.ingest(self.t, 1000, None, soc_pct=1)
        untouched.ingest(self.t + 60, 1000, None, soc_pct=0)
        self.assertAlmostEqual(untouched.parked_periods()[0]["kwh"], 0.9)
        self.assertEqual(untouched.data["measurement_errors"], {})

    def test_raw_group_identity_staleness_and_orphan_undo(self):
        ledger = self.excursion()
        ledger.data["parked_losses"].insert(
            0,
            {
                "start": self.t - 60,
                "end": self.t,
                "kwh": 1,
                "end_energy": 54.45,
                "complete": True,
            },
        )
        self.assertEqual(len(ledger.parked_periods()), 1)
        self.assertEqual(len(ledger.parked_periods()[0]["intervals"]), 2)
        interval = ledger.measurement_error_intervals()[-1]
        ledger.set_measurement_error(interval["id"], interval["fingerprint"], True)
        self.assertEqual(ledger.parked_periods()[0]["kwh"], 1)
        ledger.data["parked_losses"][-1]["kwh"] = 54
        stale = ledger.measurement_error_intervals()[-1]
        self.assertEqual(stale["state"], "stale")
        self.assertFalse(stale["measurement_error"])
        ledger.set_measurement_error(stale["id"], stale["fingerprint"], False)
        ledger.set_measurement_error(stale["id"], stale["fingerprint"], True)
        ledger.data["parked_losses"].pop()
        ledger.set_measurement_error(stale["id"], stale["fingerprint"], False)
        self.assertEqual(ledger.data["measurement_errors"], {})

    def test_measurement_action_uses_existing_admin_schema_and_atomic_store(self):
        message = {
            "id": 1,
            "type": "nio_telematics/car_dashboard/update",
            "entry_id": "test",
            "action": "set_measurement_error",
            "values": {},
        }
        self.assertEqual(
            websocket_update._ws_schema(message)["action"],
            "set_measurement_error",
        )
        spec = importlib.util.spec_from_file_location(
            "reporter_ledger.coordinator", ROOT / "car_dashboard" / "coordinator.py"
        )
        adapter = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(adapter)
        owner = adapter.CarLedgerCoordinator.__new__(adapter.CarLedgerCoordinator)
        owner.ledger = self.excursion()
        owner.hass = SimpleNamespace(
            config=SimpleNamespace(currency="DKK", time_zone="UTC"),
            states=SimpleNamespace(get=lambda _: None),
        )
        owner.settings = {"home_history": "", "home_connected": ""}
        owner.active_home_id = None
        owner.source_status = "fresh"
        owner.cost_recorder = SimpleNamespace(enrich=lambda data: data)
        owner.store = SimpleNamespace(async_save=AsyncMock())
        owner.lock = asyncio.Lock()
        owner.async_set_updated_data = Mock()
        interval = owner.ledger.measurement_error_intervals()[0]
        values = {
            "ident": interval["id"],
            "fingerprint": interval["fingerprint"],
            "excluded": True,
        }
        result = asyncio.run(owner.mutate("set_measurement_error", values))
        self.assertEqual(result["parked_periods"], [])
        self.assertEqual(
            len(owner.store.async_save.call_args.args[0]["measurement_errors"]), 1
        )
        before = deepcopy(owner.ledger.data)
        owner.store.async_save.side_effect = RuntimeError("save failed")
        with self.assertRaises(RuntimeError):
            asyncio.run(
                owner.mutate("set_measurement_error", {**values, "excluded": False})
            )
        self.assertEqual(owner.ledger.data, before)


class DirectJointZeroTests(unittest.TestCase):
    clock = datetime(2026, 11, 25, 16, 10, tzinfo=UTC)

    def coordinator(self, soc=60.5, remaining_range=313):
        owner = NioDataUpdateCoordinator.__new__(NioDataUpdateCoordinator)
        owner._vin = "TEST"
        owner.config_entry = SimpleNamespace(data={"vin": "TEST"}, title="Test car")
        owner._telemetry = {}
        owner._request_count = 0
        owner._background_index = 0
        owner._polling_refresh_count = 0
        owner._polling_auth_failed = False
        owner._polling_transport_recovering = False
        owner._joint_zero_pending = None
        owner._rejected_zero_at = {}
        owner._client = SimpleNamespace(
            async_get_change_record=AsyncMock(),
            async_get_latest_vehicle_record=AsyncMock(return_value={}),
        )
        owner.data = NioVehicleData(
            "TEST",
            NioSocStatus(
                soc,
                remaining_range,
                None,
                None,
                None,
                None,
                self.clock - timedelta(minutes=14),
            ),
            self.clock,
            {},
            {},
            soc_last_valid_at=self.clock - timedelta(minutes=14),
            remaining_range_last_valid_at=self.clock - timedelta(minutes=14),
        )
        return owner

    def read(self, owner, soc, distance, at=0, elapsed=0):
        record = {
            "soc": soc,
            "remaining_range": distance,
            "sample_timestamp": (self.clock + timedelta(seconds=at)).timestamp() * 1000,
        }
        owner._request_count = 0
        owner._client.async_get_change_record.return_value = record
        with patch(
            "custom_components.nio_telematics.coordinator.time.monotonic",
            return_value=elapsed,
        ):
            owner.data = asyncio.run(owner._async_update_data())
        return owner.data

    def test_reported_joint_zero_rebound_does_not_publish_false_energy(self):
        owner = self.coordinator()
        old_soc_clock = owner.data.soc_last_valid_at
        pending = self.read(owner, 0, 0)
        self.assertEqual(pending.soc_status.soc, 60.5)
        self.assertEqual(pending.soc_status.remaining_range, 313)
        self.assertEqual(pending.soc_last_valid_at, old_soc_clock)
        self.assertTrue(pending.soc_retained)
        rebound = self.read(owner, 60.5, 313, at=20, elapsed=20)
        self.assertIsNone(owner._joint_zero_pending)
        self.assertEqual(rebound.soc_status.soc, 60.5)
        self.read(owner, 0, 0, at=50, elapsed=50)
        self.assertEqual(owner.data.soc_status.soc, 60.5)
        self.read(owner, 60.5, 313, at=75, elapsed=75)
        self.assertEqual(owner.data.soc_status.soc, 60.5)

    def test_zero_needs_later_successful_energy_read_not_cached_time_or_errors(self):
        owner = self.coordinator()
        self.read(owner, 0, 0)
        owner._request_count = 3  # Successful background snapshot is not confirmation.
        with patch(
            "custom_components.nio_telematics.coordinator.time.monotonic",
            return_value=80,
        ):
            owner.data = asyncio.run(owner._async_update_data())
        self.assertEqual(owner.data.soc_status.soc, 60.5)
        owner._request_count = 0
        owner._client.async_get_change_record.side_effect = NioApiError(
            "temporary failure"
        )
        with patch(
            "custom_components.nio_telematics.coordinator.time.monotonic",
            return_value=100,
        ):
            with self.assertRaises(UpdateFailed):
                asyncio.run(owner._async_update_data())
        self.assertEqual(owner.data.soc_status.soc, 60.5)
        owner._client.async_get_change_record.side_effect = None
        cached = self.read(owner, 0, 0, at=0, elapsed=120)
        self.assertEqual(cached.soc_status.soc, 60.5)
        self.assertIsNotNone(owner._joint_zero_pending)
        accepted = self.read(owner, 0, 0, at=130, elapsed=130)
        self.assertEqual(accepted.soc_status.soc, 0)
        self.assertEqual(accepted.soc_status.remaining_range, 0)
        self.assertEqual(
            accepted.soc_last_valid_at, self.clock + timedelta(seconds=130)
        )
        self.assertEqual(
            accepted.remaining_range_last_valid_at, self.clock + timedelta(seconds=130)
        )
        self.assertIsNone(owner._joint_zero_pending)

    def test_one_advancing_zero_field_cannot_confirm_the_joint_pair(self):
        owner = self.coordinator()
        self.read(owner, 0, 0)
        for soc_at, range_at, observed_at in ((120, 0, 120), (120, 121, 130)):
            owner._request_count = 0
            owner._client.async_get_change_record.return_value = {
                "soc": 0,
                "remaining_range": 0,
                "sample_timestamp": (
                    self.clock + timedelta(seconds=max(soc_at, range_at))
                ).timestamp()
                * 1000,
                "_field_timestamps": {
                    "soc": (self.clock + timedelta(seconds=soc_at)).timestamp() * 1000,
                    "remaining_range": (
                        self.clock + timedelta(seconds=range_at)
                    ).timestamp()
                    * 1000,
                },
            }
            with patch(
                "custom_components.nio_telematics.coordinator.time.monotonic",
                return_value=observed_at,
            ):
                owner.data = asyncio.run(owner._async_update_data())
            self.assertEqual(owner.data.soc_status.soc, 60.5)
            self.assertIsNotNone(owner._joint_zero_pending)
        accepted = self.read(owner, 0, 0, at=140, elapsed=140)
        self.assertEqual(accepted.soc_status.soc, 0)
        self.assertEqual(
            accepted.soc_last_valid_at, self.clock + timedelta(seconds=140)
        )

    def test_initial_low_soc_zero_and_single_field_zero_remain_valid(self):
        for soc in (None, 1, 0.5):
            owner = self.coordinator(soc=soc, remaining_range=3)
            self.assertEqual(self.read(owner, 0, 0).soc_status.soc, 0)
            self.assertIsNone(owner._joint_zero_pending)
        owner = self.coordinator()
        self.assertEqual(self.read(owner, 60.5, 0).soc_status.remaining_range, 0)

    def test_pending_marks_retained_sensors_unfresh_and_sparse_read_cannot_confirm(
        self,
    ):
        owner = self.coordinator()
        self.read(owner, 0, 0)
        for cls, key in (
            (NioSocSensor, "battery_state_of_charge"),
            (NioRangeSensor, "remaining_range"),
        ):
            sensor = cls(owner, next(d for d in SENSORS if d.key == key))
            self.assertFalse(sensor.extra_state_attributes["fresh"])
            self.assertTrue(sensor.extra_state_attributes["pending_zero"])
            self.assertTrue(sensor.extra_state_attributes["data_retained"])
        owner._request_count = 0
        owner._client.async_get_change_record.return_value = {
            "max_soc": 80,
            "sample_timestamp": (self.clock + timedelta(seconds=90)).timestamp() * 1000,
        }
        with patch(
            "custom_components.nio_telematics.coordinator.time.monotonic",
            return_value=90,
        ):
            owner.data = asyncio.run(owner._async_update_data())
        self.assertEqual(owner.data.soc_status.soc, 60.5)
        self.assertIsNotNone(owner._joint_zero_pending)


class SnapshotWarningIntegrationTests(unittest.TestCase):
    def test_source_metadata_clears_warning_without_changing_saved_amounts(self):
        spec = importlib.util.spec_from_file_location(
            "reporter_ledger.coordinator", ROOT / "car_dashboard" / "coordinator.py"
        )
        adapter = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(adapter)
        owner = adapter.CarLedgerCoordinator.__new__(adapter.CarLedgerCoordinator)
        ledger = Ledger({"capacity_kwh": 90, "full_range_km": 557, "currency": "DKK"})
        ledger.import_home([[1, 100, 200, 10, 0, 2, None, None]], currency="EUR")
        history = SimpleNamespace(
            attributes={"friendly_name": "Charging sessions", "sessions": []}
        )
        owner.ledger = ledger
        owner.hass = SimpleNamespace(
            config=SimpleNamespace(currency="DKK", time_zone="UTC"),
            states=SimpleNamespace(
                get=lambda ident: history if ident == "sensor.history" else None
            ),
        )
        owner.settings = {"home_history": "sensor.history", "home_connected": ""}
        owner.active_home_id = None
        owner.source_status = "fresh"
        owner.cost_recorder = SimpleNamespace(enrich=lambda data: data)
        owner.store = SimpleNamespace(async_save=AsyncMock())
        owner.lock = asyncio.Lock()
        owner.async_set_updated_data = Mock()
        original = deepcopy(ledger.data["charges"])
        self.assertEqual(
            owner.snapshot()["history_currency_warning"]["source"], "Charging sessions"
        )
        history.attributes["currency"] = "DKK"
        self.assertIsNone(owner.snapshot()["history_currency_warning"])
        self.assertEqual(ledger.data["charges"], original)
        owner.settings["home_history"] = ""
        self.assertIsNone(owner.snapshot()["history_currency_warning"])


if __name__ == "__main__":
    unittest.main()
