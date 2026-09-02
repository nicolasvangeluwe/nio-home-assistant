"""Tests for verified NIO payload parsing."""

from datetime import UTC, datetime
import unittest

from _load import load_module

models = load_module("models")


class TestNioModels(unittest.TestCase):
    def test_soc_status_parses_verified_fields(self) -> None:
        status = models.NioSocStatus.from_payload(
            {
                "soc": 51,
                "remaining_range": 204.5,
                "chrg_state": "charging",
                "chrg_final_soc": 80,
                "max_soc": 90,
                "hivolt_btry_curnt": -12.25,
                "sample_timestamp": 1_760_000_000_000,
            }
        )
        self.assertEqual(status.soc, 51.0)
        self.assertEqual(status.remaining_range, 204.5)
        self.assertEqual(status.charging_state, "charging")
        self.assertEqual(status.charging_target, 80.0)
        self.assertEqual(status.maximum_soc, 90.0)
        self.assertEqual(status.high_voltage_battery_current, -12.25)
        self.assertEqual(
            status.event_time, datetime.fromtimestamp(1_760_000_000, tz=UTC)
        )

    def test_invalid_optional_fields_are_none(self) -> None:
        status = models.NioSocStatus.from_payload(
            {"soc": "unknown", "chrg_state": "", "sample_timestamp": None}
        )
        self.assertIsNone(status.soc)
        self.assertIsNone(status.remaining_range)
        self.assertIsNone(status.charging_state)
        self.assertIsNone(status.event_time)

    def test_numeric_enum_is_normalized_to_string(self) -> None:
        status = models.NioSocStatus.from_payload({"chrg_state": 3})

        self.assertEqual(status.charging_state, "3")

    def test_event_time_accepts_milliseconds(self) -> None:
        status = models.NioSocStatus.from_payload(
            {"sample_timestamp": 1_760_000_000_000}
        )
        self.assertEqual(
            status.event_time, datetime.fromtimestamp(1_760_000_000, tz=UTC)
        )

    def test_merge_keeps_newest_available_value_for_each_field(self) -> None:
        newest = models.NioSocStatus.from_payload(
            {"soc": 51, "sample_timestamp": 1_760_000_100_000}
        )
        older = models.NioSocStatus.from_payload(
            {
                "remaining_range": 204.5,
                "chrg_final_soc": 80,
                "sample_timestamp": 1_760_000_000_000,
            }
        )

        status = models.NioSocStatus.merge(newest, older)

        self.assertEqual(status.soc, 51)
        self.assertEqual(status.remaining_range, 204.5)
        self.assertEqual(status.charging_target, 80)
        self.assertEqual(status.event_time, newest.event_time)

    def test_vin_normalization(self) -> None:
        self.assertEqual(models.normalize_vin("  ljnabc12345678901 "), "LJNABC12345678901")

    def test_invalid_vin_is_rejected(self) -> None:
        for vin in ("short", "LJNABC1234567890I", "LJNABC1234567890O"):
            with self.subTest(vin=vin), self.assertRaises(ValueError):
                models.normalize_vin(vin)
