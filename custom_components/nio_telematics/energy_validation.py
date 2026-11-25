"""Shared, source-clock based validation for energy-feed observations."""


def confirm_joint_zero(
    self,
    energy,
    previous,
    soc_at,
    range_at,
    previous_soc_at,
    previous_range_at,
    *,
    observed_at,
):
    """Confirm an abrupt joint zero only with later source evidence.

    Sixty seconds is a chosen confirmation window, not an API guarantee.
    Background polls/errors never call this method. Near-empty and initial
    zeroes remain valid. Both zero-field clocks must advance on a later
    successful read; cached pairs never mature. Accepted fields keep that
    confirming reading's actual NIO clocks, never the local read time.
    """
    clocks = {"soc": soc_at, "remaining_range": range_at}
    values = {"soc": energy.soc, "remaining_range": energy.remaining_range}
    pending = self._joint_zero_pending
    if pending and any(
        value is not None
        and value > 0
        and clocks[key] is not None
        and clocks[key] >= pending[key]
        for key, value in values.items()
    ):
        self._rejected_zero_at.update({key: pending[key] for key in clocks})
        self._joint_zero_pending = pending = None
    blocked = {
        key
        for key, value in values.items()
        if value == 0
        and clocks[key] is not None
        and key in self._rejected_zero_at
        and clocks[key] <= self._rejected_zero_at[key]
    }
    joint = (
        energy.soc == 0
        and energy.remaining_range == 0
        and soc_at is not None
        and range_at is not None
        and abs((soc_at - range_at).total_seconds()) <= 5
        and not blocked
    )
    if (
        pending is None
        and joint
        and previous.soc is not None
        and previous.soc > 1
        and previous.remaining_range is not None
        and previous.remaining_range > 0
        and (previous_soc_at is None or soc_at > previous_soc_at)
        and (previous_range_at is None or range_at > previous_range_at)
    ):
        pending = {"started": observed_at, **clocks}
        self._joint_zero_pending = pending
    if pending:
        if joint:
            if observed_at - pending["started"] >= 60 and all(
                clocks[key] > pending[key] for key in clocks
            ):
                self._joint_zero_pending = None
                return blocked
        for key in clocks:
            if values[key] == 0 and clocks[key] is not None:
                pending[key] = max(pending[key], clocks[key])
        blocked.update(key for key, value in values.items() if value == 0)
    return blocked
