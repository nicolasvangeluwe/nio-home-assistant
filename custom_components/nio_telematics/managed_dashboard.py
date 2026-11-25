"""Lifecycle management for the shared, module-owned NIO dashboard panel."""

from __future__ import annotations

import asyncio
import hashlib
import logging
import re
from pathlib import Path
from typing import Any

from homeassistant.core import HomeAssistant
from homeassistant.helpers.storage import Store

from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)
_STORE_VERSION = 1
_STORE_KEY = "nio_telematics.managed_dashboard"
_OWNER = DOMAIN
_SCHEMA_VERSION = 1
_DEFAULT_PATH = "nio"
_PATH_RE = re.compile(r"^[a-z0-9][a-z0-9_-]{0,63}$")
_DATA_KEY = "nio_telematics_managed_dashboard"
_ENABLED = "nio_dashboard_enabled"
_PATH = "nio_dashboard_path"


def dashboard_path_for_entry(hass: HomeAssistant, entry: Any) -> str:
    """Return the entry's selected path, defaulting to the current manager path."""
    requested = entry.options.get(_PATH)
    if isinstance(requested, str) and _PATH_RE.fullmatch(requested):
        return requested
    state = hass.data.get(_DATA_KEY, {})
    selected = state.get("path")
    if isinstance(selected, str) and _PATH_RE.fullmatch(selected):
        return selected
    return _DEFAULT_PATH


def validate_dashboard_path(path: str) -> bool:
    """Check a bare URL slug without accepting a URL, suffix, or nested path."""
    return isinstance(path, str) and _PATH_RE.fullmatch(path) is not None


def _manager(hass: HomeAssistant) -> dict[str, Any]:
    return hass.data.setdefault(
        _DATA_KEY,
        {"lock": asyncio.Lock(), "path": _DEFAULT_PATH, "panel": None, "unsub": None},
    )


def _set_dashboard_issue(
    hass: HomeAssistant,
    issue_id: str,
    translation_key: str,
    placeholders: dict[str, str],
) -> None:
    """Expose route conflicts in Repairs as well as the integration log."""
    try:
        from homeassistant.helpers import issue_registry as ir

        ir.async_create_issue(
            hass,
            DOMAIN,
            issue_id,
            is_fixable=False,
            is_persistent=True,
            severity=ir.IssueSeverity.WARNING,
            translation_key=translation_key,
            translation_placeholders=placeholders,
        )
    except Exception as err:
        _LOGGER.warning("Could not report NIO dashboard issue %s: %s", issue_id, err)


def _clear_dashboard_issue(hass: HomeAssistant, issue_id: str) -> None:
    """Remove a previously reported dashboard route issue."""
    try:
        from homeassistant.helpers import issue_registry as ir

        ir.async_delete_issue(hass, DOMAIN, issue_id)
    except Exception as err:
        _LOGGER.debug("Could not clear NIO dashboard issue %s: %s", issue_id, err)


def _entries(hass: HomeAssistant, exclude_entry_id: str | None = None) -> list[Any]:
    return [
        entry
        for entry in hass.config_entries.async_entries(DOMAIN)
        if entry.entry_id != exclude_entry_id
        and getattr(entry.state, "value", entry.state) == "loaded"
        and entry.options.get(_ENABLED) is True
    ]


def _panel_registry(hass: HomeAssistant) -> dict[str, Any] | None:
    """Return HA's public component panel registry when the frontend is present."""
    try:
        from homeassistant.components import frontend

        registry = hass.data.get(frontend.DATA_PANELS)
    except (ImportError, AttributeError):
        return None
    return registry if isinstance(registry, dict) else None


def _panel_config(panel: Any) -> dict[str, Any] | None:
    config = getattr(panel, "config", None)
    return config if isinstance(config, dict) else None


def _is_owned(panel: Any) -> bool:
    config = _panel_config(panel)
    return bool(
        config
        and config.get("owner") == _OWNER
        and config.get("schema_version") == _SCHEMA_VERSION
    )


def _same_managed_config(
    current: dict[str, Any] | None, expected: dict[str, Any]
) -> bool:
    """Ignore panel_custom's HA-owned wrapper when checking our config revision."""
    return bool(current) and all(
        current.get(key) == value for key, value in expected.items()
    )


def _asset_url(component_path: Path, filename: str, public_path: str) -> str:
    asset = component_path / filename
    digest = hashlib.sha256(asset.read_bytes()).hexdigest()[:12]
    return f"{public_path}?v={digest}"


async def _async_register_static_assets(hass: HomeAssistant) -> bool:
    """Expose new module assets with content hashes; tolerate no HTTP server."""
    http = getattr(hass, "http", None)
    if http is None:
        return False
    from homeassistant.components.http import StaticPathConfig

    component_path = Path(__file__).parent
    required = {
        "nio-vehicle-panel.js": component_path / "nio-vehicle-panel.js",
        "nio-dashboard-history.js": component_path / "nio-dashboard-history.js",
        "nio-vehicle-card.js": component_path / "nio-vehicle-card.js",
        "car-dashboard.js": component_path / "car_dashboard" / "car-ledger-card.js",
    }
    missing = await hass.async_add_executor_job(
        lambda: [name for name, path in required.items() if not path.is_file()]
    )
    if missing:
        raise FileNotFoundError(
            f"NIO dashboard assets are missing: {', '.join(missing)}"
        )
    state = _manager(hass)
    if not state.get("assets_registered"):
        paths = [
            StaticPathConfig(f"/nio_telematics/{name}", str(required[name]), False)
            for name in ("nio-vehicle-panel.js",)
        ]
        await http.async_register_static_paths(paths)
        state["assets_registered"] = True
    return True


def _panel_config_for(
    hass: HomeAssistant, entries: list[Any], component_path: Path
) -> dict[str, Any]:
    legacy_digest = hashlib.sha256(
        (component_path / "car_dashboard" / "car-ledger-card.js").read_bytes()
    ).hexdigest()[:12]
    history_digest = hashlib.sha256(
        (component_path / "nio-dashboard-history.js").read_bytes()
    ).hexdigest()[:12]
    return {
        "owner": _OWNER,
        "schema_version": _SCHEMA_VERSION,
        "entry_ids": [entry.entry_id for entry in entries],
        "vehicle_card_url": _asset_url(
            component_path,
            "nio-vehicle-card.js",
            "/nio_telematics/nio-vehicle-card.js",
        ),
        "history_url": (
            f"/nio_telematics/nio-dashboard-history.js?v={history_digest}"
            f"&base_version={legacy_digest}"
        ),
        "history_base_url": (
            f"/nio_telematics/car-dashboard.js?nio_owned=1&v={legacy_digest}"
        ),
    }


def async_track_config_entry(hass: HomeAssistant, entry: Any) -> None:
    """Reconcile when a config entry reaches loaded/unloading after HA startup."""

    def _state_changed() -> None:
        hass.async_create_task(async_reconcile_dashboard(hass))

    unsubscribe = entry.async_on_state_change(_state_changed)
    entry.async_on_unload(unsubscribe)


async def async_reconcile_dashboard(
    hass: HomeAssistant, *, exclude_entry_id: str | None = None
) -> None:
    """Reconcile one shared panel against currently loaded opted-in vehicles."""
    state = _manager(hass)
    async with state["lock"]:
        entries = _entries(hass, exclude_entry_id)
        registry = _panel_registry(hass)
        if registry is None:
            if entries:
                _LOGGER.debug(
                    "NIO dashboard deferred: frontend panel registry unavailable"
                )
            return

        try:
            from homeassistant.components import frontend, panel_custom
        except (ImportError, AttributeError) as err:
            _LOGGER.debug("NIO dashboard deferred: panel API unavailable: %s", err)
            return

        prior_path = state.get("path", _DEFAULT_PATH)
        prior_panel = state.get("panel")
        for path, panel in tuple(registry.items()):
            # Exact runtime object plus the module marker is the only removal authority.
            if (
                panel is prior_panel
                and _is_owned(panel)
                and (not entries or path != prior_path)
            ):
                try:
                    frontend.async_remove_panel(hass, path)
                except Exception as err:
                    _LOGGER.warning(
                        "Could not remove owned NIO panel at %s: %s", path, err
                    )
                else:
                    state["panel"] = None

        if not entries:
            state["panel"] = None
            _clear_dashboard_issue(hass, "managed_dashboard_route_collision")
            _clear_dashboard_issue(hass, "managed_dashboard_route_conflict")
            return

        selected_path = state.get("path")
        if not validate_dashboard_path(selected_path):
            selected_path = _DEFAULT_PATH
        requested_paths = {entry.options.get(_PATH, selected_path) for entry in entries}
        if any(not validate_dashboard_path(path) for path in requested_paths):
            _LOGGER.warning("NIO dashboard path is invalid; dashboard remains disabled")
            return
        if len(requested_paths) > 1:
            _set_dashboard_issue(
                hass,
                "managed_dashboard_route_conflict",
                "dashboard_route_conflict",
                {
                    "paths": ", ".join(f"/{path}" for path in sorted(requested_paths)),
                    "path": selected_path,
                },
            )
            _LOGGER.warning(
                "NIO vehicles selected conflicting dashboard paths %s; retaining %s",
                sorted(requested_paths),
                selected_path,
            )
        else:
            _clear_dashboard_issue(hass, "managed_dashboard_route_conflict")
            selected_path = next(iter(requested_paths), selected_path)

        panel = registry.get(selected_path)
        if frontend.async_panel_exists(hass, selected_path) and panel is None:
            _set_dashboard_issue(
                hass,
                "managed_dashboard_route_collision",
                "dashboard_route_in_use",
                {"path": selected_path},
            )
            _LOGGER.warning(
                "NIO dashboard route /%s is occupied by an unknown panel",
                selected_path,
            )
            return
        if panel is not None and not (panel is prior_panel and _is_owned(panel)):
            _set_dashboard_issue(
                hass,
                "managed_dashboard_route_collision",
                "dashboard_route_in_use",
                {"path": selected_path},
            )
            _LOGGER.warning(
                "NIO dashboard route /%s is occupied by a foreign panel; "
                "no panel was changed",
                selected_path,
            )
            return

        try:
            assets_available = await _async_register_static_assets(hass)
        except Exception as err:
            _LOGGER.warning("NIO dashboard frontend assets unavailable: %s", err)
            return
        if not assets_available:
            return

        component_path = Path(__file__).parent
        config = await hass.async_add_executor_job(
            _panel_config_for, hass, entries, component_path
        )
        module_url = await hass.async_add_executor_job(
            _asset_url,
            component_path,
            "nio-vehicle-panel.js",
            "/nio_telematics/nio-vehicle-panel.js",
        )
        # Other integrations do not share our lock. Assets/hashes yielded to HA,
        # so the route may now belong to a different runtime panel object.
        registry = _panel_registry(hass)
        if registry is None:
            return
        panel = registry.get(selected_path)
        if (
            panel is not None or frontend.async_panel_exists(hass, selected_path)
        ) and not (panel is prior_panel and _is_owned(panel)):
            _set_dashboard_issue(
                hass,
                "managed_dashboard_route_collision",
                "dashboard_route_in_use",
                {"path": selected_path},
            )
            _LOGGER.warning(
                "NIO dashboard route /%s changed ownership while preparing assets; "
                "no panel was changed",
                selected_path,
            )
            return
        # Preserve an already registered, owned panel by changing only its config.
        # Registration APIs do not provide an update operation, so remove/re-add only
        # after a destination is known to be free.
        if panel is prior_panel and _is_owned(panel):
            old_config = _panel_config(panel)
            if _same_managed_config(old_config, config):
                return
            try:
                frontend.async_remove_panel(hass, selected_path)
            except Exception as err:
                _LOGGER.warning("Could not update owned NIO panel: %s", err)
                return
            state["panel"] = None

        try:
            await panel_custom.async_register_panel(
                hass,
                frontend_url_path=selected_path,
                webcomponent_name="nio-vehicle-panel",
                sidebar_title="NIO",
                sidebar_icon="mdi:car",
                module_url=module_url,
                embed_iframe=False,
                config=config,
                require_admin=False,
            )
        except Exception as err:
            _LOGGER.warning("NIO dashboard panel registration unavailable: %s", err)
            return
        registry = _panel_registry(hass)
        registered = registry.get(selected_path) if registry else None
        if registered is not None and _is_owned(registered):
            _clear_dashboard_issue(hass, "managed_dashboard_route_collision")
            if (
                prior_panel is not None
                and prior_path != selected_path
                and registry.get(prior_path) is prior_panel
                and _is_owned(prior_panel)
            ):
                try:
                    frontend.async_remove_panel(hass, prior_path)
                except Exception as err:
                    _LOGGER.warning(
                        "Could not remove previous owned NIO panel: %s", err
                    )
                    if registry.get(selected_path) is registered and _is_owned(
                        registered
                    ):
                        try:
                            frontend.async_remove_panel(hass, selected_path)
                        except Exception as remove_err:
                            _LOGGER.warning(
                                "Could not roll back new NIO panel at %s: %s",
                                selected_path,
                                remove_err,
                            )
                    return
            state.update(path=selected_path, panel=registered)
            try:
                await Store(hass, _STORE_VERSION, _STORE_KEY).async_save(
                    {"path": selected_path, "schema_version": _SCHEMA_VERSION}
                )
            except Exception as err:
                _LOGGER.warning("Could not persist NIO dashboard path: %s", err)


async def async_setup_managed_dashboard(hass: HomeAssistant) -> None:
    """Load retained route and reconcile after HA startup without blocking startup."""
    state = _manager(hass)
    try:
        saved = await Store(hass, _STORE_VERSION, _STORE_KEY).async_load()
    except Exception as err:
        _LOGGER.warning("Could not load NIO dashboard metadata: %s", err)
        saved = None
    if isinstance(saved, dict) and validate_dashboard_path(saved.get("path")):
        state["path"] = saved["path"]
    if state.get("unsub") is not None:
        return

    from homeassistant.helpers.start import async_at_started

    async def _started(_event: Any) -> None:
        state["unsub"] = None
        await async_reconcile_dashboard(hass)

    state["unsub"] = async_at_started(hass, _started)


async def async_unload_managed_dashboard(hass: HomeAssistant, entry_id: str) -> None:
    """Drop a vehicle from the panel only after HA confirms its platforms unloaded."""
    await async_reconcile_dashboard(hass, exclude_entry_id=entry_id)
