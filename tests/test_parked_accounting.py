"""Same-input conservation, source-boundary and reversible-review regressions."""

import importlib.util
import json
import pathlib
import sys
import types
import unittest
from copy import deepcopy
from dataclasses import replace
from datetime import UTC, datetime, timedelta
from unittest.mock import patch

from custom_components.nio_telematics.companion_coordinator import (
    CompanionDataUpdateCoordinator,
)
from custom_components.nio_telematics.dashboard_backup import validate_history
from custom_components.nio_telematics.models import NioSocStatus, NioVehicleData

ROOT = pathlib.Path(__file__).parents[1] / "custom_components" / "nio_telematics"
package = types.ModuleType("parked_ledger")
package.__path__ = [str(ROOT / "car_dashboard")]
sys.modules[package.__name__] = package
spec = importlib.util.spec_from_file_location(
    "parked_ledger.ledger", ROOT / "car_dashboard" / "ledger.py"
)
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)
Ledger = module.Ledger


class ParkedAccountingTests(unittest.TestCase):
    t = 1795590000

    def ledger(self):
        result = Ledger({"capacity_kwh": 90, "full_range_km": 557})
        result.preferences({"opening_price_eur_kwh": 2})
        return result

    def sample(self, ledger, seconds, soc, odo=1000, connected=False, since=None):
        ledger.observe_native_sources(
            self.t + seconds, odo, self.t + seconds, soc, connected, since
        )

    def test_oscillation_nets_before_inventory_and_retains_raw_evidence(self):
        ledger = self.ledger()
        for at, soc in ((0, 80), (600, 79.5), (1200, 80), (1800, 79.5)):
            self.sample(ledger, at, soc)
        raw = deepcopy(ledger.data["parked_losses"])
        self.assertAlmostEqual(sum(r["kwh"] for r in raw), 0.9)
        self.assertAlmostEqual(
            sum(r["kwh"] for r in ledger.accounting_parked_losses()), 0.45
        )
        self.sample(ledger, 3900, 78.5, 1001)
        self.assertAlmostEqual(ledger.cost_segments()[-1]["cost_eur"], 1.8)
        self.assertEqual(ledger.data["parked_losses"], raw)
        self.assertFalse(ledger.data["charges"])
        self.assertTrue(
            all(r["kwh"] >= 0 for r in ledger.measurement_error_intervals())
        )

    def test_recovery_above_start_does_not_create_priced_energy_or_loss(self):
        ledger = self.ledger()
        for at, soc in ((0, 80), (600, 79.5), (1200, 80.5), (1800, 80)):
            self.sample(ledger, at, soc)
        self.assertAlmostEqual(
            sum(r["kwh"] for r in ledger.accounting_parked_losses()), 0
        )
        self.sample(ledger, 3900, 79, 1001)
        self.assertAlmostEqual(ledger.cost_segments()[-1]["cost_eur"], 1.8)

    def test_actual_arrival_endpoint_is_allocated_once(self):
        ledger = self.ledger()
        self.sample(ledger, 0, 80)
        self.sample(ledger, 60, 79, 1001, True, self.t + 50)
        self.sample(ledger, 90, 78.5, 1001, False, self.t + 80)
        self.assertAlmostEqual(sum(r["kwh"] for r in ledger.cost_segments()), 0.9)
        self.assertEqual(ledger.accounting_parked_losses(), [])
        row = ledger.measurement_error_intervals()[0]
        self.assertEqual(row["accounting_basis"], "connection_boundary")
        self.assertAlmostEqual(row["recorded_kwh"], 0.45)
        self.sample(ledger, 800, 77.5, 1002, False, self.t + 80)
        self.assertAlmostEqual(sum(r["cost_eur"] for r in ledger.cost_segments()), 3.6)

    def test_fresh_early_soc_and_late_odometer_conserve_without_guessed_category(self):
        ledger = self.ledger()
        self.sample(ledger, 0, 80)
        self.sample(ledger, 60, 79.5)
        self.sample(ledger, 90, 79, 1001)
        combined = sum(r["kwh"] for r in ledger.cost_segments()) + sum(
            r["kwh"] for r in ledger.accounting_parked_losses()
        )
        self.assertAlmostEqual(combined, 0.9)

    def test_capacity_epoch_cannot_rewrite_previous_trip(self):
        ledger = self.ledger()
        self.sample(ledger, 0, 80)
        self.sample(ledger, 60, 79, 1001)
        ledger.begin_new_epoch({"capacity_kwh": 75, "full_range_km": 557})
        before = deepcopy(ledger.data["trips"])
        ledger = Ledger({"capacity_kwh": 75, "full_range_km": 557}, ledger.data)
        self.sample(ledger, 120, 79, 1001)
        self.assertEqual(ledger.data["trips"], before)
        self.assertAlmostEqual(before[0]["segments"][0]["kwh"], 0.9)

    def test_charge_boundary_never_becomes_parked_usage(self):
        ledger = self.ledger()
        ledger.import_home([[1, self.t, self.t + 120, 5, 0, 10, None, None]])
        self.sample(ledger, 0, 60, connected=True)
        self.sample(ledger, 60, 59)
        self.assertEqual(ledger.accounting_parked_losses(), [])
        # An old row with complete retained endpoints is audited rather than
        # silently spent as a parked loss or converted from the wall meter.
        ledger.data["parked_losses"][0].pop("allocation_guard", None)
        row = ledger.measurement_error_intervals()[0]
        self.assertEqual(row["accounting_basis"], "charging_boundary")
        self.assertEqual(row["kwh"], 0)
        self.assertAlmostEqual(row["recorded_kwh"], 0.9)
        self.assertEqual(ledger.parked_periods(), [])

    def test_net_projection_survives_buffer_expiry_and_backup_roundtrip(self):
        ledger = self.ledger()
        for at, soc in ((0, 80), (60, 79.5), (120, 80), (180, 79.5)):
            self.sample(ledger, at, soc)
        ledger.data["samples"] = []
        restored = Ledger(
            ledger.settings, validate_history(json.loads(json.dumps(ledger.data)))
        )
        self.assertAlmostEqual(
            sum(r["kwh"] for r in restored.accounting_parked_losses()), 0.45
        )
        invalid = deepcopy(ledger.data)
        invalid["parking_source_paths"][0][0]["until"] = float("nan")
        with self.assertRaises(ValueError):
            validate_history(invalid)

    def test_long_unchanged_parking_is_compact_and_gaps_break_recovery(self):
        ledger = self.ledger()
        for at in range(0, 24 * 3600, 30):
            ledger.ingest(self.t + at, 1000, None, soc_pct=80)
        self.assertLess(len(json.dumps(ledger.data["parking_source_paths"])), 600)
        ledger.ingest(self.t + 86400, 1000, None, soc_pct=79.5)
        ledger.ingest(self.t + 86400 + 3600, 1000, None, soc_pct=80)
        self.assertAlmostEqual(
            sum(r["kwh"] for r in ledger.accounting_parked_losses()), 0.45
        )

    def test_partial_legacy_coverage_is_not_rebuilt(self):
        ledger = self.ledger()
        for at, soc in ((0, 80), (600, 79.5), (1200, 80)):
            self.sample(ledger, at, soc)
        ledger.data["parking_source_paths"] = []
        ledger.data["samples"] = ledger.data["samples"][1:]
        self.assertAlmostEqual(
            sum(r["kwh"] for r in ledger.accounting_parked_losses()), 0.45
        )

    def test_projection_cache_rechecks_source_charge_and_overlay_edits(self):
        ledger = self.ledger()
        for at, soc in ((0, 80), (600, 79.5), (1200, 80)):
            self.sample(ledger, at, soc)
        self.assertEqual(ledger.accounting_parked_losses(), [])
        # No changed()/revision shortcut: exact retained-source edits must be
        # visible even when an imported archive is amended before save.
        ledger.data["parking_source_paths"] = []
        ledger.data["samples"] = ledger.data["samples"][:-1]
        self.assertAlmostEqual(
            sum(r["kwh"] for r in ledger.accounting_parked_losses()), 0.45
        )
        ledger.data["charges"]["overlap"] = {
            "id": "overlap",
            "kind": "home",
            "start": self.t,
            "end": self.t + 600,
            "kwh": 1,
            "confirmed": True,
            "cost_eur": 2,
        }
        self.assertEqual(ledger.accounting_parked_losses(), [])
        self.assertEqual(
            ledger.measurement_error_intervals()[0]["accounting_basis"],
            "charging_boundary",
        )
        ledger.data["charges"].clear()
        row = ledger.measurement_error_intervals()[0]
        ledger.set_measurement_error(row["id"], row["fingerprint"], True)
        self.assertEqual(ledger.accounting_parked_losses(), [])
        ledger.set_measurement_error(row["id"], row["fingerprint"], False)
        self.assertAlmostEqual(
            sum(r["kwh"] for r in ledger.accounting_parked_losses()), 0.45
        )

    def test_legacy_arrival_connection_double_allocation_is_derived_not_raw_edit(self):
        ledger = self.ledger()
        self.sample(ledger, 0, 80)
        self.sample(ledger, 60, 79, 1001, True, self.t + 50)
        self.sample(ledger, 90, 78.5, 1001, False, self.t + 80)
        # Reproduce the exact dev.7 endpoint extension retained in an archive.
        trip = ledger.data["trips"][0]
        trip["endpoint_soc_time"] = self.t + 90
        trip["end_energy"] = trip["segments"][-1]["end_energy"] = 70.65
        trip["segments"][-1]["kwh"] = 1.35
        before = deepcopy(ledger.data)
        rows = ledger.cost_segments()
        self.assertAlmostEqual(rows[0]["kwh"], 0.9)
        self.assertAlmostEqual(rows[0]["cost_eur"], 1.8)
        self.assertEqual(ledger.data, before)

    def test_exclusion_applies_after_net_without_redistribution(self):
        ledger = self.ledger()
        for at, soc in ((0, 80), (300, 79.5), (600, 79), (900, 79.5)):
            self.sample(ledger, at, soc)
        before = ledger.measurement_error_intervals()
        self.assertAlmostEqual(before[0]["kwh"], 0.45)
        self.assertEqual(before[1]["kwh"], 0)
        ledger.set_measurement_error(before[0]["id"], before[0]["fingerprint"], True)
        self.assertEqual(ledger.accounting_parked_losses(), [])
        self.assertEqual(ledger.measurement_error_intervals()[1]["kwh"], 0)
        ledger.set_measurement_error(before[0]["id"], before[0]["fingerprint"], False)
        self.assertAlmostEqual(
            sum(r["kwh"] for r in ledger.accounting_parked_losses()), 0.45
        )

    def test_excluded_legacy_boundary_cannot_still_change_inventory(self):
        ledger = self.ledger()
        self.sample(ledger, 0, 80)
        self.sample(ledger, 600, 79.5)
        # A valid dev.7 choice survives a later derived category change.
        row = ledger.measurement_error_intervals()[0]
        ledger.set_measurement_error(row["id"], row["fingerprint"], True)
        ledger.data["samples"][0]["home_connected"] = True
        self.assertEqual(
            ledger.measurement_error_intervals()[0]["accounting_basis"],
            "connection_boundary",
        )
        self.assertEqual(ledger.unaccounted_parked_intervals(), [])
        ledger.import_home([[1, self.t + 700, self.t + 800, 5, 0, 5, None, None]])
        ledger.ingest(self.t + 900, 1000, None, soc_pct=85)
        ledger.ingest(self.t + 1500, 1001, None, soc_pct=84)
        excluded_cost = ledger.cost_segments()[-1]["cost_eur"]
        self.assertAlmostEqual(excluded_cost, 0.9 * 149 / 77)
        ledger.set_measurement_error(row["id"], row["fingerprint"], False)
        self.assertEqual(len(ledger.unaccounted_parked_intervals()), 1)
        self.assertNotAlmostEqual(ledger.cost_segments()[-1]["cost_eur"], excluded_cost)
        ledger.set_measurement_error(row["id"], row["fingerprint"], True)
        ledger.data["parked_losses"][0]["complete"] = False
        self.assertEqual(ledger.measurement_error_intervals()[0]["state"], "stale")
        self.assertEqual(len(ledger.unaccounted_parked_intervals()), 1)

    def test_long_archived_zero_refill_is_review_only_and_pair_edits_stale(self):
        ledger = self.ledger()
        loss = {
            "start": self.t,
            "end": self.t + 7200,
            "kwh": 68.4,
            "end_energy": 0,
            "complete": True,
        }
        candidate = {
            "id": "candidate",
            "kind": "dismissed",
            "start": loss["end"],
            "end": loss["end"] + 6360,
            "kwh": 68.4,
            "estimated_kwh": 68.4,
            "confirmed": False,
            "cost_eur": None,
            "price_eur_kwh": None,
        }
        ledger.data["parked_losses"] = [deepcopy(loss)]
        ledger.data["charges"] = {"candidate": candidate}
        row = ledger.measurement_error_intervals()[0]
        self.assertTrue(row["review_required"])
        self.assertEqual(row["evidence_basis"], "archived_pair_only")
        self.assertEqual(row["paired_candidate_duration_seconds"], 6360)
        self.assertEqual(row["kwh"], 68.4)
        ledger.set_measurement_error(row["id"], row["fingerprint"], True)
        self.assertEqual(ledger.accounting_charges(), [])
        candidate["confirmed"] = True
        self.assertEqual(len(ledger.accounting_charges()), 1)
        self.assertEqual(ledger.data["parked_losses"], [loss])
        ledger.set_measurement_error(row["id"], row["fingerprint"], False)
        self.assertEqual(ledger.accounting_parked_losses()[0]["kwh"], 68.4)


class CompanionEnergyValidationTests(unittest.TestCase):
    clock = datetime(2026, 11, 25, 16, 10, tzinfo=UTC)

    def vehicle(
        self, soc=60.5, distance=313, at=0, quality="valid", generation=3, range_at=None
    ):
        soc_at = self.clock + timedelta(seconds=at)
        range_at = self.clock + timedelta(seconds=at if range_at is None else range_at)
        return NioVehicleData(
            "TEST",
            NioSocStatus(soc, distance, None, None, None, None, soc_at),
            self.clock,
            {},
            {},
            soc_last_valid_at=soc_at,
            remaining_range_last_valid_at=range_at,
            connection_method="companion",
            source_generation=generation,
            field_metadata={
                "socPercent": {"quality": quality, "source_timestamp": soc_at},
                "rangeKm": {"quality": quality, "source_timestamp": range_at},
            },
        )

    def owner(self, soc=60.5):
        owner = CompanionDataUpdateCoordinator.__new__(CompanionDataUpdateCoordinator)
        owner.data = self.vehicle(soc=soc)
        owner._joint_zero_pending = None
        owner._rejected_zero_at = {}
        return owner

    def read(self, owner, vehicle, elapsed):
        with patch(
            "custom_components.nio_telematics.companion_coordinator.time.monotonic",
            return_value=elapsed,
        ):
            owner.data = owner._validate_energy(vehicle)
        return owner.data

    def test_cached_generation_change_cannot_confirm_and_advancing_pair_can(self):
        owner = self.owner()
        initial = owner.data.soc_last_valid_at
        self.read(owner, self.vehicle(0, 0, at=1), 0)
        held = self.read(owner, self.vehicle(0, 0, at=1, generation=4), 120)
        self.assertEqual(held.soc_status.soc, 60.5)
        self.assertEqual(held.soc_last_valid_at, initial)
        self.assertTrue(held.field_metadata["socPercent"]["validation_blocked"])
        one = self.read(
            owner, self.vehicle(0, 0, at=122, range_at=1, generation=4), 121
        )
        self.assertEqual(one.soc_status.soc, 60.5)
        final = self.read(owner, self.vehicle(0, 0, at=123, generation=4), 122)
        self.assertEqual(final.soc_status.soc, 0)
        self.assertEqual(final.soc_last_valid_at, self.clock + timedelta(seconds=123))

    def test_stale_pair_never_confirms_and_positive_cancels(self):
        owner = self.owner()
        self.read(owner, self.vehicle(0, 0, at=1), 0)
        self.assertEqual(
            self.read(
                owner, self.vehicle(0, 0, at=122, quality="stale"), 121
            ).soc_status.soc,
            60.5,
        )
        self.assertEqual(
            self.read(owner, self.vehicle(60.5, 313, at=123), 122).soc_status.soc, 60.5
        )
        self.assertIsNone(owner._joint_zero_pending)

    def test_first_same_or_older_clock_joint_zero_preserves_baseline(self):
        for at, retained in ((0, True), (0, False), (-1, True), (-1, False)):
            with self.subTest(at=at, retained=retained):
                owner = self.owner()
                baseline = owner.data
                pair = replace(
                    self.vehicle(0, 0, at=at, generation=4),
                    soc_retained=retained,
                    remaining_range_retained=retained,
                )
                held = self.read(owner, pair, 120)
                self.assertEqual(held.soc_status.soc, 60.5)
                self.assertEqual(held.soc_status.remaining_range, 313)
                self.assertEqual(held.soc_last_valid_at, baseline.soc_last_valid_at)
                self.assertEqual(
                    held.remaining_range_last_valid_at,
                    baseline.remaining_range_last_valid_at,
                )
                self.assertTrue(held.field_metadata["socPercent"]["validation_blocked"])
                self.assertIsNone(owner._joint_zero_pending)

    def test_retained_advanced_zero_cannot_confirm_and_cached_positive_cannot_cancel(
        self,
    ):
        owner = self.owner()
        self.read(owner, self.vehicle(0, 0, at=1), 0)
        retained = replace(
            self.vehicle(0, 0, at=122, generation=4),
            soc_retained=True,
            remaining_range_retained=True,
        )
        self.assertEqual(self.read(owner, retained, 121).soc_status.soc, 60.5)
        self.assertIsNotNone(owner._joint_zero_pending)
        cached_positive = replace(
            self.vehicle(60.5, 313, at=0, generation=5),
            soc_retained=True,
            remaining_range_retained=True,
        )
        positive = self.read(owner, cached_positive, 122)
        self.assertEqual(positive.soc_status.soc, 60.5)
        self.assertEqual(positive.soc_last_valid_at, self.clock)
        self.assertIsNotNone(owner._joint_zero_pending)
        confirmed = self.read(owner, self.vehicle(0, 0, at=123, generation=5), 123)
        self.assertEqual(confirmed.soc_status.soc, 0)
        self.assertEqual(
            confirmed.soc_last_valid_at, self.clock + timedelta(seconds=123)
        )

    def test_initial_near_empty_and_single_range_zero_are_valid(self):
        for soc in (None, 0.5):
            owner = self.owner(soc=soc)
            if soc is None:
                owner.data = None
            self.assertEqual(
                self.read(owner, self.vehicle(0, 0, at=1), 0).soc_status.soc, 0
            )
        owner = self.owner()
        self.assertEqual(
            self.read(owner, self.vehicle(60.5, 0, at=1), 0).soc_status.remaining_range,
            0,
        )
