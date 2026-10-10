"""Calculation and persistence checks, independent of a running HA instance."""

import importlib.util
import json
import pathlib
import sys
import types
import unittest

root = (
    pathlib.Path(__file__).parents[1]
    / "custom_components"
    / "nio_telematics"
    / "car_dashboard"
)
package = types.ModuleType("car_ledger")
package.__path__ = [str(root)]
sys.modules["car_ledger"] = package
spec = importlib.util.spec_from_file_location("car_ledger.ledger", root / "ledger.py")
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)
Ledger = module.Ledger


class CalculationTests(unittest.TestCase):
    def setUp(self):
        self.ledger = Ledger({"capacity_kwh": 90, "full_range_km": 450})
        self.t = 1791540000

    def drive(self):
        self.ledger.ingest(self.t, 1000, 250)
        self.ledger.ingest(self.t + 600, 1010, 240)
        self.ledger.ingest(self.t + 1200, 1020, 230)

    def test_consumption_from_unrounded_energy(self):
        self.drive()
        stats = self.ledger.statistics(self.t, self.t + 1200)
        self.assertEqual(stats["distance_km"], 20)
        self.assertEqual(stats["used_kwh"], 4)
        self.assertEqual(stats["consumption_kwh_100km"], 20)
        self.assertIsNone(stats["driving_cost_eur"])

    def test_known_opening_price_and_zero_price(self):
        for price in (0.3, 0):
            ledger = Ledger({"capacity_kwh": 90, "full_range_km": 450})
            ledger.preferences({"opening_price_eur_kwh": price})
            ledger.ingest(self.t, 1000, 250)
            ledger.ingest(self.t + 600, 1010, 240)
            stats = ledger.statistics(self.t, self.t + 600)
            self.assertAlmostEqual(stats["cost_eur_100km"], 20 * price)

    def test_restore_does_not_duplicate_sample_or_trip(self):
        self.drive()
        restored = Ledger(
            self.ledger.settings, json.loads(json.dumps(self.ledger.data))
        )
        self.assertFalse(restored.ingest(self.t + 1200, 1020, 230))
        restored.tick(self.t + 3000)
        self.assertEqual(len(restored.data["trips"]), 1)
        self.assertEqual(restored.data["trips"][0]["distance_km"], 20)

    def test_home_charge_closes_trip_without_public_candidate(self):
        self.drive()
        self.ledger.ingest(self.t + 1500, 1020, 280, True)
        self.assertIsNone(self.ledger.data["active"])
        self.assertEqual(len(self.ledger.data["trips"]), 1)
        self.assertFalse(self.ledger.data["charges"])

    def test_public_candidate_rate_and_receipt(self):
        self.drive()
        self.ledger.ingest(self.t + 1500, 1020, 280)
        self.ledger.ingest(self.t + 1800, 1020, 300)
        self.assertEqual(len(self.ledger.data["charges"]), 1)
        charge = next(iter(self.ledger.data["charges"].values()))
        self.assertFalse(charge["confirmed"])
        self.assertAlmostEqual(charge["kwh"], 14)
        self.ledger.edit_charge(charge["id"], price=0.5)
        self.assertEqual(charge["kind"], "public")
        self.assertAlmostEqual(charge["cost_eur"], 7)
        self.ledger.edit_charge(charge["id"], receipt=8, kwh=16)
        self.assertEqual(charge["cost_eur"], 8)

    def test_archive_and_home_upserts_preserve_manual_cost(self):
        rows = [
            [1, self.t - 40000000, self.t - 39999900, 20, 100, None, 6, None],
            [2, self.t, self.t + 100, 0.15, 0, 0, 0.05, 0.05],
        ]
        self.ledger.import_home(rows)
        self.ledger.edit_charge("home-1", price=0.2)
        self.ledger.import_home(rows)
        self.ledger.import_home([])
        self.assertEqual(len(self.ledger.data["charges"]), 2)
        self.assertEqual(self.ledger.data["charges"]["home-1"]["cost_eur"], 4)
        self.assertEqual(self.ledger.data["charges"]["home-2"]["cost_eur"], 0)

    def test_gap_does_not_claim_complete_energy_or_cost(self):
        self.ledger.preferences({"opening_price_eur_kwh": 0.3})
        self.ledger.ingest(self.t, 1000, 250)
        self.ledger.ingest(self.t + 3600, 1020, 220)
        self.ledger.add_charge(self.t + 3700, self.t + 3800, 10, price=0.5)
        self.ledger.ingest(self.t + 3900, 1025, 215)
        stats = self.ledger.statistics(self.t, self.t + 3900)
        self.assertIsNone(stats["used_kwh"])
        self.assertIsNone(stats["driving_cost_eur"])

    def test_invalid_input_and_free_manual_charge(self):
        ident = self.ledger.add_charge(self.t, self.t + 100, 10, price=0)
        self.assertEqual(self.ledger.data["charges"][ident]["cost_eur"], 0)
        with self.assertRaises(ValueError):
            self.ledger.edit_charge(ident, price="nonsense")
        with self.assertRaises(ValueError):
            self.ledger.add_charge(self.t, self.t + 100, -2)

    def test_charge_unplugged_between_samples_is_not_public(self):
        self.drive()
        self.ledger.import_home([[1, self.t + 1250, self.t + 1450, 10, 80, 2, 3, 1]])
        self.ledger.ingest(self.t + 1500, 1020, 280, False)
        self.assertEqual(len(self.ledger.data["charges"]), 1)
        self.assertEqual(
            self.ledger.snapshot(self.t + 1600)["statistics"]["since_charge"][
                "distance_km"
            ],
            0,
        )

    def test_stationary_loss_not_claimed_as_driving(self):
        self.ledger.ingest(self.t, 1000, 250)
        self.ledger.ingest(self.t + 600, 1000, 249)
        stats = self.ledger.statistics(self.t, self.t + 600)
        self.assertEqual(stats["distance_km"], 0)
        self.assertAlmostEqual(stats["parked_loss_estimate_kwh"], 0.2)

    def test_latest_100_km_is_weighted_and_resets_after_charge(self):
        self.ledger.ingest(self.t, 1000, 450)
        for i in range(1, 7):
            self.ledger.ingest(self.t + i * 600, 1000 + i * 20, 450 - i * 20)
        stats = self.ledger.statistics(self.t, self.t + 3600, 100)
        self.assertEqual(stats["distance_km"], 100)
        self.assertAlmostEqual(stats["used_kwh"], 20)
        self.ledger.add_charge(self.t + 3700, self.t + 3800, 20, price=0.4)
        snap = self.ledger.snapshot(self.t + 4000)
        self.assertEqual(snap["statistics"]["last_100km"]["distance_km"], 0)

    def test_last_trip_excludes_current_trip_and_boundary_segment(self):
        self.drive()
        self.ledger.close_trip()
        self.ledger.ingest(self.t + 1500, 1025, 225)
        snap = self.ledger.snapshot(self.t + 1500)
        self.assertEqual(snap["statistics"]["last_trip"]["distance_km"], 20)
        self.assertEqual(snap["statistics"]["current_trip"]["distance_km"], 5)
        self.ledger.close_trip()
        snap = self.ledger.snapshot(self.t + 1500)
        self.assertEqual(snap["statistics"]["last_trip"]["distance_km"], 5)
        self.assertNotIn("current_trip", snap["statistics"])

    def test_recovery_is_persistent_and_idempotent(self):
        samples = [
            {"t": self.t, "odo": 1000, "range": 250, "home_connected": False},
            {"t": self.t + 600, "odo": 1010, "range": 240, "home_connected": False},
        ]
        self.ledger.recover_history(samples, self.t + 3000)
        restored = Ledger(self.ledger.settings, self.ledger.data)
        restored.recover_history(samples, self.t + 4000)
        self.assertEqual(len(restored.all_trips()), 1)
        self.assertEqual(
            restored.snapshot(self.t + 4000)["statistics"]["last_trip"]["distance_km"],
            10,
        )

    def test_traffic_stop_energy_and_idle_timeout(self):
        self.drive()
        self.ledger.ingest(self.t + 1500, 1020, 229)
        snap = self.ledger.snapshot(self.t + 1500)
        self.assertAlmostEqual(snap["statistics"]["current_trip"]["used_kwh"], 4)
        self.assertAlmostEqual(
            snap["statistics"]["day"]["parked_loss_estimate_kwh"], 0.2
        )
        self.ledger.tick(self.t + 2700)
        self.assertIsNone(self.ledger.data["active"])

    def test_hour_gap_with_movement_counts_energy(self):
        self.ledger.ingest(self.t, 1000, 250)
        self.ledger.ingest(self.t + 3600, 1001, 248)
        self.assertAlmostEqual(
            self.ledger.statistics(self.t, self.t + 3600)["used_kwh"], 0.4
        )

    def test_legacy_stationary_energy_reclassified_and_idempotent(self):
        self.drive()
        self.ledger.ingest(self.t + 1500, 1020, 229)
        self.ledger.close_trip()
        trip = self.ledger.data["trips"][0]
        ident = trip["id"]
        trip["segments"][-1]["kwh"] += 0.2
        trip["segments"][-1].update(end=self.t + 1500, end_energy=45.8)
        trip.update(end=self.t + 1500, end_energy=45.8)
        self.ledger.data["parked_losses"] = []
        samples = list(self.ledger.data["samples"])
        self.ledger.classify_recorded_intervals()
        self.assertEqual(trip["id"], ident)
        self.assertEqual(self.ledger.data["samples"], samples)
        self.assertAlmostEqual(sum(s["kwh"] for s in trip["segments"]), 4)
        self.assertAlmostEqual(self.ledger.data["parked_losses"][0]["kwh"], 0.2)
        before = self.ledger.data["revision"]
        self.ledger.classify_recorded_intervals()
        self.assertEqual(self.ledger.data["revision"], before)

    def test_parked_history_conserves_energy_and_does_not_join_gaps(self):
        self.ledger.data["parked_losses"] = [
            dict(start=self.t, end=self.t + 600, kwh=0.2, complete=True),
            dict(start=self.t + 600, end=self.t + 1200, kwh=0.3, complete=True),
            dict(start=self.t + 1800, end=self.t + 2400, kwh=0.1, complete=True),
            dict(start=self.t + 3000, end=self.t + 3600, kwh=0.7, complete=False),
        ]
        before = json.dumps(self.ledger.data, sort_keys=True)
        periods = self.ledger.snapshot(self.t + 4000)["parked_periods"]
        self.assertEqual(len(periods), 2)
        self.assertAlmostEqual(sum(p["kwh"] for p in periods), 0.6)
        self.assertAlmostEqual(periods[1]["soc_used_pct"], 0.5 / 90 * 100)
        self.assertEqual(periods[1]["end"] - periods[1]["start"], 1200)
        self.assertEqual(json.dumps(self.ledger.data, sort_keys=True), before)

    def test_native_soc_transition_preserves_archived_range_trip(self):
        self.drive()
        self.ledger.close_trip()
        archived = json.loads(json.dumps(self.ledger.data["trips"][0]))
        self.ledger.ingest(self.t + 1800, 1020, 228, soc_pct=50)
        self.assertEqual(self.ledger.data["source_transition_at"], self.t + 1800)
        self.assertEqual(self.ledger.data["last"]["energy"], 45)
        self.assertEqual(self.ledger.data["last"]["energy_source"], "native_soc")
        self.assertEqual(self.ledger.data["trips"][0], archived)
        self.assertEqual(len(self.ledger.data["charges"]), 0)
        self.ledger.classify_recorded_intervals()
        self.assertEqual(self.ledger.data["trips"][0], archived)

    def test_native_soc_uses_whole_percent_and_ignores_duplicate_after_restart(self):
        self.ledger.ingest(self.t, 1000, 250)
        self.ledger.ingest(self.t + 600, 1000, 249, soc_pct=50)
        restored = Ledger(
            self.ledger.settings, json.loads(json.dumps(self.ledger.data))
        )
        self.assertFalse(restored.ingest(self.t + 600, 1000, 249, soc_pct=50))
        restored.ingest(self.t + 1200, 1010, 245, soc_pct=49)
        trip = restored.data["active"]
        self.assertAlmostEqual(trip["segments"][0]["kwh"], 0.9)
        self.assertEqual(trip["segments"][0]["km"], 10)

    def test_native_soc_charge_boundary_is_not_driving_consumption(self):
        self.ledger.ingest(self.t, 1000, 250, soc_pct=50)
        self.ledger.ingest(self.t + 600, 1010, 245, soc_pct=49)
        self.ledger.ingest(self.t + 1200, 1010, 250, True, soc_pct=51)
        self.assertIsNone(self.ledger.data["active"])
        self.assertEqual(len(self.ledger.data["trips"]), 1)
        self.assertAlmostEqual(self.ledger.data["trips"][0]["segments"][0]["kwh"], 0.9)
        self.assertFalse(self.ledger.data["charges"])

    def test_reconfiguration_keeps_archives_and_starts_new_baseline(self):
        self.drive()
        self.ledger.close_trip()
        archived = json.loads(json.dumps(self.ledger.data["trips"]))
        self.ledger.begin_new_epoch({"capacity_kwh": 75, "full_range_km": 500})
        restored = Ledger(
            {"capacity_kwh": 75, "full_range_km": 500},
            json.loads(json.dumps(self.ledger.data)),
        )
        self.assertIsNone(restored.data["last"])
        self.assertEqual(restored.data["trips"], archived)
        restored.ingest(self.t + 1800, 1020, 230, soc_pct=50)
        self.assertEqual(restored.data["trips"], archived)
        self.assertFalse(restored.data["charges"])
        self.assertEqual(restored.data["last"]["energy"], 37.5)
        self.assertEqual(restored.data["source_transitions"][-1]["capacity_kwh"], 75)
        assert not restored.ingest(self.t + 1800, 1020, 230, soc_pct=50)


if __name__ == "__main__":
    unittest.main()
