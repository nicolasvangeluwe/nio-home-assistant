"""Explain an evidenced history-currency migration without changing amounts."""

from .ledger import number, source_currency


def history_currency_warning(ledger, attributes, source_label):
    """Warn only when an undeclared source can conflict with imported money.

    The configured HA currency remains the default contract. Numbers alone
    cannot identify a conversion workaround, so this advisory never applies FX
    or rewrites a record. Manual foreign receipts are not source evidence.
    """
    if not attributes or not source_label:
        return None
    try:
        declared = source_currency(attributes, "XXX", monetary=False)
    except ValueError:
        # Invalid explicit units follow the existing source-rejection path;
        # they must not be presented as merely absent metadata.
        return None
    if declared != "XXX":
        return None
    previous = {
        row.get("currency", "EUR")
        for row in ledger.data["charges"].values()
        if row.get("kind") == "home"
        and row.get("currency", "EUR") != ledger.currency
        and any(
            number(row.get(key)) is not None
            for key in ("cost_eur", "reimbursement_eur", "benefit_eur")
        )
    }
    if not previous:
        return None
    return {
        "code": "history_currency_assumed",
        "source": source_label,
        "currency": ledger.currency,
        "previous_currencies": sorted(previous),
    }
