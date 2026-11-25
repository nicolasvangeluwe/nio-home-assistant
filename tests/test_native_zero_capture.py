"""Actual dashboard capture/save/recreate regressions for initial joint zero."""

import asyncio
import json
import unittest
from copy import deepcopy
from datetime import UTC, datetime, timedelta
from types import SimpleNamespace
from unittest.mock import AsyncMock, Mock, patch

from custom_components.nio_telematics.car_dashboard.coordinator import (
    CarLedgerCoordinator,
)
from custom_components.nio_telematics.car_dashboard.ledger import Ledger
from custom_components.nio_telematics.dashboard_backup import validate_history


class NativeZeroCaptureTests(unittest.TestCase):
    clock = datetime(2026, 11, 25, 16, 10, tzinfo=UTC)

    def setup_owner(self, source="direct", data=None, baseline=60.5):
        settings = {
            "capacity_kwh": 90,
            "full_range_km": 557,
            "currency": "EUR",
            "soc": "sensor.soc",
            "range": "sensor.range",
            "odometer": "sensor.odo",
            "home_history": "",
            "home_connected": "",
        }
        if data is None:
            ledger = Ledger(settings)
            ledger.preferences({"opening_price_eur_kwh": 2})
            if baseline is not None:
                ledger.ingest(
                    self.clock.timestamp() - 3600, 1000, None, soc_pct=baseline
                )
            ledger.data["telemetry_source"] = source
            data = ledger.data
        owner = CarLedgerCoordinator.__new__(CarLedgerCoordinator)
        owner.settings = settings
        owner.lock = asyncio.Lock()
        owner.active_home_id = None
        owner.unsub = []
        owner.pending = None
        owner.source_status = "waiting_for_fresh_sample"
        owner.async_set_updated_data = Mock()
        owner.states = {}
        owner.hass = SimpleNamespace(
            config=SimpleNamespace(currency="EUR", time_zone="UTC"),
            states=SimpleNamespace(get=owner.states.get),
        )
        owner.cost_recorder = SimpleNamespace(
            refresh=AsyncMock(), enrich=lambda snapshot: snapshot
        )
        owner.saved = deepcopy(data)

        async def save(value):
            owner.saved = deepcopy(value)

        owner.store = SimpleNamespace(
            async_load=AsyncMock(side_effect=lambda: deepcopy(owner.saved)),
            async_save=AsyncMock(side_effect=save),
        )
        with (
            patch(
                "custom_components.nio_telematics.car_dashboard.coordinator.async_track_state_change_event",
                return_value=lambda: None,
            ),
            patch(
                "custom_components.nio_telematics.car_dashboard.coordinator.async_track_time_interval",
                return_value=lambda: None,
            ),
            patch(
                "custom_components.nio_telematics.car_dashboard.coordinator.dt_util.utcnow",
                return_value=self.clock,
            ),
        ):
            asyncio.run(owner.async_start())
        return owner

    def capture(
        self,
        owner,
        at,
        soc,
        distance,
        odo=1000,
        *,
        source=None,
        clocks=None,
        retained=False,
        quality="valid",
        range_clock=None,
    ):
        now = self.clock + timedelta(seconds=at)
        stamp = self.clock + timedelta(seconds=at if clocks is None else clocks)
        source = source or owner.ledger.data.get("telemetry_source", "direct")
        attrs = {
            "telemetry_source": source.split(":")[0],
            "last_valid_sample": stamp.isoformat(),
            "data_retained": retained,
        }
        if source.startswith("companion:"):
            attrs.update(
                source_generation=int(source.split(":")[1]),
                source_quality=quality,
                fresh=quality == "valid",
            )
        owner.states["sensor.soc"] = SimpleNamespace(
            state=str(soc),
            attributes={**attrs, "source_endpoint": "soc_status"},
            last_changed=stamp,
            last_updated=stamp,
        )
        # Actual NioRangeSensor does not emit a source_endpoint attribute.
        owner.states["sensor.range"] = SimpleNamespace(
            state=str(distance),
            attributes={
                **attrs,
                "last_valid_sample": (
                    self.clock + timedelta(seconds=range_clock)
                ).isoformat(),
            }
            if range_clock is not None
            else dict(attrs),
            last_changed=stamp,
            last_updated=stamp,
        )
        owner.states["sensor.odo"] = SimpleNamespace(
            state=str(odo),
            attributes={"source_sample": now.isoformat(), "fresh": True},
            last_changed=now,
            last_updated=now,
        )
        with patch(
            "custom_components.nio_telematics.car_dashboard.coordinator.dt_util.utcnow",
            return_value=now,
        ):
            asyncio.run(owner.sample())

    def snapshot(self, owner, at):
        with patch(
            "custom_components.nio_telematics.car_dashboard.coordinator.dt_util.utcnow",
            return_value=self.clock + timedelta(seconds=at),
        ):
            return owner.snapshot()

    def test_restart_recovery_never_records_zero_loss_or_refill(self):
        for source in ("direct", "companion:3"):
            with self.subTest(source=source):
                owner = self.setup_owner(source)
                self.capture(owner, 0, 0, 0)
                self.assertEqual(owner.ledger.data["last"]["soc"], 60.5)
                self.assertEqual(
                    owner.saved["native_zero_capture"]["started"],
                    self.clock.timestamp(),
                )
                owner = self.setup_owner(
                    source, validate_history(json.loads(json.dumps(owner.saved)))
                )
                self.capture(owner, 15, 60.5, 313)
                self.assertNotIn("native_zero_capture", owner.ledger.data)
                self.capture(owner, 600, 59.5, 308, 1001)
                self.assertEqual(owner.ledger.data["parked_losses"], [])
                self.assertEqual(owner.ledger.data["charges"], {})
                self.assertAlmostEqual(owner.ledger.cost_segments()[-1]["kwh"], 0.9)
                self.assertAlmostEqual(
                    owner.ledger.cost_segments()[-1]["cost_eur"], 1.8
                )

    def test_withheld_movement_readonly_then_durable_unknown_once(self):
        owner = self.setup_owner()
        self.capture(owner, 0, 0, 0, 1001)
        pending = self.snapshot(owner, 1)
        self.assertEqual(pending["pending_native_capture"]["distance_km"], 1)
        self.assertTrue(pending["pending_native_capture"]["read_only"])
        self.assertEqual(pending["unaccounted_intervals"], [])
        self.assertEqual(pending["statistics"]["day"]["unaccounted_distance_km"], 1)
        self.assertEqual(pending["statistics"]["day"]["distance_km"], 1)
        self.assertTrue(all("gap_id" not in r for r in pending["driving_segments"]))
        owner = self.setup_owner(data=validate_history(owner.saved))
        self.capture(owner, 15, 60.5, 313, 1002)
        resolved = self.snapshot(owner, 16)
        self.assertIsNone(resolved["pending_native_capture"])
        self.assertEqual(resolved["statistics"]["day"]["distance_km"], 2)
        self.assertEqual(resolved["statistics"]["day"]["unaccounted_distance_km"], 2)
        self.assertEqual(len(resolved["unaccounted_intervals"]), 1)
        self.assertIsNone(resolved["driving_segments"][0]["kwh"])
        self.capture(owner, 600, 59.5, 308, 1003)
        self.assertAlmostEqual(owner.ledger.cost_segments()[-1]["cost_eur"], 1.8)
        self.assertEqual(
            self.snapshot(owner, 601)["statistics"]["day"]["distance_km"], 3
        )

    def test_persistent_zero_requires_advancing_authoritative_clocks_after60(self):
        for source in ("direct", "companion:3"):
            with self.subTest(source=source):
                owner = self.setup_owner(source)
                self.capture(owner, 0, 0, 0, 1001)
                self.capture(owner, 120, 0, 0, 1001, clocks=0, retained=True)
                self.assertIn("native_zero_capture", owner.ledger.data)
                self.capture(owner, 121, 0, 0, 1001, clocks=121, retained=True)
                self.assertIn("native_zero_capture", owner.ledger.data)
                self.capture(owner, 122, 0, 0, 1001, clocks=122)
                self.assertNotIn("native_zero_capture", owner.ledger.data)
                self.assertEqual(owner.ledger.data["last"]["soc"], 0)
                row = owner.ledger.cost_segments()[0]
                self.assertIsNone(row["kwh"])
                self.assertEqual(row["invalid_reason"], "gap")
                self.assertEqual(owner.ledger.data["parked_losses"], [])

    def test_initial_and_near_empty_genuine_zero_are_valid(self):
        for baseline in (None, 0.5):
            with self.subTest(baseline=baseline):
                owner = self.setup_owner(baseline=baseline)
                self.capture(owner, 0, 0, 0)
                self.assertNotIn("native_zero_capture", owner.ledger.data)
                self.assertEqual(owner.ledger.data["last"]["soc"], 0)

    def test_pending_source_and_capacity_switch_preserve_observed_distance(self):
        for capacity in (90, 75):
            with self.subTest(capacity=capacity):
                owner = self.setup_owner("companion:3")
                self.capture(owner, 0, 0, 0, 1002)
                if capacity != 90:
                    updated = {**owner.settings, "capacity_kwh": capacity}
                    owner.ledger.begin_new_epoch(updated)
                    owner.settings = updated
                    owner.ledger = Ledger(updated, owner.ledger.data)
                self.capture(owner, 15, 50, 250, 1002, source="companion:4")
                snapshot = self.snapshot(owner, 16)
                self.assertIsNone(snapshot["pending_native_capture"])
                self.assertEqual(snapshot["statistics"]["day"]["distance_km"], 2)
                self.assertEqual(
                    snapshot["statistics"]["day"]["unaccounted_distance_km"], 2
                )
                self.assertEqual(owner.ledger.data["parked_losses"], [])
                self.assertEqual(owner.ledger.data["charges"], {})

    def test_pending_backup_rejects_malformed_state_and_invalid_quality_cannot_confirm(
        self,
    ):
        owner = self.setup_owner("companion:3")
        self.capture(owner, 0, 0, 0, 1001)
        self.capture(owner, 120, 0, 0, 1002, quality="stale")
        self.assertFalse(owner.ledger.data["native_zero_capture"]["released"])
        self.assertEqual(owner.saved["native_zero_capture"]["latest"]["odo"], 1002)
        self.assertIsNone(
            self.snapshot(owner, 121)["statistics"]["last_100km"]["remaining_kwh"]
        )
        malformed = deepcopy(owner.saved)
        malformed["native_zero_capture"]["latest"]["odo"] = float("nan")
        with self.assertRaises(ValueError):
            validate_history(malformed)

        malformed = deepcopy(owner.saved)
        malformed["native_zero_capture"]["extra"] = "unsupported"
        with self.assertRaises(ValueError):
            validate_history(malformed)

    def test_recent_trip_anchor_cannot_consume_the_withheld_zero(self):
        owner = self.setup_owner(baseline=None)
        owner.ledger.ingest(self.clock.timestamp() - 60, 999, None, soc_pct=61.5)
        owner.ledger.ingest(self.clock.timestamp() - 10, 1000, None, soc_pct=60.5)
        original_kwh = owner.ledger.data["active"]["segments"][0]["kwh"]
        self.capture(owner, 0, 0, 0)
        self.capture(owner, 61, 0, 0)
        self.assertEqual(
            owner.ledger.data["trips"][0]["segments"][0]["kwh"], original_kwh
        )
        self.assertEqual(owner.ledger.data["last"]["soc"], 0)
        self.assertEqual(len(owner.ledger.data["parked_losses"]), 1)
        self.assertAlmostEqual(owner.ledger.data["parked_losses"][0]["kwh"], 54.45)

    def test_generation_only_cannot_release_pending_zero_or_create_refill(self):
        owner = self.setup_owner("companion:3")
        self.capture(owner, 0, 0, 0, 1001)
        self.capture(
            owner, 120, 0, 0, 1002, source="companion:4", clocks=0, retained=True
        )
        self.assertEqual(owner.ledger.data["last"]["soc"], 60.5)
        self.assertIsNone(owner.saved["native_zero_capture"]["started"])
        self.assertEqual(owner.ledger.data["telemetry_source"], "companion:3")
        owner = self.setup_owner("companion:3", validate_history(owner.saved))
        self.capture(owner, 135, 60.5, 313, 1002, source="companion:4")
        snapshot = self.snapshot(owner, 136)
        self.assertIsNone(snapshot["pending_native_capture"])
        self.assertEqual(snapshot["statistics"]["day"]["distance_km"], 2)
        self.assertEqual(snapshot["statistics"]["day"]["unaccounted_distance_km"], 2)
        self.assertEqual(owner.ledger.data["parked_losses"], [])
        self.assertEqual(owner.ledger.data["charges"], {})

    def test_first_zero_after_generation_change_uses_saved_validation_baseline(self):
        owner = self.setup_owner("companion:3")
        self.capture(owner, 0, 0, 0, 1001, source="companion:4")
        self.assertEqual(owner.ledger.data["last"]["soc"], 60.5)
        self.assertIn("native_zero_capture", owner.saved)
        owner = self.setup_owner("companion:3", validate_history(owner.saved))
        self.capture(owner, 15, 60.5, 313, 1001, source="companion:4")
        self.assertEqual(owner.ledger.data["charges"], {})
        self.assertEqual(owner.ledger.data["parked_losses"], [])
        self.assertEqual(
            owner.ledger.statistics(0, self.clock.timestamp() + 16)[
                "unaccounted_distance_km"
            ],
            1,
        )
        self.assertEqual(owner.ledger.data["telemetry_source"], "companion:4")
        self.assertIsNone(owner.ledger.data["pending_epoch"])

    def test_first_zero_after_capacity_change_keeps_old_unit_only_as_validation(self):
        owner = self.setup_owner()
        updated = {**owner.settings, "capacity_kwh": 75}
        owner.ledger.begin_new_epoch(updated)
        archived = validate_history(json.loads(json.dumps(owner.ledger.data)))
        self.assertEqual(
            archived["pending_epoch"]["native_validation_baseline"]["capacity_kwh"], 90
        )
        owner.settings = updated
        owner.ledger = Ledger(updated, archived)
        self.capture(owner, 0, 0, 0, 1001)
        self.assertIsNone(owner.ledger.data["last"])
        self.assertEqual(owner.ledger.data["native_zero_capture"]["capacity_kwh"], 90)
        self.capture(owner, 15, 60.5, 313, 1001)
        self.assertAlmostEqual(owner.ledger.data["last"]["energy"], 45.375)
        self.assertEqual(owner.ledger.data["charges"], {})
        self.assertEqual(owner.ledger.data["parked_losses"], [])
        self.assertEqual(
            owner.ledger.statistics(0, self.clock.timestamp() + 16)[
                "unaccounted_distance_km"
            ],
            1,
        )
        self.assertIsNone(owner.ledger.data["pending_epoch"])

    def test_pending_epoch_validation_baseline_is_strictly_validated(self):
        owner = self.setup_owner()
        owner.ledger.begin_new_epoch({**owner.settings, "capacity_kwh": 75})
        malformed = deepcopy(owner.ledger.data)
        malformed["pending_epoch"]["native_validation_baseline"]["sample"]["soc"] = (
            float("nan")
        )
        with self.assertRaises(ValueError):
            validate_history(malformed)
        malformed = deepcopy(owner.ledger.data)
        malformed["pending_epoch"]["native_validation_baseline"]["capacity_kwh"] = 75
        with self.assertRaises(ValueError):
            validate_history(malformed)

    def test_one_advancing_field_cannot_confirm_even_with_fresh_flags(self):
        owner = self.setup_owner()
        self.capture(owner, 0, 0, 0)
        self.capture(owner, 122, 0, 0, clocks=122, range_clock=0)
        self.assertIn("native_zero_capture", owner.ledger.data)
        self.capture(owner, 123, 0, 0, clocks=122, range_clock=123)
        self.assertIn("native_zero_capture", owner.ledger.data)
        self.capture(owner, 124, 0, 0)
        self.assertNotIn("native_zero_capture", owner.ledger.data)
        self.assertEqual(
            owner.ledger.data["last"]["t"],
            (self.clock + timedelta(seconds=124)).timestamp(),
        )

    def test_capacity_change_keeps_pending_context_and_extra_distance(self):
        owner = self.setup_owner()
        self.capture(owner, 0, 0, 0, 1001)
        updated = {**owner.settings, "capacity_kwh": 75}
        owner.ledger.begin_new_epoch(updated)
        owner.settings = updated
        owner.ledger = Ledger(updated, validate_history(owner.ledger.data))
        self.capture(owner, 120, 0, 0, 1002, clocks=0, retained=True)
        self.assertIsNone(owner.ledger.data["last"])
        self.assertIn("native_zero_capture", owner.ledger.data)
        self.capture(owner, 135, 60.5, 313, 1002)
        snapshot = self.snapshot(owner, 136)
        self.assertEqual(snapshot["statistics"]["day"]["distance_km"], 2)
        self.assertEqual(snapshot["statistics"]["day"]["unaccounted_distance_km"], 2)
        self.assertIsNone(snapshot["pending_native_capture"])
        self.assertEqual(owner.ledger.data["parked_losses"], [])
        self.assertEqual(owner.ledger.data["charges"], {})
