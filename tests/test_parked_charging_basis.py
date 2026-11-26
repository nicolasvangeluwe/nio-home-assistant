"""Complete stationary/arrival/receipt replay; all quantities are example data."""

import json
import unittest
from copy import deepcopy
from decimal import Decimal as D

from custom_components.nio_telematics.car_dashboard.ledger import Ledger


class ParkedChargingBasisTests(unittest.TestCase):
    t = 1795500000

    def observe(self, ledger, seconds, odo, energy, connected=False):
        ledger.observe_native_sources(
            self.t + seconds,
            odo,
            self.t + seconds,
            energy / 90 * 100,
            connected,
            None,
        )

    def fixture(self, arrival=False, post_park=False, second_receipt=False):
        ledger = Ledger({"capacity_kwh": 90, "full_range_km": 557, "currency": "DKK"})
        ledger.preferences({"opening_price_eur_kwh": 2})
        ledger.import_home([[1, self.t + 100, self.t + 1000, 10, 0, 40, None, None]])
        for at, energy in ((0, 50), (100, 50), (200, 49.55), (300, 49.1)):
            self.observe(ledger, at, 700, energy)
        odo = 700
        if arrival:
            odo = 701
            self.observe(ledger, 800, odo, 48.65, True)
        energy = 58.65 if arrival else 59.1
        self.observe(ledger, 1000, odo, energy)
        if second_receipt:
            ledger.import_home([[2, self.t + 1050, self.t + 1100, 5, 0, 5, None, None]])
            energy += 5
            self.observe(ledger, 1100, odo, energy)
        self.observe(ledger, 1200, odo, energy)
        if post_park:
            energy -= 0.45
            self.observe(ledger, 1300, odo, energy)
        self.observe(ledger, 1800, odo + 10, energy - 1.8)
        return ledger

    def expected(self, second_receipt=False):
        stock = D(50) + 10 + (5 if second_receipt else 0)
        value = D(100) + 40 + (5 if second_receipt else 0)
        return float(D("1.8") * value / stock)

    def test_repeated_parked_rows_do_not_erase_or_double_credit_basis(self):
        ledger = self.fixture()
        before = deepcopy(ledger.data)
        self.assertEqual(len(ledger.unaccounted_parked_intervals()), 2)
        self.assertAlmostEqual(ledger.cost_segments()[-1]["cost_eur"], self.expected())
        stats = ledger.statistics(self.t, self.t + 2000)
        self.assertEqual(stats["cost_distance_km"], 10)
        self.assertAlmostEqual(
            sum(r["recorded_kwh"] for r in ledger.unaccounted_parked_intervals()), 0.9
        )
        self.assertEqual(ledger.data, before)

    def test_parked_then_arrival_keeps_missing_usage_unknown(self):
        ledger = self.fixture(arrival=True)
        rows = ledger.cost_segments()
        self.assertEqual(rows[0]["km"], 1)
        self.assertIsNone(rows[0]["kwh"])
        self.assertIsNone(rows[0]["cost_eur"])
        self.assertAlmostEqual(rows[-1]["cost_eur"], self.expected())
        self.assertEqual(
            ledger.statistics(self.t, self.t + 2000)["unaccounted_distance_km"], 1
        )

    def test_native_parked_start_can_settle_before_departure(self):
        ledger = self.fixture(post_park=True)
        self.assertAlmostEqual(ledger.cost_segments()[-1]["cost_eur"], self.expected())
        self.assertAlmostEqual(
            sum(r["kwh"] for r in ledger.accounting_parked_losses()), 0.45
        )

    def test_consecutive_receipts_credit_once_at_different_prices(self):
        ledger = self.fixture(second_receipt=True)
        self.assertAlmostEqual(
            ledger.cost_segments()[-1]["cost_eur"], self.expected(True)
        )
        self.assertEqual(sum(c["cost_eur"] for c in ledger.accounting_charges()), 45)

    def test_boundary_inside_second_priced_receipt_extends_pending_pool(self):
        ledger = Ledger({"capacity_kwh": 90, "full_range_km": 557, "currency": "DKK"})
        ledger.preferences({"opening_price_eur_kwh": 2})
        ledger.import_home(
            [
                [1, self.t + 100, self.t + 1000, 10, 0, 40, None, None],
                [2, self.t + 1050, self.t + 1150, 5, 0, 5, None, None],
            ]
        )
        for at, energy in (
            (0, 50),
            (100, 50),
            (200, 49.55),
            (300, 49.1),
            (1000, 59.1),
            (1050, 59.1),
            (1100, 58.65),
            (1150, 63.65),
            (1200, 63.65),
        ):
            self.observe(ledger, at, 700, energy)
        self.observe(ledger, 1800, 710, 61.85)
        self.assertEqual(len(ledger.unaccounted_parked_intervals()), 3)
        self.assertAlmostEqual(
            ledger.cost_segments()[-1]["cost_eur"], self.expected(True)
        )

    def test_native_save_recreate_and_exact_text_preserve_raw_history(self):
        ledger = self.fixture(arrival=True, post_park=True)
        original = deepcopy(ledger.data)
        for data in (deepcopy(original), json.loads(json.dumps(original))):
            recreated = Ledger(ledger.settings, data)
            self.assertAlmostEqual(
                recreated.cost_segments()[-1]["cost_eur"], self.expected()
            )
            self.assertEqual(recreated.data, original)

    def test_unpriced_foreign_candidate_ongoing_unknown_basis_block_recovery(self):
        for patch in (
            {"cost_eur": None},
            {"currency": "EUR"},
            {"kind": "candidate"},
            {"confirmed": False},
            {"ongoing": True},
        ):
            with self.subTest(patch=patch):
                ledger = self.fixture()
                ledger.data["charges"]["home-1"].update(patch)
                self.assertIsNone(ledger.cost_segments()[-1]["cost_eur"])
        ledger = self.fixture()
        ledger.data["preferences"]["opening_price_eur_kwh"] = None
        self.assertIsNone(ledger.cost_segments()[-1]["cost_eur"])

    def test_missing_or_pre_receipt_native_start_and_source_change_block_recovery(self):
        for mutation in ("samples", "reports", "transition", "above_pool"):
            with self.subTest(mutation=mutation):
                ledger = self.fixture()
                if mutation == "samples":
                    ledger.data["samples"] = [
                        s for s in ledger.data["samples"] if s["t"] != self.t + 1200
                    ]
                elif mutation == "reports":
                    for report in ledger.data["native_soc_reports"]:
                        report["t"] = min(report["t"], self.t + 999)
                elif mutation == "transition":
                    ledger.data["source_transitions"].append(
                        {"t": self.t + 900, "energy": 50, "capacity_kwh": 75}
                    )
                else:
                    for trip in ledger.all_trips():
                        for row in trip["segments"]:
                            row["start_energy"] = 70
                self.assertIsNone(ledger.cost_segments()[-1]["cost_eur"])

    def test_second_intervening_drive_cannot_join_arrival_pool(self):
        ledger = self.fixture(arrival=True)
        # Move the valid following trip before completion of the receipt.
        ledger.data["charges"]["home-1"]["end"] = self.t + 2000
        self.assertIsNone(ledger.cost_segments()[-1]["cost_eur"])
