"""Tests for the shared, module-managed dashboard lifecycle."""

from types import SimpleNamespace
from unittest.mock import AsyncMock, Mock

from homeassistant.components import frontend
from homeassistant.config_entries import ConfigEntryState
from homeassistant.core import HomeAssistant
from homeassistant.setup import async_setup_component
from pytest_homeassistant_custom_component.common import MockConfigEntry

from custom_components.nio_telematics import managed_dashboard as managed


def _entry(entry_id: str, path: str = "nio") -> SimpleNamespace:
    return SimpleNamespace(
        entry_id=entry_id,
        state=SimpleNamespace(value="loaded"),
        options={"nio_dashboard_enabled": True, "nio_dashboard_path": path},
    )


def _panel(config: dict) -> SimpleNamespace:
    return SimpleNamespace(config=config)


def _install_panel_api(hass: HomeAssistant, monkeypatch, entries):
    """Install small frontend API fakes while retaining HA's registry semantics."""
    registry = hass.data.setdefault(frontend.DATA_PANELS, {})
    calls = hass.data.setdefault("test_managed_panel_calls", [])
    monkeypatch.setattr(
        hass.config_entries,
        "async_entries",
        lambda domain=None: entries if domain == managed.DOMAIN else [],
    )
    monkeypatch.setattr(
        managed, "_async_register_static_assets", AsyncMock(return_value=True)
    )
    monkeypatch.setattr(
        managed,
        "_panel_config_for",
        lambda _hass, selected, _path: {
            "owner": managed._OWNER,
            "schema_version": managed._SCHEMA_VERSION,
            "entry_ids": [entry.entry_id for entry in selected],
        },
    )
    monkeypatch.setattr(
        managed, "_asset_url", lambda *_args: "/nio_telematics/panel.js?v=test"
    )

    async def register(_hass, *, frontend_url_path, config, **kwargs):
        calls.append({"frontend_url_path": frontend_url_path, **kwargs})
        if frontend_url_path in registry:
            raise ValueError("path already occupied")
        registry[frontend_url_path] = _panel(config)

    monkeypatch.setattr(
        frontend, "async_panel_exists", lambda _hass, path: path in registry
    )
    monkeypatch.setattr(
        frontend,
        "async_remove_panel",
        lambda _hass, path: registry.pop(path, None),
    )
    monkeypatch.setattr(
        "homeassistant.components.panel_custom.async_register_panel", register
    )
    return registry


async def test_two_opted_in_vehicles_share_one_idempotent_panel(
    hass: HomeAssistant, monkeypatch
) -> None:
    """Multiple entries share one route and repeated reconciliation stays stable."""
    entries = [_entry("car-1"), _entry("car-2")]
    registry = _install_panel_api(hass, monkeypatch, entries)

    await managed.async_reconcile_dashboard(hass)
    panel = registry["nio"]
    await managed.async_reconcile_dashboard(hass)

    assert list(registry) == ["nio"]
    assert panel.config["entry_ids"] == ["car-1", "car-2"]
    assert hass.data[managed._DATA_KEY]["panel"] is panel
    call = hass.data["test_managed_panel_calls"][0]
    assert call["embed_iframe"] is False
    assert call["require_admin"] is False
    assert "handle_safe_area" not in call


async def test_native_panel_registration_uses_real_ha_api(hass: HomeAssistant) -> None:
    """Register/serve the module with HA's real frontend and panel_custom APIs."""
    from custom_components.nio_telematics.car_dashboard import async_setup_dashboard
    from custom_components.nio_telematics.vehicle_dashboard import (
        async_setup_vehicle_dashboard,
    )

    assert await async_setup_component(hass, "frontend", {})
    await async_setup_dashboard(hass)
    await async_setup_vehicle_dashboard(hass)
    entry = MockConfigEntry(
        domain=managed.DOMAIN,
        title="ET5 Touring",
        data={"vin": "fixture"},
        options={"nio_dashboard_enabled": True, "nio_dashboard_path": "nio"},
    )
    entry.add_to_hass(hass)
    entry._async_set_state(hass, ConfigEntryState.LOADED, None)
    try:
        await managed.async_reconcile_dashboard(hass)
        panel = hass.data[frontend.DATA_PANELS]["nio"]
        assert panel.component_name == "custom"
        assert panel.config["entry_ids"] == [entry.entry_id]
        assert panel.config["_panel_custom"]["name"] == "nio-vehicle-panel"
        assert panel.config["_panel_custom"]["module_url"].startswith(
            "/nio_telematics/nio-vehicle-panel.js?v="
        )
        assert panel.config["history_url"].startswith(
            "/nio_telematics/nio-dashboard-history.js?v="
        )
        await managed.async_reconcile_dashboard(hass)
        assert hass.data[frontend.DATA_PANELS]["nio"] is panel
    finally:
        entry._async_set_state(hass, ConfigEntryState.NOT_LOADED, None)
        await managed.async_reconcile_dashboard(hass)


async def test_foreign_route_collision_is_not_modified(
    hass: HomeAssistant, monkeypatch
) -> None:
    """A title/path match never grants ownership of an existing panel."""
    entries = [_entry("car-1")]
    registry = _install_panel_api(hass, monkeypatch, entries)
    foreign = _panel({"owner": "another_integration", "schema_version": 1})
    registry["nio"] = foreign

    await managed.async_reconcile_dashboard(hass)

    assert registry["nio"] is foreign
    assert hass.data[managed._DATA_KEY].get("panel") is None


async def test_last_entry_unload_removes_only_the_owned_runtime_panel(
    hass: HomeAssistant, monkeypatch
) -> None:
    """Unloading the last opted-in entry removes the panel, not retained metadata."""
    entries = [_entry("car-1")]
    registry = _install_panel_api(hass, monkeypatch, entries)
    await managed.async_reconcile_dashboard(hass)
    owned_panel = registry["nio"]
    store = Mock()
    store.async_remove = AsyncMock()
    monkeypatch.setattr(managed, "Store", Mock(return_value=store))

    await managed.async_unload_managed_dashboard(hass, "car-1")

    assert registry == {}
    assert owned_panel.config["owner"] == managed._OWNER
    store.async_remove.assert_not_awaited()


async def test_foreign_replacement_during_asset_await_is_not_removed(
    hass: HomeAssistant, monkeypatch
) -> None:
    """Another integration can change the registry while we await local assets."""
    entries = [_entry("car-1")]
    registry = _install_panel_api(hass, monkeypatch, entries)
    await managed.async_reconcile_dashboard(hass)
    foreign = _panel({"owner": "other", "schema_version": 1})
    entries.append(_entry("car-2"))
    issue = Mock()
    monkeypatch.setattr(managed, "_set_dashboard_issue", issue)

    async def replace_while_awaiting(_hass):
        registry["nio"] = foreign
        return True

    monkeypatch.setattr(
        managed, "_async_register_static_assets", replace_while_awaiting
    )
    await managed.async_reconcile_dashboard(hass)

    assert registry["nio"] is foreign
    assert len(hass.data["test_managed_panel_calls"]) == 1
    assert issue.call_args.args[1] == "managed_dashboard_route_collision"


async def test_panel_api_unavailable_does_not_break_entry_setup(
    hass: HomeAssistant, monkeypatch
) -> None:
    """A headless or incomplete frontend leaves telemetry setup unaffected."""
    monkeypatch.setattr(
        hass.config_entries,
        "async_entries",
        lambda domain=None: [_entry("car-1")] if domain == managed.DOMAIN else [],
    )
    monkeypatch.setattr(managed, "_panel_registry", lambda _hass: None)

    await managed.async_reconcile_dashboard(hass)

    assert hass.data[managed._DATA_KEY]["panel"] is None


def test_dashboard_path_accepts_slug_only() -> None:
    """Nested paths, query strings and uppercase routes are rejected."""
    assert managed.validate_dashboard_path("nio-preview")
    assert not managed.validate_dashboard_path("/nio")
    assert not managed.validate_dashboard_path("nio?view=1")
    assert not managed.validate_dashboard_path("NIO")


async def test_startup_reconciliation_is_deferred_and_clears_one_shot_unsubscribe(
    hass: HomeAssistant, monkeypatch
) -> None:
    """The manager waits for HA started, then releases its callback handle."""
    callback = None

    def at_started(_hass, listener):
        nonlocal callback
        callback = listener
        return Mock()

    monkeypatch.setattr(
        managed,
        "Store",
        Mock(return_value=SimpleNamespace(async_load=AsyncMock(return_value={}))),
    )
    monkeypatch.setattr("homeassistant.helpers.start.async_at_started", at_started)
    reconcile = AsyncMock()
    monkeypatch.setattr(managed, "async_reconcile_dashboard", reconcile)

    await managed.async_setup_managed_dashboard(hass)
    assert callback is not None
    reconcile.assert_not_awaited()
    await callback(None)

    reconcile.assert_awaited_once_with(hass)
    assert hass.data[managed._DATA_KEY]["unsub"] is None


async def test_real_entry_state_callback_reconciles_after_startup_load(
    hass: HomeAssistant, monkeypatch
) -> None:
    """The public config-entry callback includes an entry loaded after HA start."""
    entry = MockConfigEntry(
        domain=managed.DOMAIN,
        title="ET7",
        data={"vin": "fixture"},
        options={"nio_dashboard_enabled": True, "nio_dashboard_path": "nio"},
    )
    entry.add_to_hass(hass)
    seen = []

    async def reconcile(current_hass):
        seen.extend(managed._entries(current_hass))

    monkeypatch.setattr(managed, "async_reconcile_dashboard", reconcile)
    managed.async_track_config_entry(hass, entry)
    entry._async_set_state(hass, ConfigEntryState.LOADED, None)
    await hass.async_block_till_done()

    assert seen == [entry]
    entry._async_set_state(hass, ConfigEntryState.NOT_LOADED, None)
    await hass.async_block_till_done()
