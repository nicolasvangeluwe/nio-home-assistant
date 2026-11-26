"""Deferred periodic booked allocation; no physical mixing or tariff inference."""

import unittest
from copy import deepcopy
from decimal import Decimal as D

from custom_components.nio_telematics.car_dashboard.ledger import Ledger


class DeferredChargingBasisTests(unittest.TestCase):
    t = 1795534000.0

    def fixture(
        self,
        capacity=90,
        opening=50.85,
        ending=50.4,
        after=74.843,
        receipts=None,
        start=4300,
    ):
        # Capacity90/75, opening price2 and post-session endpoints are synthetic;
        # they are not asserted reporter specifications or observed tariffs.
        ledger = Ledger(
            {"capacity_kwh": capacity, "full_range_km": 557, "currency": "DKK"}
        )
        ledger.preferences({"opening_price_eur_kwh": 2})
        receipts = receipts or [(1, 120, 4200, 24.443, 55.32)]
        ledger.import_home(
            [
                [ident, self.t + a, self.t + b, kwh, 0, cost, None, None]
                for ident, a, b, kwh, cost in receipts
            ]
        )

        def observe(at, odo, energy, connected=False):
            ledger.observe_native_sources(
                self.t + at,
                odo,
                self.t + at,
                energy / capacity * 100,
                connected,
                self.t + 120 if connected else self.t + 4200,
            )

        observe(0, 705, opening)
        observe(3000, 706, ending, True)
        observe(start, 706, after)
        observe(start + 600, 716, after - 1.8)
        return ledger

    def test_future_session_settles_at_own_later_start_and_preserves_unknown_arrival(
        self,
    ):
        ledger = self.fixture()
        original = deepcopy(ledger.data)
        rows = ledger.cost_segments()
        self.assertIsNone(rows[0]["kwh"])
        self.assertIsNone(rows[0]["cost_eur"])
        self.assertEqual(rows[0]["km"], 1)
        price = (D("50.85") * 2 + D("55.32")) / (D("50.85") + D("24.443"))
        self.assertAlmostEqual(rows[-1]["cost_eur"], float(D("1.8") * price))
        self.assertEqual(ledger.data, original)
        self.assertEqual(
            ledger.statistics(0, self.t + 6000)["unaccounted_distance_km"], 1
        )

    def test_nominal_pool_exceeds_capacity_without_clipping_receipt_energy(self):
        for capacity, opening, quantity in ((90, 80, 85), (75, 70, 65)):
            with self.subTest(capacity=capacity):
                receipts = [(1, 120, 1800, 20, 20), (2, 1860, 4200, 20, 60)]
                ledger = self.fixture(
                    capacity, opening, opening - 5, quantity, receipts
                )
                nominal = D(str(opening)) + 40
                value = D(str(opening)) * 2 + 80
                self.assertGreater(nominal, D(capacity))
                self.assertAlmostEqual(
                    ledger.cost_segments()[-1]["cost_eur"],
                    float(D("1.8") * value / nominal),
                )
                self.assertEqual(
                    sum(c["kwh"] for c in ledger.data["charges"].values()), 40
                )

    def test_wall_input_and_concurrent_withdrawal_retire_quantity_proportionally(self):
        # A hypothetical5kWh@4DKK prefix and5.45kWh withdrawal still yield the
        # SAME50.85->50.40 endpoints. Full receipt24.443/55.32 is booked once.
        # The later observed69.843 stock prevents adding that prefix twice.
        for quantity in (69.843, 72.0):
            with self.subTest(quantity=quantity):
                ledger = self.fixture(after=quantity)
                pool = D("50.85") + D("24.443")
                value = D("101.7") + D("55.32")
                q = D(str(quantity))
                retired = (pool - q) * value / pool
                self.assertEqual(retired + q * value / pool, value)
                self.assertAlmostEqual(
                    ledger.cost_segments()[-1]["cost_eur"],
                    float(D("1.8") * value / pool),
                )
                # A later receipt uses the measured remaining stock, not the
                # uncapped nominal pool or a wall-energy/battery conversion.
                ledger.import_home(
                    [[2, self.t + 5100, self.t + 5400, 5, 0, 20, None, None]]
                )
                ledger.observe_native_sources(
                    self.t + 5500,
                    716,
                    self.t + 5500,
                    (quantity - 1.8 + 5) / 90 * 100,
                    False,
                    self.t + 5400,
                )
                ledger.observe_native_sources(
                    self.t + 6100,
                    726,
                    self.t + 6100,
                    (quantity - 1.8 + 5 - 1.8) / 90 * 100,
                    False,
                    self.t + 5400,
                )
                expected = (
                    ((q - D("1.8")) * value / pool + 20) / (q - D("1.8") + 5) * D("1.8")
                )
                self.assertAlmostEqual(
                    ledger.cost_segments()[-1]["cost_eur"], float(expected)
                )

    def test_unpriced_foreign_candidate_ongoing_source_and_endpoint_guards(self):
        for update in (
            {"cost_eur": None},
            {"currency": "EUR"},
            {"confirmed": False},
            {"kind": "candidate"},
            {"ongoing": True},
        ):
            with self.subTest(update=update):
                ledger = self.fixture()
                ledger.data["charges"]["home-1"].update(update)
                self.assertIsNone(ledger.cost_segments()[-1]["cost_eur"])
        ledger = self.fixture()
        ledger.data["source_transitions"].append(
            {"t": self.t + 3500, "energy": 50, "capacity_kwh": 75}
        )
        self.assertIsNone(ledger.cost_segments()[-1]["cost_eur"])
        ledger = self.fixture(after=80)  # Above nominal75.293, still under90.
        self.assertIsNone(ledger.cost_segments()[-1]["cost_eur"])
        ledger = self.fixture()
        ledger.data["preferences"]["opening_price_eur_kwh"] = None
        self.assertIsNone(ledger.cost_segments()[-1]["cost_eur"])
        ledger = self.fixture()
        ledger.data["charges"]["other"] = {
            "id": "other",
            "kind": "home",
            "start": self.t + 3100,
            "end": self.t + 4150,
            "kwh": 1,
            "cost_eur": None,
            "confirmed": True,
            "currency": "DKK",
            "ongoing": True,
        }
        self.assertIsNone(ledger.cost_segments()[-1]["cost_eur"])

    def test_start_endpoint_is_required_and_no_intervening_drive_can_be_backpriced(
        self,
    ):
        for start, can_price in ((4200, True), (4199, False)):
            with self.subTest(start=start):
                ledger = self.fixture(start=start)
                if can_price:
                    self.assertIsNotNone(ledger.cost_segments()[-1]["cost_eur"])
                else:
                    self.assertIsNone(ledger.cost_segments()[-1]["cost_eur"])
        ledger = self.fixture()
        ledger.data["samples"] = [
            s for s in ledger.data["samples"] if s["t"] != self.t + 4300
        ]
        ledger.data["native_cost_anchors"] = [
            p
            for p in ledger.data["native_cost_anchors"]
            if p["observed_at"] != self.t + 4300
        ]
        self.assertIsNone(ledger.cost_segments()[-1]["cost_eur"])
        ledger = self.fixture()
        for proof in ledger.data["native_cost_anchors"]:
            if proof["observed_at"] == self.t + 4300:
                proof["source_from"] = proof["source_until"] = self.t + 4199
        # Odometer START after receipt end with energy's own source clock
        # before receipt end is not independent post-settlement stock evidence.
        self.assertIsNone(ledger.cost_segments()[-1]["cost_eur"])
        ledger = self.fixture(start=4100)
        ledger.observe_native_sources(
            self.t + 5500,
            726,
            self.t + 5500,
            (74.843 - 3.6) / 90 * 100,
            False,
            self.t + 4200,
        )
        self.assertIsNone(ledger.cost_segments()[-1]["cost_eur"])
