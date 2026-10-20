"""Transactional source changes through HA config-entry APIs."""

from __future__ import annotations

import asyncio
from copy import deepcopy

from homeassistant.config_entries import ConfigEntryState


class SourceSwitchError(Exception):
    """A safe error: no entry data or credentials in log/flow messages."""


async def async_switch_source(hass, entry, data) -> None:
    """Stop one collector, start its replacement, restore data on failed setup.

    Caller must preflight identity and current coverage before invoking this.
    Snapshot after unloading, so any final OAuth refresh is preserved too.
    """
    lock = hass.data.setdefault("nio_telematics_source_switch_locks", {}).setdefault(
        entry.entry_id, asyncio.Lock()
    )
    async with lock:
        if not await hass.config_entries.async_unload(entry.entry_id):
            raise SourceSwitchError("source_unload_failed")
        original = deepcopy(dict(entry.data))
        try:
            hass.config_entries.async_update_entry(entry, data={**original, **data})
            loaded = await hass.config_entries.async_setup(entry.entry_id)
            if not loaded or entry.state is not ConfigEntryState.LOADED:
                raise SourceSwitchError("source_setup_failed")
        except Exception:
            # Failed setup can have registered a retry or loaded platforms.
            # Unload before restoring so no retry can run the rejected source.
            try:
                unloaded = await hass.config_entries.async_unload(entry.entry_id)
            except Exception:
                unloaded = False
            hass.config_entries.async_update_entry(entry, data=original)
            if not unloaded:
                raise SourceSwitchError("source_rollback_failed") from None
            try:
                restored = await hass.config_entries.async_setup(entry.entry_id)
            except Exception:
                restored = False
            if not restored or entry.state is not ConfigEntryState.LOADED:
                raise SourceSwitchError("source_rollback_failed") from None
            raise SourceSwitchError("source_switch_failed") from None
