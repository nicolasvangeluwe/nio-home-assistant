# NIO Open Telematics for Home Assistant

Early development foundation for a read-only Home Assistant integration using
NIO's official EU Open Telematics API.

## Project status and disclosure

This is an independent, unofficial personal project created to meet the
author's own Home Assistant needs and shared in case it is useful to others.
Its design, code, tests, and documentation have been produced with substantial
assistance from AI and reviewed through automated validation and hands-on
testing. It does not claim to be an official NIO product, a professionally
supported integration, or affiliated with NIO, Home Assistant, or OpenAI.

It is experimental software. Review it, protect your credentials and vehicle
data, and use it at your own risk.

## EU NIO owners: we need your help

> [!IMPORTANT]
> **EU NIO owners: we need you.**
>
> We all want reliable battery SoC in Home Assistant, but the official API is
> currently returning missing or incorrect telemetry. We need more owners,
> vehicles, and countries to produce clear evidence and make the problem
> visible enough for NIO to investigate and fix it.
>
> Install the current development release, compare its values with the car or
> NIO app, and share your vehicle model, EU country, application type, and
> redacted endpoint results in the dedicated [EU telemetry test-report
> discussion](https://github.com/nicolasvangeluwe/nio-home-assistant/discussions/6).
>
> If you also receive SoC `0`, `resource_not_found`, or unexpected
> `permission_denied` responses, please report the behaviour to
> [`api@nio.io`](mailto:api@nio.io) or through your national NIO contact or
> importer. Ask for a ticket/reference number and add it to the discussion. If
> you know a more direct route to NIO's Open Telematics/API team, an
> introduction would be enormously helpful.
>
> Never post credentials, tokens, a full VIN, or precise location data. One
> report is a curiosity; a fleet of matching reports is evidence. EU NIO
> owners, rally—we are legion, and we need you. 😄

Current development release (`0.1.1-dev.7`):

- polls every documented read-only telemetry category that can provide useful
  Home Assistant state: body, dynamics, location, trip, energy, cabin,
  powertrain, diagnostics, and aftersales odometer data;
- creates 64 stable scalar sensors and 16 disabled diagnostic endpoint sensors;
- preserves variable-length/nested data such as battery cells, motor lists,
  window faults, door structures, and alarm signals as attributes on the
  corresponding disabled diagnostic sensor;
- uses one coordinator and one Home Assistant device per VIN;
- redacts credentials and vehicle identifiers from diagnostics;
- handles authentication, permission, rate-limit, envelope, and transport
  errors separately, and keeps unavailable optional feeds from breaking feeds
  that do work.

`0.1.1-dev.4` fixed NIO's HTTP-success `invalid_grant` refresh response:
Home Assistant now opens its native reauthentication repair for rejected
authorization, while temporary token-service failures remain retryable. This
does not change NIO's upstream SoC or endpoint-permission behavior.

`0.1.1-dev.5` keeps the last valid official remaining-range reading when a
later sparse update has no range, including after a restart. A retained value
is marked with `data_retained` and `last_valid_sample` attributes. It may be
stale; check freshness before using it for charging decisions. The integration
does **not** convert range into SoC: that calibration is specific to a car and
belongs in the owner's Home Assistant configuration.
`0.1.1-dev.6` also recovers a numeric range from the sensor's own recent
Recorder history on the first upgrade when an older version had ended at
`unknown`. This migration fallback is skipped if Recorder is unavailable.

`0.1.1-dev.7` reads official SoC from the sparse `soc_status/changes` feed,
retains the last valid reading between events and across restarts, and no longer
lets a placeholder zero from `vehicle_status/latest` override it. A fresh
installation may show SoC as unknown until NIO sends a real change event;
`last_valid_sample` and `data_retained` indicate its age and retention. This is
separate from any owner-specific range-to-charge calculation. The tested ET5
Touring's actual SoC feed still needs live verification.

Most detailed entities are disabled by default to avoid flooding a new Home
Assistant installation. **Disabled does not mean broken or denied**; it is only
the default Home Assistant entity-registry setting. The enabled diagnostic
**API availability** sensor shows which endpoint families work, have no recent
data, are denied by NIO, or returned another error. Once enabled, each detailed
telemetry sensor reports its source endpoint and that endpoint's current status
as attributes. The existing battery/range/charging entities keep their original
IDs.

## Live API status

The table below is based on hands-on testing against one EU NIO ET5 Touring,
not on what the API merely promises. Other vehicle models or accounts may
behave differently.

| Data | Implemented | Observed result |
|---|---:|---|
| OAuth authorization, refresh and user info | Yes | Working after restart; a rejected refresh grant now triggers native HA reauthentication (cause of NIO's rejection unknown) |
| Latest vehicle timestamp/state/mileage | Yes | Working; timestamp and mileage advanced after driving; raw mileage is kilometres |
| Battery SoC in latest vehicle status | Yes | Returned `0` instead of the vehicle's real SoC; no longer used for the SoC sensor in dev.7 |
| Charging state, battery current/voltage | Yes | Missing, null, or zero in the latest-status response |
| SoC/range/charging-target change feed | Yes | Range now appears intermittently on the tested ET5 Touring; absent polls still occur. The dev.7 SoC feed selection is not yet verified live on this car. |
| Body, lights, windows, position, trips, cells, cabin, motor, alarms | Yes | NIO currently returns `permission_denied` |
| Driving and battery-extremum change feeds | Yes | Request accepted, but currently returns no recent record |
| Aftersales odometer reports | Yes | NIO currently returns `permission_denied`; the working latest-status mileage is used for the normal odometer sensor |

### Current live sensor diagnosis

This diagnosis was observed with `v0.1.1-dev.1` on one EU ET5 Touring on
2026-09-06. It describes this app/account/vehicle combination and may differ for
another NIO application or vehicle.

| Diagnosis | Sensors/data |
|---|---|
| Working and meaningful | API availability, data timestamp, odometer (`5077 km`), vehicle state (`PARKED_VEHICLE`), comfort mode |
| Plausible but not yet verified while driving | Speed (`0` while parked) |
| Returned, but not currently trustworthy | SoC (`0`), charging state (null), remaining range (missing), charging target (missing), operation mode (null), total voltage/current (`0`), DC-DC status (null), insulation resistance (`0`), gear (unmapped raw `0`) |
| Endpoint works but has no recent event record | Driving mode, steering angle/speed, accelerator position, average/minimum/maximum speed, highest/lowest cell voltage, highest/lowest battery temperature, discharged energy, SoC lock limit/status, vehicle-to-load status |
| Endpoint denied by NIO | Vehicle lock/doors, fridge, lights/windows, position/GPS, trips and trip energy, cell details, heating/HVAC, driving motors, alarms, aftersales odometer |

`permission_denied` is returned by the official NIO API. It is **not** a Home
Assistant user-rights problem. It means NIO refuses that endpoint for the
current OAuth application/token/vehicle combination. Because authorization
succeeds using NIO's documented default personal-app grant, the current
evidence points to an upstream NIO entitlement or vehicle/application
provisioning restriction. Only NIO can confirm the exact backend reason.

The VIN was independently verified because vehicle state and mileage were
correct. If a granted scope is missing, the integration keeps setup active and
flags the affected feed as `permission_denied`, so available data keeps working
while the NIO-side restriction is investigated. A detailed case has been sent
to NIO and feedback is still pending. If you have faster access to NIO's Open
Telematics API support or can test another eligible EU vehicle, please open a
GitHub issue and help move the investigation forward. Never post credentials,
tokens, a full VIN, or precise location data.

The config flow now uses locally supplied NIO application credentials, OAuth
Authorization Code + PKCE, NIO's HTTP Basic token exchange, wrapped token
response, and automatic refresh through Home Assistant's OAuth session. The
official reference exposes vehicle telemetry by VIN and does not document a
vehicle-list endpoint, so setup validates a manually entered VIN after consent.
The OAuth authorization request omits `scope`, using NIO's documented default
of the application's full permitted scope set. When this permission policy
changes, Home Assistant requests a single native reauthorization flow and
records the permission revision after it completes. Individual optional feeds
that NIO still denies remain isolated as
`permission_denied` rather than taking the integration offline.
Automated tests, hassfest, and HACS repository validation run on every push.

Never commit a Client ID, Client Secret, VIN, access token, refresh token, or
diagnostic payload containing personal vehicle data.

## Installation and configuration

### Install with HACS

HACS must already be installed in Home Assistant.

[![Open your Home Assistant instance and open this repository in
HACS](https://my.home-assistant.io/badges/hacs_repository.svg)](https://my.home-assistant.io/redirect/hacs_repository/?owner=nicolasvangeluwe&repository=nio-home-assistant&category=integration)

Select the button above for the easiest installation. If the link cannot reach
your Home Assistant instance, add the repository manually:

1. Open **HACS** in Home Assistant.
2. Open the three-dot menu in the upper-right corner and select
   **Custom repositories**.
3. Enter this repository URL:
   `https://github.com/nicolasvangeluwe/nio-home-assistant`
4. Select **Integration** as the category, then select **Add**.
5. Open **NIO Open Telematics** in HACS and select **Download**. Choose the
   latest development release when HACS asks for a version.
6. Restart Home Assistant after the download finishes.

These steps follow the official [HACS custom-repository
instructions](https://www.hacs.xyz/docs/faq/custom_repositories/).

### Configure NIO and Home Assistant

In the [NIO Open Telematics developer
console](https://open-eu.nio.com/console), create or open a Personal
Application using the OAuth Authorization Code flow and set its redirect URI
exactly to:

`https://my.home-assistant.io/redirect/oauth`

Then:

1. In Home Assistant, open **Settings > Devices & services**.
2. Select **Add integration**, search for **NIO Open Telematics**, and select
   it.
3. Enter the Personal Application's Client ID and Client Secret when prompted.
4. Complete NIO authorization, then enter the vehicle name and 17-character
   VIN.

If the integration is missing from **Add integration** after the restart,
clear or hard-refresh the browser cache and try again.

### Manual installation

As an alternative to HACS, copy `custom_components/nio_telematics` into Home
Assistant's `custom_components` directory and restart Home Assistant. Future
updates must then also be installed manually.

## Changelog

See [CHANGELOG.md](./CHANGELOG.md) for public release notes and version history.

## Contributing

Please read [CONTRIBUTING.md](./CONTRIBUTING.md) and open an issue or discussion
before starting code changes. Testing with other eligible NIO applications and
vehicle models is especially useful.

## Acknowledgements

Special thanks to [@lubbyhst](https://github.com/lubbyhst) for early
cross-vehicle testing, clear issue reports, proposed OAuth and documentation
improvements, and sharing independent NIO API results.
