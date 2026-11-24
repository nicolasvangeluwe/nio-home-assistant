"""Read-only calendar windows over the existing ledger calculation contract."""

from datetime import UTC, date, datetime, time, timedelta
from math import nextafter

SCOPES = ("day", "week", "month", "year")


def calendar_window(scope, anchor, tz=UTC, now=None):
    """Return local calendar boundaries, including DST and Monday-based weeks."""
    if scope not in SCOPES:
        raise ValueError("Choose day, week, month or year")
    now = now if now is not None else datetime.now(UTC).timestamp()
    selected = (
        date.fromisoformat(anchor) if anchor else datetime.fromtimestamp(now, tz).date()
    )
    start = selected
    if scope == "week":
        start -= timedelta(days=start.weekday())
    elif scope == "month":
        start = start.replace(day=1)
    elif scope == "year":
        start = start.replace(month=1, day=1)
    if scope in ("day", "week"):
        end = start + timedelta(days=1 if scope == "day" else 7)
    elif scope == "month":
        end = date(start.year + (start.month == 12), start.month % 12 + 1, 1)
    else:
        end = date(start.year + 1, 1, 1)
    begin = datetime.combine(start, time.min, tzinfo=tz).timestamp()
    finish = datetime.combine(end, time.min, tzinfo=tz).timestamp()
    return {
        "scope": scope,
        "date": selected.isoformat(),
        "start_date": start.isoformat(),
        "end_date": end.isoformat(),
        "start": begin,
        "end": finish,
        "timezone": str(tz),
        "effective_end": min(now, nextafter(finish, float("-inf"))),
        "boundary_mode": "interval_end",
    }


def period_statistics(ledger, window):
    """Use the same statistics and projection formulas as Ledger.snapshot()."""
    stat = ledger.statistics(window["start"], window["effective_end"])
    energy = ledger.data["last"]["energy"] if ledger.data["last"] else None
    consumption = stat["consumption_kwh_100km"]
    stat["projected_range_km"] = (
        energy / consumption * 100
        if energy is not None and consumption and consumption > 0
        else None
    )
    # The saved preferences are already validated by the ledger mutation API.
    from .ledger import number

    pref = ledger.data["preferences"]
    petrol, price = number(pref.get("petrol_l_100km")), number(pref.get("petrol_eur_l"))
    if pref.get("currency", "EUR") != ledger.currency:
        price = None
    stat["petrol_comparison_eur"] = (
        stat["distance_km"] / 100 * petrol * price
        if petrol is not None and price is not None
        else None
    )
    stat["petrol_saving_eur"] = (
        stat["petrol_comparison_eur"] - stat["driving_cost_eur"]
        if stat["petrol_comparison_eur"] is not None
        and stat["driving_cost_eur"] is not None
        and stat["cost_complete"]
        else None
    )
    return stat
