"""Recorded EVCC source allocation; estimates, never current-rate backpricing."""

from bisect import bisect_right
from math import isfinite

VERSION = 1
SOURCE_KEYS = ("energy", "solar", "total_cost", "grid_price", "export_price")


def numeric(value):
    try:
        result = float(value)
        return result if isfinite(result) else None
    except (TypeError, ValueError):
        return None


def normalise(rows):
    """Retain unavailable markers: they must interrupt coverage."""
    return sorted({float(r["t"]): numeric(r["v"]) for r in rows}.items())


def normalise_rates(rows):
    values = normalise(rows)
    for i, (t, value) in enumerate(values):
        if value is not None or i == 0:
            continue
        before = next((r for r in reversed(values[:i]) if r[1] is not None), None)
        after = next((r for r in values[i + 1 :] if r[1] is not None), None)
        # A brief restart marker between identical observations in one tariff
        # quarter does not mean that the dated rate was unknown for that quarter.
        if (
            before
            and after
            and before[1] == after[1]
            and after[0] - t <= 300
            and int(before[0] // 900) == int(after[0] // 900)
        ):
            values[i] = (t, before[1])
    return values


def split_session(charge, sources, progress=None):
    """Replay cumulative readings, optionally continuing a persisted prefix.

    EVCC publishes a sensor batch sequentially; a one-second look-ahead aligns
    cumulative solar/cost with energy. Rates never use this look-ahead. Source
    percentages/rates are rounded and quarter-boundary allocation is estimated.
    """
    series = {
        k: (normalise_rates if k.endswith("price") else normalise)(sources.get(k, []))
        for k in SOURCE_KEYS
    }
    stamps = {k: [r[0] for r in values] for k, values in series.items()}

    def at(key, t):
        index = bisect_right(stamps[key], t) - 1
        return series[key][index][1] if index >= 0 else None

    def rate_cost(key, start, end, energy):
        if not energy:
            return 0.0
        if end - start > 300:
            # A small first meter increment after a pause belongs near its end.
            if energy > 0.1:
                return None
            rate = at(key, end)
            return None if rate is None else energy * rate
        cuts = [start] + [t for t in stamps[key] if start < t < end] + [end]
        result = 0.0
        for a, b in zip(cuts, cuts[1:], strict=False):
            rate = at(key, a)
            if rate is None:
                return None
            result += energy * (b - a) / (end - start) * rate
        return result

    start, end, final_energy = charge["start"], charge["end"], charge["kwh"]
    prior = progress if progress and progress.get("version") == VERSION else None
    if prior and (prior["start"] != start or prior["energy"] > final_energy + 0.025):
        prior = None
    checkpoint = (
        dict(prior)
        if prior
        else {
            "version": VERSION,
            "start": start,
            "t": start,
            "energy": 0.0,
            "solar_energy": 0.0,
            "grid_cost": 0.0,
            "export_cost": 0.0,
        }
    )
    readings = [
        (t, v)
        for t, v in series["energy"]
        if start <= t <= end + 3 and t > checkpoint["t"]
    ]
    zero_baseline = at("energy", start + 1) == 0
    if (
        not prior
        and not zero_baseline
        and (
            not readings
            or readings[0][0] > start + 180
            or readings[0][1] is None
            or readings[0][1] > 0.05
        )
    ):
        return {"status": "missing_start"}, None
    for t, energy in readings:
        if energy is None:
            # A temporary availability marker is safe only when the subsequent
            # meter delta still fits the bounded interval rule below.
            continue
        if energy < checkpoint["energy"] - 0.002:
            return {"status": "counter_reset"}, prior
        delta = energy - checkpoint["energy"]
        if delta <= 0:
            continue
        if t - checkpoint["t"] > 300 and delta > 0.1:
            return {"status": "missing_energy_interval"}, prior
        percentage = at("solar", t + 1)
        if percentage is None or not 0 <= percentage <= 100:
            return {"status": "missing_solar"}, prior
        solar_energy = energy * percentage / 100
        solar_delta = solar_energy - checkpoint["solar_energy"]
        tolerance = 0.002 + energy * 0.00002
        if solar_delta < -tolerance or solar_delta > delta + tolerance:
            return {"status": "source_discontinuity"}, prior
        solar_delta = min(delta, max(0.0, solar_delta))
        grid_cost = rate_cost("grid_price", checkpoint["t"], t, delta - solar_delta)
        export_cost = rate_cost("export_price", checkpoint["t"], t, solar_delta)
        if grid_cost is None or export_cost is None:
            return {"status": "missing_interval_price"}, prior
        checkpoint.update(
            t=t,
            energy=energy,
            solar_energy=solar_energy,
            grid_cost=checkpoint["grid_cost"] + grid_cost,
            export_cost=checkpoint["export_cost"] + export_cost,
        )
        if abs(energy - final_energy) <= 0.0011:
            break
    if abs(checkpoint["energy"] - final_energy) > 0.0011:
        return {"status": "missing_end"}, checkpoint
    total = numeric(charge.get("cost_eur"))
    recorded_total = at("total_cost", checkpoint["t"] + 1)
    if total is None or recorded_total is None or abs(total - recorded_total) > 0.01:
        return {"status": "missing_total"}, checkpoint
    calculated = checkpoint["grid_cost"] + checkpoint["export_cost"]
    difference = total - calculated
    if abs(difference) > max(0.03, final_energy * 0.0015, abs(total) * 0.02):
        return {"status": "total_mismatch", "difference_eur": difference}, checkpoint
    # Preserve the authoritative EVCC combined total. The small rounding/model
    # residual is disclosed in metadata, not treated as another measured cost.
    return {
        "status": "complete",
        "version": VERSION,
        "grid_cost_eur": checkpoint["grid_cost"],
        "foregone_export_eur": total - checkpoint["grid_cost"],
        "grid_kwh": final_energy - checkpoint["solar_energy"],
        "solar_kwh": checkpoint["solar_energy"],
        "cost_split_kwh": final_energy,
        "cost_split_total_eur": total,
        "cost_split_basis": "recorded_interval_estimate",
        "cost_split_residual_eur": difference,
    }, checkpoint
