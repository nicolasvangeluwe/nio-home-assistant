"""Durable native-source proof for replayed parked charging value.

All times and quantities beyond the explicitly stated receipt-backed example
are synthetic. These tests cover pure Ledger behavior and need no Home Assistant.
"""

import importlib.util
import json
import pathlib
import sys
import types
import unittest
from copy import deepcopy
from decimal import Decimal as D

LEDGER_ROOT = (
    pathlib.Path(__file__).parents[1]
    / "custom_components"
    / "nio_telematics"
    / "car_dashboard"
)
PACKAGE = types.ModuleType("durable_ledger")
PACKAGE.__path__ = [str(LEDGER_ROOT)]
sys.modules[PACKAGE.__name__] = PACKAGE
SPEC = importlib.util.spec_from_file_location(
    "durable_ledger.ledger", LEDGER_ROOT / "ledger.py"
)
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)
Ledger = MODULE.Ledger


class DurableChargingBasisTests(unittest.TestCase):
    t = 1_795_600_000
    capacity = 90

    def make_ledger(self, opening_kwh=67.51, opening_value=144.71):
        ledger = Ledger(
            {"capacity_kwh": self.capacity, "full_range_km": 557, "currency": "DKK"}
        )
        ledger.preferences(
            {
                "opening_price_eur_kwh": float(D(opening_value) / D(opening_kwh)),
                "currency": "DKK",
            }
        )
        # This same-currency opening stock/value is the known booked basis.
        return ledger

    def observe(self, ledger, seconds, odo, energy, *, soc_time=None):
        at = self.t + seconds
        source_at = at if soc_time is None else self.t + soc_time
        ledger.observe_native_sources(
            at, odo, source_at, energy / self.capacity * 100, False, None
        )

    def receipt_backed_rise(self):
        ledger = self.make_ledger()
        # Reported example: pending priced receipt began before the parked
        # sample and finishes after it. Its quantity/value are credited once.
        ledger.import_home(
            [[71, self.t - 100, self.t + 200, 8.54, 0, 20.65, None, None]]
        )
        self.observe(ledger, -200, 700, 67.51)
        self.observe(ledger, 0, 700, 71.55)
        self.observe(ledger, 100, 700, 71.10)
        self.observe(ledger, 200, 700, 70.65)
        # Post-receipt native START at 70.65 and a synthetic 1.8 kWh trip.
        self.observe(ledger, 400, 700, 70.65)
        self.observe(ledger, 1000, 710, 68.85)
        return ledger

    def test_receipt_backed_rise_opens_original_known_book_pool_once(self):
        ledger = self.receipt_backed_rise()
        rows = ledger.cost_segments()
        pool_kwh = D("67.51") + D("8.54")
        pool_value = D("144.71") + D("20.65")
        self.assertAlmostEqual(float(pool_kwh), 76.05)
        self.assertAlmostEqual(float(pool_value), 165.36)
        self.assertAlmostEqual(
            rows[-1]["cost_eur"], float(D("1.8") * pool_value / pool_kwh)
        )
        self.assertEqual(
            sum(D(str(c["kwh"])) for c in ledger.accounting_charges()), D("8.54")
        )

    def test_native_proof_survives_both_rolling_buffers_and_json_recreation(self):
        ledger = self.receipt_backed_rise()
        before = deepcopy(ledger.data)
        expected = ledger.cost_segments()[-1]["cost_eur"]
        self.assertEqual(
            ledger.data, before, "read replay must not mutate persisted decisions"
        )
        before_saved = json.loads(json.dumps(before))
        before_recreated = Ledger(ledger.settings, before_saved)
        self.assertEqual(before_recreated.cost_segments()[-1]["cost_eur"], expected)
        self.assertEqual(before_recreated.data, before_saved)
        for n in range(1, 2002):
            # Synthetic stationary native readings rotate both 2000-entry
            # report/sample rings while leaving this trip and receipt intact.
            self.observe(ledger, 1000 + n, 710, 68.85)
        self.assertEqual(len(ledger.data["samples"]), 2000)
        self.assertEqual(len(ledger.data["native_soc_reports"]), 2000)
        self.assertEqual(ledger.cost_segments()[-1]["cost_eur"], expected)
        serialized = json.loads(json.dumps(ledger.data))
        recreated = Ledger(ledger.settings, serialized)
        self.assertEqual(recreated.cost_segments()[-1]["cost_eur"], expected)
        self.assertEqual(recreated.data, serialized)

    def test_saved_durable_proof_is_separate_from_diagnostic_ring_contents(self):
        ledger = self.receipt_backed_rise()
        expected = ledger.cost_segments()[-1]["cost_eur"]
        # The permanent proof collection is expected to be persisted in the
        # ledger data; empty diagnostic rings cannot revoke captured proof.
        self.assertTrue(ledger.data.get("native_cost_anchors"))
        ledger.data["native_soc_reports"] = []
        ledger.data["samples"] = []
        self.assertEqual(ledger.cost_segments()[-1]["cost_eur"], expected)

    def test_legacy_archive_requires_full_180_second_source_interval(self):
        ledger = self.legacy_resume_fixture()
        # Emulate development-11 archives: remove the new permanent anchors
        # and any sample-level source timestamp. The retained source report
        # only proves a selected source time in [sample.t - 180, sample.t].
        ledger.data.pop("native_cost_anchors", None)
        for sample in ledger.data["samples"]:
            sample.pop("native_source_time", None)
        # Old report times and sample source metadata were not both retained
        # by every development-11 archive. Migration must conservatively use
        # the native sample's full [t-180,t] source interval.
        ledger.data["native_soc_reports"] = []
        recreated = Ledger(ledger.settings, json.loads(json.dumps(ledger.data)))
        self.assertIsNone(recreated.cost_segments()[0]["cost_eur"])

    def legacy_resume_fixture(self):
        ledger = self.make_ledger()
        ledger.import_home(
            [[71, self.t - 100, self.t + 200, 8.54, 0, 20.65, None, None]]
        )
        self.observe(ledger, -200, 700, 67.51)
        self.observe(ledger, 0, 700, 71.55)
        self.observe(ledger, 100, 700, 71.10)
        self.observe(ledger, 200, 700, 70.65)
        # START +312 is 112 seconds after receipt end. A known-energy 0.9kWh
        # trip follows; the independent later START is +600.
        self.observe(ledger, 312, 700, 70.65)
        self.observe(ledger, 412, 705, 69.75)
        self.observe(ledger, 600, 705, 69.75)
        self.observe(ledger, 1200, 715, 67.95)
        return ledger

    def test_legacy_late_proof_resumes_after_known_unpriced_native_trip(self):
        ledger = self.legacy_resume_fixture()
        ledger.data.pop("native_cost_anchors", None)
        for sample in ledger.data["samples"]:
            sample.pop("native_source_time", None)
        ledger.data["native_soc_reports"] = []
        ledger = Ledger(ledger.settings, json.loads(json.dumps(ledger.data)))
        segments = ledger.cost_segments()
        self.assertIsNone(segments[0]["cost_eur"])
        # Retire the preceding known 0.9kWh at the original weighted book
        # price, but do not backfill its missing cost. Later independent START
        # can price only its own 1.8kWh from the remaining pool.
        pool_kwh = D("76.05") - D("0.9")
        pool_value = D("165.36") - D("0.9") * D("165.36") / D("76.05")
        self.assertAlmostEqual(
            segments[-1]["cost_eur"], float(D("1.8") * pool_value / pool_kwh)
        )
        self.assertIsNone(
            segments[0]["cost_eur"], "late evidence must not retroprice earlier trip"
        )

    def test_unknown_intervening_energy_prevents_later_resume(self):
        ledger = self.legacy_resume_fixture()
        ledger.data.pop("native_cost_anchors", None)
        for sample in ledger.data["samples"]:
            sample.pop("native_source_time", None)
        ledger.data["native_soc_reports"] = []
        ledger = Ledger(ledger.settings, json.loads(json.dumps(ledger.data)))
        first_trip = ledger.all_trips()[0]
        first_trip["segments"][0]["kwh"] = None
        first_trip["segments"][0]["end_energy"] = None
        self.assertIsNone(ledger.cost_segments()[-1]["cost_eur"])

    def test_later_same_value_report_corroborates_legacy_start_source_clock(self):
        ledger = self.make_ledger()
        ledger.import_home(
            [[71, self.t - 100, self.t + 200, 8.54, 0, 20.65, None, None]]
        )
        self.observe(ledger, -200, 700, 67.51)
        self.observe(ledger, 0, 700, 71.55)
        self.observe(ledger, 100, 700, 71.10)
        # START sample at +312 was initially paired to SoC report +150.
        self.observe(ledger, 312, 700, 70.65, soc_time=150)
        # A repeated odometer timestamp carries a distinct same-valued report
        # at +250, legitimately after receipt completion (+200).
        ledger.observe_native_sources(
            self.t + 312, 700, self.t + 250, 70.65 / self.capacity * 100, False, None
        )
        self.observe(ledger, 412, 710, 68.85)
        ledger.data.pop("native_cost_anchors", None)
        for sample in ledger.data["samples"]:
            sample.pop("native_source_time", None)
        migrated = Ledger(ledger.settings, json.loads(json.dumps(ledger.data)))
        self.assertIsNotNone(migrated.cost_segments()[-1]["cost_eur"])

    def test_legacy_charging_loss_without_guard_remains_unknown_after_ring_expiry(self):
        ledger = self.receipt_backed_rise()
        expected = ledger.cost_segments()[-1]["cost_eur"]
        for loss in ledger.data["parked_losses"]:
            loss.pop("allocation_guard", None)
        raw_losses = deepcopy(ledger.data["parked_losses"])
        ledger.data.pop("native_cost_anchors", None)
        for sample in ledger.data["samples"]:
            sample.pop("native_source_time", None)
        ledger = Ledger(ledger.settings, json.loads(json.dumps(ledger.data)))
        ledger.classify_recorded_intervals()
        self.assertEqual(ledger.data["parked_losses"], raw_losses)
        self.assertTrue(
            any(
                row["accounting_basis"] == "charging_boundary" and row["kwh"] == 0
                for row in ledger.unaccounted_parked_intervals()
            )
        )
        for n in range(1, 2002):
            self.observe(ledger, 1000 + n, 710, 68.85)
        self.assertEqual(ledger.cost_segments()[-1]["cost_eur"], expected)
        self.assertEqual(ledger.data["parked_losses"], raw_losses)
        self.assertTrue(
            any(
                row["accounting_basis"] == "charging_boundary" and row["kwh"] == 0
                for row in ledger.unaccounted_parked_intervals()
            )
        )

    def test_permanent_start_proof_projects_raw_pause_energy_without_rewriting(self):
        ledger = self.legacy_resume_fixture()
        trip = ledger.all_trips()[0]
        second = trip["segments"][1]
        # Development-11 may carry the later idle energy (69.3) as the raw
        # second-segment start, despite that row starting at +412 when the
        # matching permanent native sample measured 69.75. End + consumption
        # independently projects the same 69.75 book endpoint.
        second.update(kwh=2.25, start_energy=69.3, end_energy=67.5)
        raw = deepcopy(ledger.data)
        rows = ledger.cost_segments()
        pool_kwh = D("76.05") - D("0.9")
        pool_value = D("165.36") - D("0.9") * D("165.36") / D("76.05")
        self.assertAlmostEqual(
            rows[-1]["cost_eur"], float(D("2.25") * pool_value / pool_kwh)
        )
        self.assertEqual(
            ledger.data, raw, "read projection must preserve legacy segment facts"
        )

    def test_unknown_energy_and_source_or_capacity_boundary_block_resume(self):
        for change in ("unknown", "source", "capacity"):
            with self.subTest(change=change):
                ledger = self.receipt_backed_rise()
                if change == "unknown":
                    ledger.all_trips()[0]["segments"][0]["kwh"] = None
                elif change == "source":
                    ledger.data["source_transitions"].append(
                        {
                            "t": self.t + 350,
                            "energy": 70.65,
                            "capacity_kwh": self.capacity,
                        }
                    )
                else:
                    ledger.data["source_transitions"].append(
                        {"t": self.t + 350, "energy": 70.65, "capacity_kwh": 75}
                    )
                self.assertIsNone(ledger.cost_segments()[-1]["cost_eur"])

    def test_unpriced_foreign_ongoing_and_candidate_receipts_cannot_open_pool(self):
        for patch in (
            {"cost_eur": None},
            {"currency": "EUR"},
            {"ongoing": True},
            {"kind": "candidate"},
            {"confirmed": False},
        ):
            with self.subTest(patch=patch):
                ledger = self.receipt_backed_rise()
                ledger.data["charges"]["home-71"].update(patch)
                self.assertIsNone(ledger.cost_segments()[-1]["cost_eur"])


if __name__ == "__main__":
    unittest.main()
