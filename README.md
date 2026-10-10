# NIO Open Telematics for Home Assistant

Bring NIO vehicle data into Home Assistant through NIO's **official EU Open Telematics API**. This is an experimental, read-only integration: it provides entities for dashboards and automations, but does not control the car or implement charging rules.

On the EU ET5 Touring used for testing, the integration has received **real native battery state of charge (SoC)**, remaining range, vehicle state and odometer readings. SoC is read directly from NIO—not calculated from range. Results may differ for another car or application.

## What entities do I get?

On a fresh installation, these sensors are enabled by default:

| Sensor | What it shows | Observed on the test car |
|---|---|---|
| Battery state of charge | NIO-reported battery percentage | **Yes—changing, non-zero values** |
| Remaining range | NIO-reported distance in km | **Yes—changing values** |
| Odometer | Total distance in km | **Yes** |
| Data timestamp | Timestamp of the latest energy record | **Yes** |
| API availability | Whether NIO's endpoint families respond, have no record, or deny access | **Yes** |
| Charging state | Whether the car is charging, if NIO reports it | Not yet verified as useful |
| Charging target | NIO-reported target percentage, if supplied | A zero placeholder was seen; not yet verified as useful |
| Maximum SoC | NIO-reported maximum percentage | 90% was observed; behavior over time is unverified |
| High-voltage battery current | Battery current in A | 0 A was observed while parked; changing values are unverified |
| Battery pack count | Number of reported packs | One pack was observed |
| Battery pack voltage | Voltage in V when exactly one pack is reported | 359 V was observed |
| Battery pack current | Current in A when exactly one pack is reported | 0 A was observed while parked |

You can also enable optional entities on the vehicle's **Entities** page in Home Assistant. They include:

| Area | Optional sensors | What we have actually seen |
|---|---|---|
| Vehicle | Vehicle state, comfort mode, speed, gear, operation mode, voltage/current and other status | State, mileage and comfort mode have supplied meaningful values; the remaining fields need more testing. |
| Battery and charging | Discharged energy, SoC lock, vehicle-to-load, battery-temperature extrema, pack cell count and temperature-probe count | NIO has supplied these field names, including 96 cells and 48 probes in one pack. Some values are zero or placeholders; useful changes are not verified for every sensor. |
| Driving and trips | Driving mode, steering, accelerator, trip distance and energy breakdown | No reliable trip or driving feed confirmed on the test car. |
| Body and cabin | Lock, lights, windows, fridge, HVAC, preheating, outside/cabin conditions | These endpoint families have mostly been denied by NIO on the test application. |
| Location and diagnostics | Position-related fields, battery-cell extrema, aftersales odometer and per-endpoint API diagnostics | Mostly denied or without a recent record on the test application. |

The full set of entity definitions is in [sensor.py](custom_components/nio_telematics/sensor.py). **Disabled by default is a Home Assistant display choice, not proof that a sensor is broken.** Home Assistant keeps existing owners' disabled/enabled choices after an update; previously disabled sensors may need to be enabled manually. Conversely, an entity may exist while NIO provides no useful value. Enable only the details you want to inspect. On cars reporting multiple packs, the per-pack voltage/current/count sensors stay empty rather than incorrectly combining readings; the battery-pack-count sensor keeps the separate pack details as attributes.

SoC and range retain the last valid reading across sparse responses and restarts. Their attributes identify the source sample and whether the displayed value was retained; check its age before relying on it for an automation. An API request error can still make the integration temporarily unavailable. The SoC sensor's `observed_fields` attribute lists the energy *field names* your car has sent. Polling discovers available changes more quickly, but cannot make NIO publish fresh vehicle data. See the [changelog](CHANGELOG.md) for the polling, retention and release details.

The observations above are from one EU ET5 Touring on 10 October 2026, not a promise of current availability or support for every NIO model. NIO has returned `permission_denied` for several optional endpoints; the exact upstream reason is unknown.

## Install with HACS

[![Open this repository in HACS](https://my.home-assistant.io/badges/hacs_repository.svg)](https://my.home-assistant.io/redirect/hacs_repository/?owner=nicolasvangeluwe&repository=nio-home-assistant&category=integration)

If the button does not open your Home Assistant instance:

1. In **HACS**, open the three-dot menu → **Custom repositories**.
2. Add `https://github.com/nicolasvangeluwe/nio-home-assistant` as an **Integration**.
3. Open **NIO Open Telematics**, select **Download**, and choose the latest development release.
4. Restart Home Assistant.

In the [NIO developer console](https://open-eu.nio.com/console), create a **Personal Application** using OAuth Authorization Code and set its redirect URI exactly to `https://my.home-assistant.io/redirect/oauth`. Then open **Settings → Devices & services → Add integration → NIO Open Telematics** in Home Assistant. Enter your application's Client ID and Client Secret, authorize with NIO, and enter your vehicle name and 17-character VIN. The official API does not document a vehicle-list endpoint, so VIN entry is currently required. The integration omits the OAuth `scope` parameter to use NIO's documented default personal-app permissions.

For manual installation, copy `custom_components/nio_telematics` into Home Assistant's `custom_components` directory and restart. Manual updates require repeating that copy.

## Testing and contributing

If you use another eligible EU NIO, a short report of your model, country and which entities provide real values would help enormously. Add it to the [EU telemetry discussion](https://github.com/nicolasvangeluwe/nio-home-assistant/discussions/6) or open an [issue](https://github.com/nicolasvangeluwe/nio-home-assistant/issues) for a reproducible bug. Never post credentials, tokens, a full VIN or precise location.

This is an independent personal project created with substantial AI assistance and shared because it may help other owners. It is **not affiliated with or endorsed by NIO or Home Assistant**. Review the code and protect your data; it is still development software. Code contributions are welcome—please read [CONTRIBUTING.md](CONTRIBUTING.md). Thanks to [@Laddvin](https://github.com/Laddvin) for pointing to the useful SoC change feed and [@lubbyhst](https://github.com/lubbyhst) for independent testing and early improvements.
