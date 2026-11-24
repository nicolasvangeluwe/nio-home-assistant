"""Accounting outcomes: preserved currency meaning and booked-price continuity."""

import asyncio
import importlib.util
import json
import pathlib
import sys
import types
import unittest
from copy import deepcopy
from types import SimpleNamespace
from unittest.mock import AsyncMock, Mock, patch

ROOT = pathlib.Path(__file__).parents[1] / "custom_components" / "nio_telematics"
package = types.ModuleType("accounting_ledger")
package.__path__ = [str(ROOT / "car_dashboard")]
sys.modules[package.__name__] = package
spec = importlib.util.spec_from_file_location(
    "accounting_ledger.ledger", ROOT / "car_dashboard" / "ledger.py"
)
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)
Ledger = module.Ledger


class AccountingTests(unittest.TestCase):
    t = 1791540000

    def ledger(self, currency="EUR", data=None):
        return Ledger(
            {"capacity_kwh": 90, "full_range_km": 450, "currency": currency}, data
        )

    def native_gap(self, price=0.3, end_soc=86):
        ledger = self.ledger()
        if price is not None:
            ledger.preferences({"opening_price_eur_kwh": price})
        for dt, odo, soc in (
            (0, 1000, 90),
            (600, 1010, 88),
            (4200, 1020, end_soc),
            (4800, 1030, end_soc - 2),
        ):
            ledger.ingest(self.t + dt, odo, None, soc_pct=soc)
        return ledger

    def test_native_gap_is_skipped_and_later_energy_keeps_existing_booked_price(self):
        ledger = self.native_gap()
        before = deepcopy(ledger.data)
        rows = ledger.cost_segments()
        self.assertIsNone(rows[1]["kwh"])
        self.assertIsNone(rows[1]["cost_eur"])
        self.assertAlmostEqual(rows[2]["kwh"], 1.8)
        self.assertAlmostEqual(rows[2]["cost_eur"], 0.54)
        self.assertNotIn("cost_estimated", rows[2])
        stat = ledger.snapshot(self.t + 4800)["statistics"]["month"]
        self.assertAlmostEqual(stat["used_kwh"], 3.6)
        self.assertEqual(stat["consumption_distance_km"], 20)
        self.assertAlmostEqual(stat["driving_cost_eur"], 1.08)
        self.assertNotIn("cost_estimated", stat)
        self.assertFalse(stat["energy_complete"])
        self.assertFalse(stat["cost_complete"])
        self.assertAlmostEqual(
            ledger.snapshot(self.t + 4800)["counters"][0]["statistics"][
                "driving_cost_eur"
            ],
            1.08,
        )
        self.assertEqual(before, ledger.data)
        restored = self.ledger(data=json.loads(json.dumps(ledger.data)))
        self.assertEqual(restored.cost_segments(), rows)

    def test_unknown_opening_and_rising_gap_remain_unpriced_but_zero_is_valid(self):
        for ledger in (self.native_gap(None), self.native_gap(end_soc=89)):
            self.assertIsNone(ledger.cost_segments()[-1]["cost_eur"])
        zero = self.native_gap(0).cost_segments()[-1]
        self.assertEqual(zero["cost_eur"], 0)

    def test_late_overlapping_charge_and_source_boundary_prevent_recovery(self):
        for source_boundary in (False, True):
            ledger = self.native_gap()
            if source_boundary:
                ledger.data["source_transitions"].append(
                    {"t": self.t + 1800, "energy": 78, "capacity_kwh": 90}
                )
            else:
                ledger.add_charge(self.t + 1000, self.t + 2000, 1, receipt=0.3)
            self.assertIsNone(ledger.cost_segments()[-1]["cost_eur"])

    def test_legacy_anchor_overlap_excluded_only_in_derived_native_view(self):
        ledger = self.native_gap()
        raw = ledger.data["active"]["segments"][-1]
        raw["kwh"] = 3.6  # Signature produced by the former pre-gap anchor.
        before = deepcopy(ledger.data)
        projected = ledger.snapshot(self.t + 4800)
        self.assertEqual(
            projected["driving_segments"][-1]["invalid_reason"], "legacy_gap_overlap"
        )
        self.assertIsNone(projected["driving_segments"][-1]["kwh"])
        self.assertIsNone(projected["trips"][0]["segments"][-1]["kwh"])
        self.assertEqual(ledger.data, before)
        # Other native asynchrony is not a sufficient exclusion signature.
        raw["kwh"] = 2.1
        self.assertEqual(ledger.cost_segments()[-1]["kwh"], 2.1)

    def test_independent_reference_gap_then_two_charges(self):
        ledger = self.ledger()
        ledger.preferences({"opening_price_eur_kwh": 0.3})
        ledger.data["opening"] = {"t": self.t, "energy": 71.55}
        ledger.data["trips"] = [
            {
                "id": "reference",
                "start": self.t,
                "end": self.t + 600,
                "segments": [
                    {
                        "start": self.t,
                        "end": self.t + 100,
                        "km": 10,
                        "kwh": None,
                        "complete": False,
                        "invalid_reason": "gap",
                        "start_energy": 71.55,
                        "end_energy": 60.3,
                    },
                    {
                        "start": self.t + 400,
                        "end": self.t + 500,
                        "km": 10,
                        "kwh": 2,
                        "complete": True,
                        "start_energy": 84.2,
                        "end_energy": 82.2,
                    },
                    {
                        "start": self.t + 500,
                        "end": self.t + 600,
                        "km": 25,
                        "kwh": 5,
                        "complete": True,
                        "start_energy": 82.2,
                        "end_energy": 77.2,
                    },
                ],
            }
        ]
        ledger.add_charge(self.t + 150, self.t + 200, 12, price=0.2)
        ledger.add_charge(self.t + 250, self.t + 300, 11.9, price=0.4)
        rows = ledger.cost_segments()
        self.assertIsNone(rows[0]["kwh"])
        self.assertIsNone(rows[0]["cost_eur"])
        self.assertAlmostEqual(rows[1]["cost_eur"], 0.5997624703087886)
        self.assertAlmostEqual(rows[2]["cost_eur"], 1.4994061757719715)
        # Missing charging price cannot acquire the carried historical rate.
        next(iter(ledger.data["charges"].values()))["cost_eur"] = None
        self.assertIsNone(ledger.cost_segments()[1]["cost_eur"])

    def test_mixed_currency_keeps_energy_but_never_combines_amounts(self):
        ledger = self.ledger("DKK")
        euro = ledger.add_charge(self.t, self.t + 60, 10, receipt=2, currency="EUR")
        kroner = ledger.add_charge(self.t + 120, self.t + 180, 10, receipt=14.92)
        stat = ledger.statistics(self.t, self.t + 180)
        self.assertEqual(stat["charged_kwh"], 20)
        self.assertEqual(stat["currency"], "DKK")
        self.assertEqual(stat["currency_mismatch_count"], 1)
        self.assertEqual(stat["known_spend_eur"], 14.92)
        self.assertIsNone(stat["spend_eur"])
        self.assertIsNone(stat["price_eur_kwh"])
        self.assertEqual(stat["missing_prices"], 0)
        self.assertEqual(ledger.data["charges"][euro]["cost_eur"], 2)
        self.assertEqual(ledger.data["charges"][kroner]["currency"], "DKK")
        day = ledger.snapshot(self.t + 180)["charging_daily"][0]
        self.assertEqual(day["known_cost_eur"], 14.92)
        self.assertEqual(day["currency_mismatch_count"], 1)

    def test_currency_changes_preserve_legacy_imports_and_preferences(self):
        ledger = self.ledger()
        ledger.preferences({"opening_price_eur_kwh": 0.3, "petrol_eur_l": 1.8})
        row = [1, self.t, self.t + 60, 10, 0, 10, 12, 2]
        ledger.import_home([row])
        archive = deepcopy(ledger.data)
        archive["charges"]["home-1"].pop("currency")
        archive["preferences"].pop("currency")
        restored = self.ledger("DKK", archive)
        restored.import_home([[1, self.t, self.t + 60, 10, 0, 74.6, 89.52, 14.92]])
        charge = restored.data["charges"]["home-1"]
        self.assertEqual(
            (charge["currency"], charge["cost_eur"], charge["reimbursement_eur"]),
            ("EUR", 10, 12),
        )
        self.assertTrue(charge["cost_currency_conflict"])
        self.assertEqual(restored.data["preferences"]["currency"], "EUR")
        with self.assertRaises(ValueError):
            restored.preferences({"currency": "DKK", "petrol_eur_l": 12})
        restored.edit_charge("home-1", currency="DKK", category="home")
        self.assertIsNone(charge["cost_eur"])
        restored.edit_charge("home-1", currency="DKK", receipt=74.6)
        self.assertIsNone(charge["reimbursement_eur"])
        self.assertEqual(charge["cost_eur"], 74.6)

    def test_new_dkk_import_free_cost_and_invalid_manual_values(self):
        ledger = self.ledger("DKK")
        ledger.import_home([[1, self.t, self.t + 60, 10, 0, 74.6, None, None]])
        self.assertEqual(ledger.statistics(self.t, self.t + 60)["spend_eur"], 74.6)
        self.assertEqual(ledger.data["charges"]["home-1"]["currency"], "DKK")
        zero = ledger.add_charge(self.t, self.t + 60, 10, receipt=0)
        self.assertEqual(ledger.data["charges"][zero]["cost_eur"], 0)
        for value in (-1, float("nan"), float("inf")):
            with self.assertRaises(ValueError):
                ledger.edit_charge(zero, receipt=value)
        with self.assertRaises(ValueError):
            ledger.edit_charge(zero, receipt=1, currency="dkk")

    def test_split_enrichment_cannot_reuse_eur_result_for_dkk_record(self):
        spec = importlib.util.spec_from_file_location(
            "accounting_ledger.cost_adapter", ROOT / "car_dashboard" / "cost_adapter.py"
        )
        adapter = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(adapter)
        ledger = self.ledger("DKK")
        ledger.import_home([[1, self.t, self.t + 60, 1, 0, 1, None, None]])
        result = {
            "status": "complete",
            "currency": "EUR",
            "cost_split_kwh": 1,
            "cost_split_total_eur": 1,
            "grid_cost_eur": 1,
        }
        ledger.data["cost_split_results"] = {"home-1": result}
        recorder = adapter.CostRecorder(SimpleNamespace(ledger=ledger, settings={}))
        self.assertNotIn(
            "grid_cost_eur", recorder.enrich(ledger.snapshot(self.t + 60))["charges"][0]
        )
        result["currency"] = "DKK"
        self.assertEqual(
            recorder.enrich(ledger.snapshot(self.t + 60))["charges"][0][
                "grid_cost_eur"
            ],
            1,
        )

    def test_foreign_price_cannot_restore_unknown_battery_value(self):
        ledger = self.native_gap()
        ledger.currency = "DKK"
        self.assertIsNone(ledger.cost_segments()[-1]["cost_eur"])
        ledger.add_charge(self.t + 4850, self.t + 4900, 1, receipt=2, currency="EUR")
        ledger.ingest(self.t + 5000, 1040, None, soc_pct=83)
        self.assertIsNone(ledger.cost_segments()[-1]["cost_eur"])

    def test_running_coordinator_updates_accounting_and_new_manual_units_only(self):
        spec = importlib.util.spec_from_file_location(
            "accounting_ledger.coordinator", ROOT / "car_dashboard" / "coordinator.py"
        )
        adapter = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(adapter)
        owner = adapter.CarLedgerCoordinator.__new__(adapter.CarLedgerCoordinator)
        owner.ledger = self.ledger()
        owner.ledger.import_home([[1, self.t, self.t + 60, 1, 0, 2, None, None]])
        owner.hass = SimpleNamespace(
            config=SimpleNamespace(currency="DKK", time_zone="UTC"),
            states=SimpleNamespace(get=lambda _: None),
        )
        owner.settings = {"home_connected": "", "currency": "EUR"}
        owner.active_home_id = None
        owner.source_status = "fresh"
        owner.cost_recorder = SimpleNamespace(enrich=lambda value: value)
        owner.store = SimpleNamespace(async_save=AsyncMock())
        owner.async_set_updated_data = Mock()
        owner.lock = asyncio.Lock()
        snapshot = owner.snapshot()
        self.assertEqual(snapshot["currency"], "DKK")
        self.assertEqual(snapshot["preferences"]["currency"], "EUR")
        self.assertEqual(snapshot["charges"][0]["currency"], "EUR")
        # A write can arrive before the next sample/snapshot after a change.
        owner.ledger.currency = "EUR"
        asyncio.run(
            owner.mutate(
                "add_charge",
                {
                    "start": self.t + 120,
                    "end": self.t + 180,
                    "kwh": 1,
                    "receipt": 14.92,
                },
            )
        )
        manual = next(
            c for c in owner.ledger.data["charges"].values() if c["kind"] == "public"
        )
        self.assertEqual(manual["currency"], "DKK")
        self.assertEqual(manual["cost_eur"], 14.92)

    def test_explicit_source_currency_wins_over_ha_default_without_conversion(self):
        ledger = self.ledger("DKK")
        for attributes in (
            {"currency": "EUR"},
            {"unit_of_measurement": "EUR"},
            {"unit_of_measurement": "€/kWh"},
        ):
            currency = module.source_currency(attributes, "DKK")
            self.assertEqual(currency, "EUR")
            ledger.import_home(
                [[1, self.t, self.t + 60, 1, 0, 2, None, None]], currency=currency
            )
            self.assertEqual(ledger.data["charges"]["home-1"]["currency"], "EUR")
            self.assertEqual(ledger.data["charges"]["home-1"]["cost_eur"], 2)
            self.assertIsNone(ledger.statistics(self.t, self.t + 60)["spend_eur"])
        self.assertEqual(module.source_currency({}, "DKK"), "DKK")
        with self.assertRaises(ValueError):
            module.source_currency(
                {"currency": "DKK", "unit_of_measurement": "EUR"}, "DKK"
            )

    def test_coordinator_sample_honors_history_currency_metadata(self):
        spec = importlib.util.spec_from_file_location(
            "accounting_ledger.coordinator", ROOT / "car_dashboard" / "coordinator.py"
        )
        adapter = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(adapter)
        owner = adapter.CarLedgerCoordinator.__new__(adapter.CarLedgerCoordinator)
        owner.ledger = self.ledger()
        history = SimpleNamespace(
            attributes={
                "currency": "EUR",
                "sessions": [
                    [1, self.t, self.t + 60, 1, 0, 2, None, None],
                ],
            }
        )
        owner.hass = SimpleNamespace(
            config=SimpleNamespace(currency="DKK"),
            states=SimpleNamespace(
                get=lambda ident: history if ident == "sensor.history" else None
            ),
        )
        owner.settings = {
            "home_history": "sensor.history",
            "home_connected": "",
            "odometer": "",
            "range": "",
            "soc": "",
        }
        owner.active_home_id = None
        owner.cost_recorder = SimpleNamespace(refresh=AsyncMock())
        owner.source_status = "waiting_for_fresh_sample"
        owner.store = SimpleNamespace(async_save=AsyncMock())
        owner.async_set_updated_data = Mock()
        owner.lock = asyncio.Lock()
        asyncio.run(owner.sample())
        self.assertEqual(owner.ledger.currency, "DKK")
        self.assertEqual(owner.ledger.data["charges"]["home-1"]["currency"], "EUR")
        self.assertEqual(owner.ledger.data["charges"]["home-1"]["cost_eur"], 2)

    def test_explicit_foreign_price_sources_never_enter_dkk_checkpoint_replay(self):
        spec = importlib.util.spec_from_file_location(
            "accounting_ledger.cost_adapter", ROOT / "car_dashboard" / "cost_adapter.py"
        )
        adapter = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(adapter)
        ledger = self.ledger("DKK")
        ledger.import_home([[1, self.t, self.t + 60, 1, 0, 2, None, None]])
        for explicit in ({"currency": "EUR"}, {"unit_of_measurement": "€/kWh"}):
            state = SimpleNamespace(state="2", attributes=explicit)
            owner = SimpleNamespace(
                ledger=ledger,
                settings={
                    "cost_sources": {
                        key: "sensor." + key for key in adapter.SOURCE_KEYS
                    }
                },
                hass=SimpleNamespace(
                    states=SimpleNamespace(get=lambda _, current=state: current)
                ),
            )
            recorder = adapter.CostRecorder(owner)
            with patch.object(
                adapter,
                "get_instance",
                side_effect=AssertionError("foreign source queried"),
            ):
                asyncio.run(recorder.refresh(self.t + 60))
            self.assertEqual(ledger.data["cost_split_results"], {})


if __name__ == "__main__":
    unittest.main()
