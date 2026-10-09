"""SoC restoration must not mistake the old snapshot placeholder for data."""

from types import SimpleNamespace

import pytest

from custom_components.nio_telematics.sensor import _restorable_soc, _soc_number


@pytest.mark.parametrize(
    ("raw", "expected"),
    [(38, 38.0), (0, 0.0), (-1, None), (101, None), ("unknown", None)],
)
def test_soc_value_validation(raw: object, expected: float | None) -> None:
    assert _soc_number(raw) == expected


def test_only_energy_sourced_soc_is_restored() -> None:
    old_state = SimpleNamespace(state="0.0", attributes={})
    energy_state = SimpleNamespace(
        state="38.0",
        attributes={"source_endpoint": "soc_status", "last_valid_sample": "time"},
    )

    assert _restorable_soc(old_state) is None
    assert _restorable_soc(energy_state) == (38.0, "time")
