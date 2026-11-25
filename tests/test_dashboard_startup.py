"""Only initial optional source validation waits for HA's startup boundary."""

import asyncio
import unittest
from copy import deepcopy
from types import SimpleNamespace
from unittest.mock import AsyncMock, patch

from homeassistant.const import EVENT_HOMEASSISTANT_STARTED

import custom_components.nio_telematics as integration
from custom_components.nio_telematics.car_dashboard import async_configure_recorder


class DashboardStartupTests(unittest.TestCase):
    def fixture(self, running=False):
        settings = {
            "odometer": "sensor.odo",
            "range": "sensor.range",
            "soc": "",
            "home_connected": "binary_sensor.amina",
            "home_history": "",
            "cost_sources": {},
            "capacity_kwh": 90.0,
            "full_range_km": 557.0,
        }
        history = {
            "revision": 12,
            "trips": [{"id": "keep-trip"}],
            "charges": {"keep-receipt": {"cost_eur": 2}},
            "measurement_errors": {"keep-decision": {}},
        }
        recorder = SimpleNamespace(
            settings=deepcopy(settings),
            ledger=SimpleNamespace(data=deepcopy(history)),
            async_stop=AsyncMock(),
        )
        callbacks = {}
        unload = []
        states = {"sensor.odo": object(), "sensor.range": object()}

        def listen(event, callback):
            self.assertEqual(event, EVENT_HOMEASSISTANT_STARTED)
            token = object()
            callbacks[token] = callback
            return lambda: callbacks.pop(token, None)

        entry = SimpleNamespace(
            entry_id="test", domain="nio_telematics", async_on_unload=unload.append
        )
        manager = {
            "recorders": {"test": recorder},
            "settings": {"test": deepcopy(settings)},
            "lock": asyncio.Lock(),
            "store": SimpleNamespace(async_save=AsyncMock()),
        }
        hass = SimpleNamespace(
            is_running=running,
            data={"nio_telematics_car_dashboard": manager, "panel_identity": object()},
            states=SimpleNamespace(get=states.get),
            config_entries=SimpleNamespace(async_get_entry=lambda _: entry),
            bus=SimpleNamespace(async_listen_once=listen),
        )

        async def reconcile(hass, entry):
            return await async_configure_recorder(hass, entry.entry_id, settings)

        return SimpleNamespace(
            hass=hass,
            entry=entry,
            manager=manager,
            recorder=recorder,
            history=history,
            callbacks=callbacks,
            unload=unload,
            states=states,
            reconcile=AsyncMock(side_effect=reconcile),
        )

    def fire(self, f):
        async def started():
            f.hass.is_running = True
            callbacks = list(f.callbacks.values())
            f.callbacks.clear()
            for callback in callbacks:
                await callback(SimpleNamespace(event_type=EVENT_HOMEASSISTANT_STARTED))

        asyncio.run(started())

    def test_late_sensor_reconciles_after_started_without_recreating_saved_recorder(
        self,
    ):
        f = self.fixture()
        panel = f.hass.data["panel_identity"]
        with (
            patch.object(integration, "async_reconcile_ledger", f.reconcile),
            patch.object(integration._LOGGER, "warning") as warning,
        ):
            asyncio.run(integration._async_initial_dashboard_reconcile(f.hass, f.entry))
            self.assertEqual(f.reconcile.await_count, 0)
            self.assertFalse(warning.called)
            self.assertIs(f.manager["recorders"]["test"], f.recorder)
            f.states["binary_sensor.amina"] = object()
            self.fire(f)
            self.assertEqual(f.reconcile.await_count, 1)
            self.assertFalse(warning.called)
            self.assertEqual(f.hass.data["nio_telematics_dashboard_errors"], {})
        self.assertEqual(f.recorder.ledger.data, f.history)
        self.assertFalse(f.recorder.async_stop.called)
        self.assertFalse(f.manager["store"].async_save.called)
        self.assertIs(f.hass.data["panel_identity"], panel)

    def test_persistently_missing_source_warns_only_after_started(self):
        f = self.fixture()
        with (
            patch.object(integration, "async_reconcile_ledger", f.reconcile),
            patch.object(integration._LOGGER, "warning") as warning,
        ):
            asyncio.run(integration._async_initial_dashboard_reconcile(f.hass, f.entry))
            self.assertFalse(warning.called)
            self.fire(f)
            self.assertEqual(warning.call_count, 1)
            self.assertEqual(
                f.hass.data["nio_telematics_dashboard_errors"]["test"],
                "home_connected entity does not exist",
            )
        self.assertEqual(f.recorder.ledger.data, f.history)
        self.assertFalse(f.recorder.async_stop.called)

    def test_running_reload_and_explicit_options_still_validate_immediately(self):
        f = self.fixture(running=True)
        with (
            patch.object(integration, "async_reconcile_ledger", f.reconcile),
            patch.object(integration._LOGGER, "warning"),
        ):
            asyncio.run(integration._async_initial_dashboard_reconcile(f.hass, f.entry))
            self.assertEqual(f.reconcile.await_count, 1)
            self.assertEqual(f.callbacks, {})
            # Explicit options save uses the same immediate existing helper.
            f.hass.is_running = False
            asyncio.run(integration._async_dashboard_options_updated(f.hass, f.entry))
            self.assertEqual(f.reconcile.await_count, 2)
            self.assertEqual(f.callbacks, {})

    def test_unload_cancels_callback_and_recreated_saved_recorder_keeps_history(self):
        f = self.fixture()
        with patch.object(integration, "async_reconcile_ledger", f.reconcile):
            asyncio.run(integration._async_initial_dashboard_reconcile(f.hass, f.entry))
            for cancel in f.unload:
                cancel()
            self.fire(f)
            self.assertEqual(f.reconcile.await_count, 0)
            replacement = SimpleNamespace(
                settings=deepcopy(f.recorder.settings),
                ledger=SimpleNamespace(data=deepcopy(f.history)),
                async_stop=AsyncMock(),
            )
            f.manager["recorders"]["test"] = replacement
            f.states["binary_sensor.amina"] = object()
            asyncio.run(integration._async_initial_dashboard_reconcile(f.hass, f.entry))
            self.assertEqual(f.reconcile.await_count, 1)
            self.assertIs(f.manager["recorders"]["test"], replacement)
            self.assertEqual(replacement.ledger.data, f.history)
            self.assertFalse(replacement.async_stop.called)
