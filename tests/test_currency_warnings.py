"""Currency migration advisories retain the source/default monetary contract."""

import importlib
import sys
import types
import unittest
from copy import deepcopy
from pathlib import Path

ROOT = Path(__file__).parents[1] / "custom_components/nio_telematics/car_dashboard"
package = types.ModuleType("currency_warning_ledger")
package.__path__ = [str(ROOT)]
sys.modules[package.__name__] = package
Ledger = importlib.import_module(package.__name__ + ".ledger").Ledger
warning = importlib.import_module(
    package.__name__ + ".currency_warnings"
).history_currency_warning


def make_ledger(currency, data=None):
    return Ledger(
        {"currency": currency, "capacity_kwh": 90, "full_range_km": 557}, data
    )


class CurrencyWarningTests(unittest.TestCase):
    def migration(self):
        old = make_ledger("EUR")
        old.import_home([[1, 100, 200, 10, 0, 7.42, 0, 0]], currency="EUR")
        return make_ledger("DKK", old.data)

    def test_old_converted_source_then_actual_dkk_requires_metadata_notice(self):
        ledger = self.migration()
        before = deepcopy(ledger.data)
        result = warning(ledger, {"unit_of_measurement": "kWh"}, "Amina history")
        self.assertEqual(result["currency"], "DKK")
        self.assertEqual(result["previous_currencies"], ["EUR"])
        self.assertEqual(result["source"], "Amina history")
        self.assertEqual(ledger.data, before)
        # The notice is not a guessed exchange rate or a changed default.
        ledger.import_home([[2, 300, 400, 10, 0, 7.42, 0, 0]])
        self.assertEqual(ledger.data["charges"]["home-2"]["cost_eur"], 7.42)
        self.assertEqual(ledger.data["charges"]["home-2"]["currency"], "DKK")
        self.assertIsNotNone(warning(ledger, {"sessions": []}, "Amina history"))
        ledger.import_home([[2, 300, 400, 10, 0, 55.32, 0, 0]], currency="DKK")
        self.assertEqual(ledger.data["charges"]["home-2"]["cost_eur"], 55.32)
        self.assertIsNone(warning(ledger, {"currency": "DKK"}, "Amina history"))
        self.assertEqual(ledger.data["charges"]["home-1"]["currency"], "EUR")

    def test_explicit_source_currency_suppresses_assumption_notice(self):
        for attributes in (
            {"currency": "DKK"},
            {"currency": "EUR"},
            {"unit_of_measurement": "dkk"},
        ):
            with self.subTest(attributes=attributes):
                self.assertIsNone(warning(self.migration(), attributes, "History"))

    def test_new_install_and_manual_foreign_receipts_are_not_migration_evidence(self):
        ledger = make_ledger("DKK")
        self.assertIsNone(warning(ledger, {"sessions": []}, "History"))
        ledger.add_charge(100, 200, 10, price=0.2, currency="EUR")
        self.assertIsNone(warning(ledger, {"sessions": []}, "History"))
        ledger.import_home([[1, 100, 200, 10, 0, 55.32, 0, 0]], currency="DKK")
        self.assertIsNone(warning(ledger, {"sessions": []}, "History"))

    def test_unpriced_old_energy_and_unavailable_source_are_not_unit_evidence(self):
        ledger = make_ledger("DKK")
        ledger.import_home([[1, 100, 200, 10, 0, None, None, None]], currency="EUR")
        self.assertIsNone(warning(ledger, {"sessions": []}, "History"))
        self.assertIsNone(warning(self.migration(), None, "History"))
        self.assertIsNone(warning(self.migration(), {}, "History"))
        self.assertIsNone(warning(self.migration(), {"sessions": []}, ""))

    def test_invalid_explicit_units_are_not_misreported_as_undeclared(self):
        for attributes in (
            {"unit_of_measurement": "$"},
            {"currency": "?"},
            {"currency": "DKK", "unit_of_measurement": "EUR"},
        ):
            with self.subTest(attributes=attributes):
                self.assertIsNone(warning(self.migration(), attributes, "History"))

    def test_reverse_currency_change_is_also_an_evidenced_assumption(self):
        ledger = make_ledger("EUR")
        ledger.import_home([[1, 100, 200, 10, 0, 55.32, 0, 0]], currency="DKK")
        result = warning(ledger, {"unit_of_measurement": "sessions"}, "History")
        self.assertEqual(result["currency"], "EUR")
        self.assertEqual(result["previous_currencies"], ["DKK"])


if __name__ == "__main__":
    unittest.main()
