# NIO Open Telematics for Home Assistant

An experimental, read-only Home Assistant integration for NIO's official EU Open Telematics API.

This is an independent personal project, built with substantial AI assistance and shared with other owners. It is not affiliated with or endorsed by NIO or Home Assistant. Please treat it as development software, protect your credentials and vehicle data, and check data freshness before using it in automations.

## What works today

On one EU ET5 Touring, OAuth, vehicle state, odometer, **native battery SoC**, and remaining range have been verified in Home Assistant. SoC and range come from NIO's `soc_status/changes` feed; empty or partial responses do not erase the last valid readings. Each sensor exposes its source sample time and whether the displayed value was retained. NIO decides when new vehicle events are published, so a retained value can be old.

The integration checks the overlapping last ten minutes of SoC changes about every 15 seconds, with a 30-second gap around each rotating background request. A shared limiter keeps vehicle API requests at least 15 seconds apart per OAuth client and backs off when NIO rate-limits them. **Ten minutes is the history window, not the polling interval.** More frequent requests do not make the car transmit more frequently.

Other documented energy fields include charging state and target, battery current, temperatures, SoC limits, and pack diagnostics. Their presence in the API documentation does not mean that every car supplies a useful value. Detailed and diagnostic entities are disabled by default; enable only the ones you want in the vehicle's Home Assistant entity list. The SoC sensor's `observed_fields` attribute lists field *names* seen from your car. The **API availability** sensor distinguishes successful, empty, denied, and failed endpoint families.

### Known limits

- On the tested ET5 Touring, several non-energy feeds (including body, location, trips, and cabin data) have returned `permission_denied` from **NIO's API**. That is not a Home Assistant account-permission error; its exact NIO-side cause remains unconfirmed.
- A successful response can contain placeholders or absent fields. For example, a zero charging target while not charging is not a confirmed usable target. The integration suppresses zero-valued top-level battery-temperature placeholders rather than displaying a false −40 °C.
- The normal odometer uses verified mileage from `vehicle_status/latest`; the separate aftersales odometer endpoint has been denied for the tested application.
- Results are from **one vehicle and application**, not a compatibility guarantee for all EU models. No vehicle commands or charging policy are implemented in this integration.

See [CHANGELOG.md](CHANGELOG.md) for the release-by-release history. The current development version is `0.1.1-dev.12`.

## EU owners: help test

If you have an eligible EU NIO, please compare the integration's SoC, range, and other enabled values with your car or NIO app. Share your model, country, what works or does not, and approximate sample age in the [EU telemetry test discussion](https://github.com/nicolasvangeluwe/nio-home-assistant/discussions/6). A quick report is useful; you do not need to be a developer. Never post credentials, tokens, a full VIN, or precise location.

A case was sent to NIO, but the unresolved endpoint denials still need clarification. If you have a direct route to NIO's Open Telematics team, or can provide results from another EU vehicle, please join the discussion. We all want dependable SoC in Home Assistant—NIO owners, we are legion. 😄

## Install with HACS

[![Open this repository in HACS](https://my.home-assistant.io/badges/hacs_repository.svg)](https://my.home-assistant.io/redirect/hacs_repository/?owner=nicolasvangeluwe&repository=nio-home-assistant&category=integration)

If the button does not open your Home Assistant instance:

1. In **HACS**, open the three-dot menu → **Custom repositories**.
2. Add `https://github.com/nicolasvangeluwe/nio-home-assistant` as an **Integration**.
3. Open **NIO Open Telematics** in HACS, select **Download**, and choose the latest development release.
4. Restart Home Assistant.

In the [NIO developer console](https://open-eu.nio.com/console), create or open a **Personal Application** using the OAuth Authorization Code flow. Set its redirect URI **exactly** to `https://my.home-assistant.io/redirect/oauth`. Personal applications receive their permitted scopes by default; the integration intentionally omits a `scope` parameter from authorization.

Then in Home Assistant, open **Settings → Devices & services → Add integration → NIO Open Telematics**. Enter your own application's Client ID and Client Secret, authorize with NIO, and enter a vehicle name and 17-character VIN. The official API does not document a vehicle-list endpoint, so VIN entry is currently required. If the integration is missing after restart, refresh the browser.

For manual installation, copy `custom_components/nio_telematics` into Home Assistant's `custom_components` directory and restart. Manual updates require repeating that copy.

## Contributing

Issues, [discussions](https://github.com/nicolasvangeluwe/nio-home-assistant/discussions), and cross-vehicle test reports are welcome. Please read [CONTRIBUTING.md](CONTRIBUTING.md) before a code change. Thanks to [@Laddvin](https://github.com/Laddvin) for identifying the useful SoC change feed and [@lubbyhst](https://github.com/lubbyhst) for independent testing and early improvements.
