# NIO Open Telematics for Home Assistant

Bring your NIO into Home Assistant using NIO's official EU Open Telematics API. This is an independent, read-only integration: it shows vehicle data but does not control charging or the car.

## What works today

On my EU ET5 Touring, it receives live **battery SoC, remaining range, odometer and vehicle state**, plus the user-set charge limit and battery-pack voltage/current. Pack, cell and temperature-probe counts are available as diagnostics. Other optional sensors cover charging, trips, location, body and cabin data; what NIO supplies may differ by car.

**Charge limit:** the entity labelled *Maximum state of charge* comes from NIO's `max_soc` field—the limit set in the car (90% on my test car). *Charging target* is a different API field and has reported 0% while parked; do not use that value as your saved charge limit.

SoC and range keep their last valid readings when NIO sends sparse updates. Check each sensor's sample time before relying on it for an automation. See the [changelog](CHANGELOG.md) for technical details and release history.

NIO may deny individual telemetry feeds for some vehicles or accounts. The integration keeps any permitted vehicle data available and identifies denied feeds in its API availability diagnostics; it cannot override NIO's access decision. An actual expired OAuth grant still requests reauthentication.

An optional **NIO Vehicle card** shows the key readings in a compact car view. It uses bundled artwork, follows light/dark themes and offers 14 interface languages; it needs no external image service. To use it, go to **Settings → Dashboards → Resources**, add `/nio_telematics/nio-vehicle-card.js` as a **JavaScript module**, then refresh Home Assistant. The **NIO Vehicle** card will appear in the card picker; alternatively use a manual card with `type: custom:nio-vehicle-card`. Choose a model and language in the card's Settings or the integration's **Configure** dialog. No existing dashboard is replaced.

EVCC connection, power and session-history entities can be selected if you have them. Battery capacity and full-charge range enable the optional experimental trip/charging ledger, whose history survives HACS updates. Changing these energy inputs starts a new baseline without rewriting old trips. Electricity-price and reimbursement entities, if selected, are shown as reference values; they do not calculate historical costs. Everything on the card is read-only, and charging rules stay in Home Assistant.

## Install

[![Open this repository in HACS](https://my.home-assistant.io/badges/hacs_repository.svg)](https://my.home-assistant.io/redirect/hacs_repository/?owner=nicolasvangeluwe&repository=nio-home-assistant&category=integration)

1. Add this repository to HACS as an **Integration** ([how to add a custom repository](https://www.hacs.xyz/docs/faq/custom_repositories/)), download the latest development release, then restart Home Assistant.
2. Create a **Personal Application** in the [NIO developer console](https://open-eu.nio.com/console) with OAuth Authorization Code. Set its redirect URI to `https://my.home-assistant.io/redirect/oauth`.
3. In **Settings → Devices & services**, add **NIO Open Telematics**. Enter the application's Client ID and Secret, authorize with NIO, then enter your car's name and VIN.

You can enable additional sensors on the vehicle's **Entities** page. Existing Home Assistant enable/disable choices survive updates. For manual installation, copy `custom_components/nio_telematics` into your Home Assistant configuration and restart.

## Try it and tell us what you find

If you own an EU NIO, please give it a try. A quick note with your **model, country and which readings work** is genuinely useful—especially from a car other than my ET5 Touring. Share your results in the [EU owner discussion](https://github.com/nicolasvangeluwe/nio-home-assistant/discussions/6), or [report a bug](https://github.com/nicolasvangeluwe/nio-home-assistant/issues). Do not share credentials, tokens, a full VIN or precise location.

This is a personal project built with substantial AI assistance and shared for other owners to use and improve. It is not affiliated with or endorsed by NIO or Home Assistant. Thanks to [@Laddvin](https://github.com/Laddvin) for spotting the first real data and finding the working SoC feed, and [@lubbyhst](https://github.com/lubbyhst) for independent testing and early improvements. Contributions are welcome; see [CONTRIBUTING.md](CONTRIBUTING.md).
