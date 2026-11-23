"""Calendar selection preserves the existing ledger calculations (no HA runtime)."""

import importlib.util
import pathlib
import sys
import types
import unittest
from copy import deepcopy
from datetime import UTC, datetime
from zoneinfo import ZoneInfo

ROOT = (
    pathlib.Path(__file__).parents[1] / "custom_components/nio_telematics/car_dashboard"
)
PACKAGE = "nio_period_test"
package = types.ModuleType(PACKAGE)
package.__path__ = [str(ROOT)]
sys.modules[PACKAGE] = package


def load(name):
    spec = importlib.util.spec_from_file_location(
        f"{PACKAGE}.{name}", ROOT / f"{name}.py"
    )
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


periods, ledger_module = load("periods"), load("ledger")
tz = ZoneInfo("Europe/Brussels")


class PeriodTests(unittest.TestCase):
    def test_local_days_follow_dst(self):
        for date, hours in [("2026-03-29", 23), ("2026-10-25", 25)]:
            with self.subTest(date=date):
                window = periods.calendar_window("day", date, tz)
                self.assertEqual(window["end"] - window["start"], hours * 3600)

    def test_week_crosses_year_and_starts_monday(self):
        window = periods.calendar_window("week", "2026-01-01", tz)
        self.assertEqual(
            (window["start_date"], window["end_date"]), ("2025-12-29", "2026-01-05")
        )

    def test_current_date_uses_ha_timezone(self):
        now = datetime(2026, 11, 22, 23, 30, tzinfo=UTC).timestamp()
        self.assertEqual(
            periods.calendar_window("day", None, tz, now)["date"], "2026-11-23"
        )

    def test_invalid_selection(self):
        for scope, date in [
            ("hour", "2026-01-01"),
            ("day", "2026-02-30"),
            ("day", "not-a-date"),
        ]:
            with self.subTest(scope=scope, date=date), self.assertRaises(ValueError):
                periods.calendar_window(scope, date)

    def test_month_and_year_boundaries(self):
        self.assertEqual(
            periods.calendar_window("month", "2026-12-31")["end_date"], "2027-01-01"
        )
        self.assertEqual(
            periods.calendar_window("year", "2024-02-29")["end_date"], "2025-01-01"
        )

    def test_statistics_use_same_ledger_without_mutation(self):
        ledger = ledger_module.Ledger({"capacity_kwh": 90, "full_range_km": 450})
        start = datetime(2026, 11, 23, 8, tzinfo=tz).timestamp()
        ledger.ingest(start, 1000, 250)
        ledger.ingest(start + 600, 1010, 240)
        ledger.ingest(start + 1200, 1020, 230)
        now = start + 3600
        before = deepcopy(ledger.data)
        legacy = ledger.snapshot(now, tz)
        for scope in ("day", "week", "month", "year"):
            window = periods.calendar_window(scope, "2026-11-23", tz, now)
            actual = periods.period_statistics(ledger, window)
            expected = ledger.statistics(window["start"], now)
            for key, value in expected.items():
                self.assertEqual(actual[key], value, (scope, key))
            self.assertIsNone(actual["petrol_saving_eur"])
            if scope != "week":
                self.assertEqual(actual, legacy["statistics"][scope], scope)
        self.assertEqual(ledger.data, before)

    def test_next_midnight_excluded_and_future_clipped_to_now(self):
        now = datetime(2026, 11, 23, 12, tzinfo=tz).timestamp()
        previous = periods.calendar_window("day", "2026-11-22", tz, now)
        current = periods.calendar_window("day", "2026-11-23", tz, now)
        self.assertLess(previous["effective_end"], current["start"])
        self.assertEqual(current["effective_end"], now)


if __name__ == "__main__":
    unittest.main()
