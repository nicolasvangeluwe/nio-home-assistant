"""Calculation and persistence checks, independent of a running HA instance."""

import importlib.util
import json
import pathlib
import sys
import types
import unittest
from copy import deepcopy
from datetime import datetime, timedelta, timezone

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
provisional_home_charge = module.provisional_home_charge


class CalculationTests(unittest.TestCase):
    def setUp(self):
        self.ledger = Ledger({"capacity_kwh": 90, "full_range_km": 450})
        self.t = 1791540000

    def drive(self):
        self.ledger.ingest(self.t, 1000, 250)
        self.ledger.ingest(self.t + 600, 1010, 240)
        self.ledger.ingest(self.t + 1200, 1020, 230)

    def test_snapshot_uses_pre_resolved_timezone_for_local_dates(self):
        local_tz = timezone(timedelta(hours=2))
        now = datetime(2026, 10, 1, 0, 30, tzinfo=local_tz).timestamp()
        self.ledger.add_charge(now - 300, now - 60, 5, price=0.2)
        self.assertEqual(
            self.ledger.snapshot(now)["charging_daily"][0]["date"], "2026-09-30"
        )
        self.assertEqual(
            self.ledger.snapshot(now, local_tz)["charging_daily"][0]["date"],
            "2026-10-01",
        )

    def test_parked_periods_use_pre_resolved_timezone_at_month_boundary(self):
        local_tz = timezone(timedelta(hours=2))
        boundary = datetime(2026, 10, 1, 0, 0, tzinfo=local_tz).timestamp()
        self.ledger.data["parked_losses"] = [
            {
                "start": boundary - 600,
                "end": boundary - 60,
                "kwh": 0.2,
                "complete": True,
            },
            {
                "start": boundary - 60,
                "end": boundary + 600,
                "kwh": 0.3,
                "complete": True,
            },
        ]
        self.assertEqual(len(self.ledger.parked_periods()), 1)
        self.assertEqual(len(self.ledger.parked_periods(local_tz)), 2)

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

    def test_ongoing_home_charge_survives_restart_and_completes_same_id(self):
        start = [114, self.t, self.t + 100, 2.5, 90, 0.1, 0.8, 0.7]
        self.ledger.import_home([start])
        self.ledger.import_home([], active_session_id=114)
        self.assertEqual(self.ledger.snapshot(self.t + 200)["charges"], [])
        self.assertEqual(
            self.ledger.snapshot(self.t + 200)["active_home_charge"]["id"],
            "home-114",
        )
        restored = Ledger(
            self.ledger.settings, json.loads(json.dumps(self.ledger.data))
        )
        restored.import_home([start], active_session_id=114)
        self.assertEqual(restored.statistics(self.t, self.t + 200)["charged_kwh"], 0)
        final = [114, self.t, self.t + 300, 5.1, 95, 0.3, 1.6, 1.3]
        restored.import_home([final])
        restored.import_home([final])
        self.assertEqual(len(restored.data["charges"]), 1)
        self.assertEqual(restored.statistics(self.t, self.t + 400)["charged_kwh"], 5.1)
        self.assertIsNone(restored.snapshot(self.t + 400)["active_home_charge"])

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

    def test_native_rolling_100km_survives_a_later_charge(self):
        self.ledger.ingest(self.t, 1000, None, soc_pct=90)
        for index in range(1, 13):
            self.ledger.ingest(
                self.t + index * 600,
                1000 + index * 10,
                None,
                soc_pct=90 - index * 3,
            )
        self.ledger.close_trip()
        self.ledger.add_charge(self.t + 7350, self.t + 7400, 5, price=0.2)
        before = deepcopy(self.ledger.data)
        rolling = self.ledger.snapshot(self.t + 7500)["statistics"]["last_100km"]
        self.assertEqual(self.ledger.data, before)
        self.assertEqual(rolling["basis"], "native_soc_driving")
        self.assertEqual(rolling["distance_km"], 100)
        self.assertTrue(rolling["energy_complete"])
        self.assertAlmostEqual(rolling["consumption_kwh_100km"], 27)

    def test_snapshot_retains_history_contract_and_rolling_range(self):
        self.ledger.observe_native_sources(self.t, 1000, self.t - 10, 52)
        self.ledger.observe_native_sources(self.t + 120, 1001, self.t + 110, 51.5)
        snapshot = self.ledger.snapshot(self.t + 120)
        self.assertEqual(snapshot["experience_version"], 1)
        self.assertEqual(snapshot["trip_semantics_version"], 2)
        self.assertIn("driving_segments", snapshot)
        self.assertTrue(snapshot["battery_timeline"])
        self.assertEqual(
            snapshot["statistics"]["last_100km"]["basis"], "native_soc_driving"
        )

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

    def test_native_unchanged_reports_anchor_departure_after_home_charge(self):
        self.ledger.import_home(
            [[114, self.t - 3600, self.t - 1800, 36.85, 50, 5.014619, 0, 0]]
        )
        self.ledger.ingest(self.t, 6208, 400, soc_pct=89.5)
        self.ledger.ingest(self.t + 120, 6208, 400, soc_pct=89.5)
        self.ledger.ingest(self.t + 240, 6209, 399, soc_pct=89.5)
        trip = self.ledger.data["active"]
        self.assertEqual(trip["start"], self.t + 120)
        self.assertEqual(trip["segments"][0]["kwh"], 0)
        self.assertFalse(self.ledger.data["parked_losses"])

    def test_native_short_stop_is_not_parked_loss(self):
        self.ledger.ingest(self.t, 6208, 400, soc_pct=89.5)
        self.ledger.ingest(self.t + 120, 6209, 399, soc_pct=89.5)
        self.ledger.ingest(self.t + 240, 6209, 398, soc_pct=89)
        self.assertEqual(self.ledger.data["parked_losses"], [])
        self.ledger.ingest(self.t + 360, 6211, 397, soc_pct=88.5)
        trip = self.ledger.data["active"]
        self.assertAlmostEqual(sum(s["kwh"] for s in trip["segments"]), 0.9)
        self.assertAlmostEqual(trip["segments"][-1]["kwh"], 0.9)
        self.assertEqual(self.ledger.data["parked_losses"], [])

    def test_native_rebound_resolves_without_public_charge_or_blank_trip(self):
        self.ledger.ingest(self.t, 6208, 400, soc_pct=84)
        self.ledger.ingest(self.t + 120, 6212, 396, soc_pct=84.5)
        self.assertIsNone(self.ledger.data["active"]["segments"][0]["kwh"])
        self.ledger.ingest(self.t + 240, 6216, 392, soc_pct=83.5)
        trip = self.ledger.data["active"]
        self.assertTrue(trip["complete"])
        self.assertEqual(self.ledger.data["charges"], {})
        self.assertAlmostEqual(sum(s["kwh"] for s in trip["segments"]), 0.45)
        self.assertAlmostEqual(
            self.ledger.statistics(self.t, self.t + 240)["used_kwh"], 0.45
        )

    def test_native_parked_loss_only_after_trip_closure(self):
        self.ledger.ingest(self.t, 6208, 400, soc_pct=89.5)
        self.ledger.ingest(self.t + 120, 6209, 399, soc_pct=89)
        self.ledger.ingest(self.t + 240, 6209, 399, soc_pct=88.5)
        self.assertEqual(self.ledger.data["parked_losses"], [])
        self.ledger.tick(self.t + 120 + 25 * 60)
        self.assertEqual(len(self.ledger.data["trips"]), 1)
        self.assertAlmostEqual(self.ledger.data["parked_losses"][0]["kwh"], 0.45)
        before = json.loads(json.dumps(self.ledger.data))
        restored = Ledger(self.ledger.settings, before)
        restored.tick(self.t + 3600)
        self.assertEqual(restored.data["parked_losses"], before["parked_losses"])

    def test_native_source_clocks_reconcile_late_arrival_without_late_parked_loss(self):
        ledger = self.ledger
        ledger.observe_native_sources(self.t, 1000, self.t - 10, 52)
        ledger.observe_native_sources(self.t + 120, 1000, self.t + 110, 52)
        # The 51.5% reading is newer than the movement report. It cannot be
        # used as a departure value until a subsequent distance report arrives.
        ledger.observe_native_sources(self.t + 240, 1001, self.t + 260, 51.5)
        ledger.observe_native_sources(self.t + 360, 1002, self.t + 260, 51.5)
        ledger.observe_native_sources(self.t + 360, 1002, self.t + 390, 51)
        ledger.observe_native_sources(self.t + 480, 1002, self.t + 470, 51)
        ledger.observe_native_sources(self.t + 1500, 1002, self.t + 1490, 50.5)
        ledger.tick(self.t + 2100)
        trip = ledger.data["trips"][0]
        self.assertEqual(trip["distance_km"], 2)
        self.assertAlmostEqual(sum(row["kwh"] for row in trip["segments"]), 0.9)
        self.assertAlmostEqual(ledger.data["parked_losses"][0]["kwh"], 0.45)
        self.assertEqual(trip["native_alignment_version"], 2)

    def test_native_alignment_survives_restart_and_duplicate_reports(self):
        ledger = self.ledger
        ledger.observe_native_sources(self.t, 1000, self.t - 10, 52)
        ledger.observe_native_sources(self.t + 120, 1000, self.t + 110, 52)
        restored = Ledger(ledger.settings, json.loads(json.dumps(ledger.data)))
        before = deepcopy(restored.data)
        self.assertFalse(
            restored.observe_native_sources(self.t + 120, 1000, self.t + 110, 52)
        )
        self.assertEqual(restored.data, before)
        restored.observe_native_sources(self.t + 240, 1001, self.t + 230, 51.5)
        self.assertAlmostEqual(restored.data["active"]["segments"][0]["kwh"], 0.45)

    def test_late_native_endpoint_does_not_cross_charge_boundary(self):
        ledger = self.ledger
        ledger.observe_native_sources(self.t, 1000, self.t - 10, 52)
        ledger.observe_native_sources(self.t + 120, 1001, self.t + 110, 51.5)
        trip = ledger.data["active"]
        before = deepcopy(trip)
        ledger.observe_native_sources(
            self.t + 120,
            1001,
            self.t + 140,
            51,
            connected=True,
            connected_since=self.t + 130,
        )
        self.assertEqual(trip, before)

    def test_native_replay_preserves_trip_id_archive_and_raw_samples(self):
        self.ledger.ingest(self.t, 1000, 400, soc_pct=90)
        self.ledger.ingest(self.t + 600, 1001, 399, soc_pct=89.5)
        self.ledger.ingest(self.t + 700, 1001, 398, soc_pct=89)
        self.ledger.ingest(self.t + 800, 1002, 397, soc_pct=89)
        self.ledger.tick(self.t + 2500)
        ident = self.ledger.data["trips"][0]["id"]
        raw = deepcopy(self.ledger.data["samples"])
        self.ledger.data["parked_losses"].append(
            dict(start=self.t + 600, end=self.t + 700, kwh=0.45, complete=True)
        )
        self.ledger.data["charges"]["home-114"] = dict(
            id="home-114",
            kind="home",
            start=self.t - 3600,
            end=self.t - 1800,
            kwh=36.85,
            cost_eur=5.014619,
            confirmed=True,
            category="home",
        )
        reports = [
            dict(t=t, odo=odo, soc_pct=soc, soc_time=t - 10, home_connected=False)
            for t, odo, soc in (
                (self.t, 1000, 90),
                (self.t + 120, 1000, 90),
                (self.t + 600, 1001, 89.5),
                (self.t + 720, 1001, 89),
                (self.t + 840, 1002, 89),
            )
        ]
        self.assertTrue(self.ledger.repair_native_trip(ident, reports, self.t + 3000))
        repaired = self.ledger.data["trips"][0]
        self.assertEqual(repaired["id"], ident)
        self.assertEqual(repaired["start"], self.t + 120)
        self.assertEqual(repaired["distance_km"], 2)
        self.assertEqual(self.ledger.data["parked_losses"], [])
        self.assertEqual(
            self.ledger.data["native_replays"][ident]["superseded_parked_losses"],
            [dict(start=self.t + 600, end=self.t + 700, kwh=0.45, complete=True)],
        )
        self.assertEqual(self.ledger.data["samples"], raw)
        self.assertIn("home-114", self.ledger.data["charges"])
        before = json.loads(json.dumps(self.ledger.data))
        self.assertFalse(self.ledger.repair_native_trip(ident, reports, self.t + 4000))
        self.assertEqual(self.ledger.data, before)

    def test_native_replay_accepts_bounded_predeparture_baseline(self):
        ledger = self.ledger
        ledger.ingest(self.t, 1000, None, soc_pct=52)
        ledger.ingest(self.t + 120, 1000, None, soc_pct=52)
        ledger.ingest(self.t + 240, 1001, None, soc_pct=51.5)
        ledger.tick(self.t + 2000)
        ident = ledger.data["trips"][0]["id"]
        reports = [
            {
                "t": self.t + offset,
                "odo_time": self.t + offset,
                "odo": odo,
                "soc_time": self.t + offset - 10,
                "soc_pct": soc,
                "home_connected": False,
            }
            for offset, odo, soc in ((0, 1000, 52), (120, 1000, 52), (240, 1001, 51.5))
        ]
        self.assertEqual(ledger.data["trips"][0]["start"], self.t + 120)
        self.assertTrue(ledger.repair_native_trip(ident, reports, self.t + 2000))
        self.assertEqual(ledger.data["trips"][0]["id"], ident)
        self.assertAlmostEqual(ledger.data["trips"][0]["segments"][0]["kwh"], 0.45)

    def test_active_home_session_without_completed_history_is_projection_only(self):
        self.ledger.import_home([], active_session_id=115)
        self.assertEqual(self.ledger.data["charges"], {})
        card = provisional_home_charge("home-115", self.t, self.t + 600, 0.46, 0.05, 89)
        self.assertEqual(card["id"], "home-115")
        self.assertTrue(card["ongoing"])
        self.assertAlmostEqual(card["kwh"], 0.46)
        self.assertEqual(self.ledger.data["charges"], {})
        self.ledger.import_home(
            [[115, self.t, self.t + 1200, 2.0, 85, 0.24, 0.645, 0.405]],
            active_session_id=None,
        )
        self.assertEqual(len(self.ledger.data["charges"]), 1)
        self.assertFalse(self.ledger.data["charges"]["home-115"].get("ongoing"))

    def test_late_odometer_tail_stays_in_one_trip_and_legacy_split_can_merge(self):
        # An unchanged-distance SoC report precedes the final odometer tick.
        readings = [
            (self.t, 1000, 80),
            (self.t + 120, 1001, 79.5),
            (self.t + 240, 1002, 79),
            (self.t + 360, 1002, 78.5),
            (self.t + 480, 1003, 78.5),
        ]
        for t, odo, soc in readings:
            self.ledger.ingest(t, odo, None, soc_pct=soc)
        self.ledger.tick(self.t + 2400)
        combined = deepcopy(self.ledger.data["trips"][0])
        self.assertEqual(combined["distance_km"], 3)
        self.assertAlmostEqual(sum(s["kwh"] for s in combined["segments"]), 1.35)

        # Mimic two adjacent, already-archived records from the old adapter.
        primary = deepcopy(combined)
        primary["segments"] = primary["segments"][:-1]
        primary.update(
            end=self.t + 240,
            last_movement=self.t + 240,
            end_odo=1002,
            end_energy=71.1,
            distance_km=2,
        )
        tail = deepcopy(combined)
        tail["id"] = "legacy-false-tail"
        tail["segments"] = [dict(combined["segments"][-1], kwh=None, complete=False)]
        tail.update(
            start=self.t + 360,
            start_odo=1002,
            start_energy=70.65,
            distance_km=1,
            complete=False,
        )
        self.ledger.data["trips"] = [primary, tail]
        raw = deepcopy(self.ledger.data["samples"])
        reports = [
            dict(t=t, odo=odo, soc_pct=soc, soc_time=t - 10, home_connected=False)
            for t, odo, soc in readings
        ]
        self.assertTrue(
            self.ledger.repair_native_trip(
                primary["id"], reports, self.t + 3000, merge_tail_id=tail["id"]
            )
        )
        self.assertEqual(len(self.ledger.data["trips"]), 1)
        repaired = self.ledger.data["trips"][0]
        self.assertEqual(repaired["id"], primary["id"])
        self.assertEqual(repaired["distance_km"], 3)
        self.assertEqual(repaired["end_odo"], 1003)
        self.assertAlmostEqual(sum(s["kwh"] for s in repaired["segments"]), 1.35)
        self.assertEqual(self.ledger.data["samples"], raw)
        before = deepcopy(self.ledger.data)
        self.assertFalse(
            self.ledger.repair_native_trip(
                primary["id"], reports, self.t + 4000, merge_tail_id=tail["id"]
            )
        )
        self.assertEqual(self.ledger.data, before)

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

    def test_pause_then_restart_does_not_create_a_missing_interval(self):
        self.drive()
        self.ledger.close_trip()
        archived = json.loads(json.dumps(self.ledger.data["trips"]))
        self.ledger.begin_new_epoch(self.ledger.settings)
        restored = Ledger(
            self.ledger.settings, json.loads(json.dumps(self.ledger.data))
        )
        restored.ingest(self.t + 86400, 1020, 200)
        self.assertEqual(restored.data["trips"], archived)
        self.assertEqual(restored.data["parked_losses"], [])
        self.assertEqual(restored.data["charges"], {})


if __name__ == "__main__":
    unittest.main()
