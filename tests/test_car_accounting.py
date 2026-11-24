"""Accounting outcomes: preserved currency meaning and booked-price continuity."""

import asyncio
import importlib.util
import json
import pathlib
import sys
import types
import unittest
from copy import deepcopy
from datetime import UTC, datetime
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

    def coordinator(self, states):
        spec = importlib.util.spec_from_file_location(
            "accounting_ledger.coordinator", ROOT / "car_dashboard" / "coordinator.py"
        )
        adapter = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(adapter)
        owner = adapter.CarLedgerCoordinator.__new__(adapter.CarLedgerCoordinator)
        owner.ledger = self.ledger("DKK")
        owner.hass = SimpleNamespace(
            config=SimpleNamespace(currency="DKK", time_zone="UTC"),
            states=SimpleNamespace(get=states.get),
        )
        owner.settings = {
            "home_history": "sensor.history",
            "home_connected": "sensor.connected",
            "odometer": "",
            "range": "",
            "soc": "",
        }
        owner.active_home_id = None
        owner.source_status = "waiting_for_fresh_sample"
        owner.cost_recorder = SimpleNamespace(
            refresh=AsyncMock(), enrich=lambda value: value
        )
        owner.store = SimpleNamespace(async_save=AsyncMock())
        owner.async_set_updated_data = Mock()
        owner.lock = asyncio.Lock()
        return owner

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

    def holiday_gap(self):
        ledger = self.ledger("DKK")
        ledger.preferences({"opening_price_eur_kwh": 0.3})
        for dt, odo, soc in (
            (0, 7000, 79.5),
            (600, 7005, 79),
            (14100, 7046, 67),
            (14700, 7056, 65),
            (15300, 7066, 63),
        ):
            ledger.ingest(self.t + dt, odo, None, soc_pct=soc)
        ledger.tick(self.t + 18000)
        return ledger

    def test_manual_gap_independent_reference_never_changes_stock_or_receipts(self):
        ledger = self.holiday_gap()
        raw = deepcopy(ledger.data)
        before = ledger.statistics(0, self.t + 18000)
        interval = ledger.unaccounted_intervals()[0]
        later = deepcopy(ledger.cost_segments()[2:])
        self.assertEqual(before["distance_km"], 66)
        self.assertEqual(before["consumption_distance_km"], 25)
        self.assertAlmostEqual(before["used_kwh"], 4.05)
        self.assertAlmostEqual(before["driving_cost_eur"], 1.215)
        self.assertEqual(before["unaccounted_distance_km"], 41)
        ledger.resolve_gap(
            interval["id"],
            interval["fingerprint"],
            "manual",
            energy_kwh=12,
            cost=3.6,
            currency="DKK",
        )
        after = ledger.statistics(0, self.t + 18000)
        self.assertEqual(after["distance_km"], 66)
        self.assertEqual(after["consumption_distance_km"], 66)
        self.assertAlmostEqual(after["used_kwh"], 16.05)
        self.assertAlmostEqual(after["driving_cost_eur"], 4.815)
        self.assertEqual(after["unaccounted_distance_km"], 0)
        self.assertEqual(after["manual_gap_count"], 1)
        self.assertEqual(after["spend_eur"], 0)
        self.assertEqual(after["charged_kwh"], 0)
        self.assertEqual(ledger.cost_segments()[2:], later)
        self.assertAlmostEqual(
            ledger.statistics(0, self.t + 18000, 100, native_only=True)[
                "consumption_kwh_100km"
            ],
            16.2,
        )
        for key in (
            "trips",
            "charges",
            "samples",
            "opening",
            "preferences",
            "parked_losses",
        ):
            self.assertEqual(ledger.data[key], raw[key])
        restored = self.ledger("DKK", json.loads(json.dumps(ledger.data)))
        self.assertEqual(
            restored.unaccounted_intervals(), ledger.unaccounted_intervals()
        )
        self.assertEqual(restored.cost_segments(), ledger.cost_segments())
        snapshot = ledger.snapshot(self.t + 18000)
        self.assertEqual(snapshot["counters"][0]["statistics"]["manual_gap_count"], 1)
        self.assertTrue(
            any(
                r.get("manual_gap_reconciled")
                for t in snapshot["trips"]
                for r in t["segments"]
            )
        )

    def test_gap_ignore_and_reopen_are_reversible_and_never_zero_usage(self):
        ledger = self.holiday_gap()
        interval = ledger.unaccounted_intervals()[0]
        for status in ("ignored", "open", "manual", "ignored", "open"):
            values = (
                {"energy_kwh": 12, "cost": 3.6, "currency": "DKK"}
                if status == "manual"
                else {}
            )
            ledger.resolve_gap(
                interval["id"], interval["fingerprint"], status, **values
            )
            stat = ledger.statistics(0, self.t + 18000)
            self.assertEqual(
                stat["unaccounted_distance_km"], 0 if status == "manual" else 41
            )
            self.assertEqual(stat["ignored_gap_count"], int(status == "ignored"))
            if status != "manual":
                self.assertIsNone(ledger.cost_segments()[1]["kwh"])
                self.assertIsNone(ledger.cost_segments()[1]["cost_eur"])
        self.assertEqual(ledger.data["gap_resolutions"], {})

    def test_manual_gap_cost_is_signed_currency_scoped_and_optional(self):
        ledger = self.holiday_gap()
        interval = ledger.unaccounted_intervals()[0]
        ledger.resolve_gap(
            interval["id"],
            interval["fingerprint"],
            "manual",
            energy_kwh=12,
            cost=-0.6,
            currency="DKK",
        )
        self.assertAlmostEqual(
            ledger.statistics(0, self.t + 18000)["driving_cost_eur"], 0.615
        )
        ledger.resolve_gap(
            interval["id"],
            interval["fingerprint"],
            "manual",
            energy_kwh=12,
            cost=3.6,
            currency="EUR",
        )
        stat = ledger.statistics(0, self.t + 18000)
        self.assertAlmostEqual(stat["driving_cost_eur"], 1.215)
        self.assertEqual(stat["currency_mismatch_count"], 1)
        self.assertEqual(ledger.unaccounted_intervals()[0]["cost"], 3.6)
        # Clearing an actual cost does not convert its old amount or create a rate.
        ledger.resolve_gap(
            interval["id"], interval["fingerprint"], "manual", energy_kwh=12
        )
        self.assertIsNone(ledger.cost_segments()[1]["cost_eur"])
        ledger.resolve_gap(
            interval["id"], interval["fingerprint"], "manual", energy_kwh=2
        )
        self.assertAlmostEqual(ledger.cost_segments()[1]["cost_eur"], 0.6)
        ledger.preferences({"opening_price_eur_kwh": None})
        self.assertIsNone(ledger.cost_segments()[1]["cost_eur"])

    def test_source_changes_stale_manual_overlay_and_reject_old_fingerprint(self):
        ledger = self.holiday_gap()
        interval = ledger.unaccounted_intervals()[0]
        ledger.resolve_gap(
            interval["id"], interval["fingerprint"], "manual", energy_kwh=12, cost=3.6
        )
        trip = next(
            t
            for t in ledger.data["trips"]
            if any(s.get("invalid_reason") == "gap" for s in t["segments"])
        )
        trip["source"] = "native_source_replay"
        self.assertEqual(ledger.unaccounted_intervals()[0]["resolution"], "stale")
        self.assertIsNone(ledger.cost_segments()[1]["kwh"])
        self.assertEqual(
            ledger.snapshot(self.t + 18000)["stale_gap_resolution_count"], 1
        )
        with self.assertRaises(ValueError):
            ledger.resolve_gap(
                interval["id"], interval["fingerprint"], "manual", energy_kwh=12
            )
        # Once evidence repairs the gap, its old overlay is retained as stale,
        # never applied to a now-complete native row; it can still be undone.
        row = next(s for s in trip["segments"] if s.get("invalid_reason") == "gap")
        row.update(kwh=10.8, complete=True, invalid_reason=None)
        self.assertEqual(ledger.unaccounted_intervals(), [])
        self.assertEqual(
            ledger.snapshot(self.t + 18000)["stale_gap_resolution_count"], 1
        )
        ledger.resolve_gap(interval["id"], interval["fingerprint"], "open")
        self.assertEqual(ledger.data["gap_resolutions"], {})

    def test_manual_gap_rejects_invalid_values_without_partial_mutation(self):
        ledger = self.holiday_gap()
        interval = ledger.unaccounted_intervals()[0]
        for values in (
            {"energy_kwh": -1},
            {"energy_kwh": True},
            {"energy_kwh": None},
            {"energy_kwh": float("nan")},
            {"energy_kwh": 2, "cost": float("inf")},
            {"energy_kwh": 2, "cost": True},
            {"energy_kwh": 2, "currency": "dkk"},
        ):
            before = deepcopy(ledger.data)
            with self.assertRaises(ValueError):
                ledger.resolve_gap(
                    interval["id"], interval["fingerprint"], "manual", **values
                )
            self.assertEqual(ledger.data, before)
        ledger.resolve_gap(
            interval["id"], interval["fingerprint"], "manual", energy_kwh=0, cost=0
        )
        self.assertEqual(ledger.cost_segments()[1]["kwh"], 0)
        self.assertEqual(ledger.cost_segments()[1]["cost_eur"], 0)

    def test_gap_mutation_persists_atomically_and_rolls_back_failed_store(self):
        owner = self.coordinator({})
        owner.ledger = self.holiday_gap()
        interval = owner.ledger.unaccounted_intervals()[0]
        raw = deepcopy(owner.ledger.data["trips"])
        result = asyncio.run(
            owner.mutate(
                "resolve_gap",
                {
                    "ident": interval["id"],
                    "fingerprint": interval["fingerprint"],
                    "status": "manual",
                    "energy_kwh": 12,
                    "cost": 3.6,
                    "currency": "DKK",
                },
            )
        )
        self.assertEqual(result["unaccounted_intervals"][0]["resolution"], "manual")
        persisted = owner.store.async_save.call_args.args[0]
        self.assertEqual(persisted["trips"], raw)
        self.assertEqual(len(persisted["gap_resolutions"]), 1)
        before = deepcopy(owner.ledger.data)
        owner.store.async_save.side_effect = RuntimeError("store unavailable")
        with self.assertRaises(RuntimeError):
            asyncio.run(
                owner.mutate(
                    "resolve_gap",
                    {
                        "ident": interval["id"],
                        "fingerprint": interval["fingerprint"],
                        "status": "ignored",
                    },
                )
            )
        self.assertEqual(owner.ledger.data, before)

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

    def test_gap_reconciliation_cannot_create_new_known_priced_stock(self):
        for observed_start, observed_end, should_price in (
            (60, 55, False),
            (60, 35, False),
            (40, 35, True),
        ):
            ledger = self.ledger()
            ledger.preferences({"opening_price_eur_kwh": 0.3})
            ledger.data["opening"] = {"t": self.t, "energy": 40}
            ledger.data["trips"] = [
                {
                    "id": "stock-boundary",
                    "segments": [
                        {
                            "start": self.t,
                            "end": self.t + 100,
                            "km": 10,
                            "kwh": None,
                            "complete": False,
                            "invalid_reason": "gap",
                            "start_energy": observed_start,
                            "end_energy": observed_end,
                        },
                        {
                            "start": self.t + 100,
                            "end": self.t + 200,
                            "km": 5,
                            "kwh": 2,
                            "complete": True,
                            "start_energy": observed_end,
                            "end_energy": observed_end - 2,
                        },
                    ],
                }
            ]
            later_cost = ledger.cost_segments()[-1]["cost_eur"]
            if should_price:
                self.assertAlmostEqual(later_cost, 0.6)
            else:
                self.assertIsNone(later_cost)
            interval = ledger.unaccounted_intervals()[0]
            ledger.resolve_gap(
                interval["id"], interval["fingerprint"], "manual", energy_kwh=2
            )
            manual_cost = ledger.cost_segments()[0]["cost_eur"]
            if should_price:
                self.assertAlmostEqual(manual_cost, 0.6)
            else:
                self.assertIsNone(manual_cost)

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
        self.assertEqual(day["missing"], 1)

    def test_foreign_only_day_is_incomplete_without_losing_energy(self):
        ledger = self.ledger("DKK")
        ledger.add_charge(self.t, self.t + 60, 10, receipt=2, currency="EUR")
        day = ledger.snapshot(self.t + 60)["charging_daily"][0]
        self.assertEqual(day["kwh"], 10)
        self.assertEqual(day["known_cost_eur"], 0)
        self.assertEqual(day["missing"], 1)
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

    def test_source_parser_distinguishes_currency_rate_and_quantity_units(self):
        for unit in ("dkk", "DKK/kwh", "dKk / kWh"):
            self.assertEqual(
                module.source_currency({"unit_of_measurement": unit}, "EUR"), "DKK"
            )
        for unit in ("$", "DKK/kwhh", "ZZZ/kWh", "watts", "kWh"):
            with self.assertRaises(ValueError):
                module.source_currency({"unit_of_measurement": unit}, "EUR")
        for unit in ("KWH", "count", "sessions", "kW", "°C"):
            self.assertEqual(
                module.source_currency(
                    {"unit_of_measurement": unit}, "DKK", monetary=False
                ),
                "DKK",
            )
        with self.assertRaises(ValueError):
            module.source_currency(
                {"currency": "EUR", "unit_of_measurement": "$"}, "DKK"
            )

    def test_history_adapter_rejects_unknown_money_but_keeps_quantity_history(self):
        for attributes, expected in (
            ({}, "DKK"),
            ({"unit_of_measurement": "dkk/kwh"}, "DKK"),
            ({"unit_of_measurement": "EUR"}, "EUR"),
            ({"unit_of_measurement": "KWH"}, "DKK"),
            ({"unit_of_measurement": "sessions"}, "DKK"),
            ({"unit_of_measurement": "$"}, None),
            ({"unit_of_measurement": "DKK/kwhh"}, None),
        ):
            history = SimpleNamespace(
                attributes={
                    **attributes,
                    "sessions": [
                        [1, self.t, self.t + 60, 2.5, 0, 5, None, None],
                    ],
                }
            )
            owner = self.coordinator({"sensor.history": history})
            asyncio.run(owner.sample())
            if expected is None:
                self.assertEqual(owner.ledger.data["charges"], {})
            else:
                charge = owner.ledger.data["charges"]["home-1"]
                self.assertEqual(charge["currency"], expected)
                self.assertEqual(charge["kwh"], 2.5)
                self.assertEqual(charge["cost_eur"], 5)

    def test_live_adapter_rejects_unknown_money_without_fabricating_cost(self):
        for attributes, expected in (
            ({}, "DKK"),
            ({"unit_of_measurement": "dkk"}, "DKK"),
            ({"unit_of_measurement": "EUR"}, "EUR"),
            ({"unit_of_measurement": "$"}, None),
            ({"unit_of_measurement": "DKK/kwhh"}, None),
        ):
            owner = self.coordinator(
                {
                    "sensor.history": SimpleNamespace(attributes={}),
                    "sensor.connected": SimpleNamespace(
                        state="on", last_changed=datetime.fromtimestamp(self.t, UTC)
                    ),
                    "sensor.energy": SimpleNamespace(
                        state="2.5", attributes={"unit_of_measurement": "kWh"}
                    ),
                    "sensor.cost": SimpleNamespace(state="5", attributes=attributes),
                }
            )
            owner.active_home_id = "home-live"
            owner.settings["cost_sources"] = {
                "energy": "sensor.energy",
                "total_cost": "sensor.cost",
            }
            charge = owner.snapshot()["active_home_charge"]
            self.assertEqual(charge["kwh"], 2.5)
            self.assertEqual(charge["cost_eur"], None if expected is None else 5)
            if expected is not None:
                self.assertEqual(charge["currency"], expected)

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
