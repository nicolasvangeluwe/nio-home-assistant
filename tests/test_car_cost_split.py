"""Cost-split regressions for the optional bundled car ledger."""

import importlib.util
import pathlib
import unittest

PATH = (
    pathlib.Path(__file__).parents[1]
    / "custom_components"
    / "nio_telematics"
    / "car_dashboard"
    / "cost_split.py"
)
spec = importlib.util.spec_from_file_location("car_cost_split", PATH)
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)
split_session = module.split_session


def readings(energy, solar, total, grid=0.3, export=0.1):
    def rows(pairs):
        return [{"t": t, "v": value} for t, value in pairs]

    return {
        "energy": rows(energy),
        "solar": rows(solar),
        "total_cost": rows(total),
        "grid_price": rows([(0, grid)]),
        "export_price": rows([(0, export)]),
    }


class CostSplitTests(unittest.TestCase):
    def test_solar_grid_and_mixed_sources(self):
        for solar, total, grid, export in (
            (100, 0.1, 0, 0.1),
            (0, 0.3, 0.3, 0),
            (50, 0.2, 0.15, 0.05),
        ):
            data = readings(
                [(0, 0), (60, 1)],
                [(0, 0), (60, solar)],
                [(0, 0), (60, total)],
            )
            charge = {"start": 0, "end": 60, "kwh": 1, "cost_eur": total}
            result, _ = split_session(charge, data)
            self.assertEqual(result["status"], "complete")
            self.assertAlmostEqual(result["grid_cost_eur"], grid)
            self.assertAlmostEqual(result["foregone_export_eur"], export)

    def test_missing_start_remains_unknown(self):
        data = readings(
            [(20, 0.5), (60, 1)],
            [(0, 0), (60, 50)],
            [(0, 0), (60, 0.2)],
        )
        charge = {"start": 0, "end": 60, "kwh": 1, "cost_eur": 0.2}
        result, _ = split_session(charge, data)
        self.assertEqual(result["status"], "missing_start")

    def test_foreign_or_legacy_eur_checkpoint_cannot_price_dkk_session(self):
        data = readings([(0, 0), (60, 1)], [(0, 0), (60, 0)], [(0, 0), (60, 1)], grid=1)
        charge = {"start": 0, "end": 60, "kwh": 1, "cost_eur": 1, "currency": "DKK"}
        progress = {
            "version": 1,
            "start": 0,
            "t": 30,
            "energy": 0.5,
            "solar_energy": 0,
            "grid_cost": 0.15,
            "export_cost": 0,
        }
        for explicit_currency in (False, True):
            if explicit_currency:
                progress["currency"] = "EUR"
            result, checkpoint = split_session(charge, data, progress)
            self.assertEqual(result["status"], "complete")
            self.assertEqual(result["currency"], "DKK")
            self.assertEqual(checkpoint["currency"], "DKK")
            self.assertAlmostEqual(result["grid_cost_eur"], 1)

    def test_foreign_historical_rate_metadata_cannot_be_reinterpreted(self):
        data = readings([(0, 0), (60, 1)], [(0, 0), (60, 0)], [(0, 0), (60, 1)], grid=1)
        data["grid_price"][0]["currency"] = "EUR"
        charge = {"start": 0, "end": 60, "kwh": 1, "cost_eur": 1, "currency": "DKK"}
        result, checkpoint = split_session(charge, data)
        self.assertEqual(result["status"], "currency_mismatch")
        self.assertIsNone(checkpoint)
        data["grid_price"][0]["currency"] = "DKK"
        self.assertEqual(split_session(charge, data)[0]["status"], "complete")


if __name__ == "__main__":
    unittest.main()
