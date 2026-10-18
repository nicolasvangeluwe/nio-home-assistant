# Open Telematics for NIO (EU)

Bring your NIO into Home Assistant using NIO's official EU Open Telematics API. This is an independent, unofficial, read-only integration—not affiliated with or endorsed by NIO. It shows vehicle data but does not control charging or the car.

## What works today

On my EU ET5 Touring, it receives live **battery SoC, remaining range, odometer and vehicle state**, plus the user-set charge limit and battery-pack voltage/current. Pack, cell and temperature-probe counts are available as diagnostics. Other optional sensors cover charging, trips, location, body and cabin data; what NIO supplies may differ by car.

**Charge limit:** the entity labelled *Maximum state of charge* comes from NIO's `max_soc` field—the limit set in the car (90% on my test car). *Charging target* is a different API field and has reported 0% while parked; do not use that value as your saved charge limit.

SoC, range and odometer keep their last valid readings when NIO sends sparse updates or Home Assistant restarts. Check each sensor's sample time before relying on it for an automation. See the [changelog](CHANGELOG.md) for technical details and release history.

NIO may deny individual telemetry feeds for some vehicles or accounts. The integration keeps any permitted vehicle data available and identifies denied feeds in its API availability diagnostics; it cannot override NIO's access decision. An actual expired OAuth grant still requests reauthentication.

## Optional car app

The **NIO Vehicle Dashboard** is an opt-in, mobile-friendly car view with SoC, range, odometer, charge limit and four history tabs. It does not replace any existing dashboard or control the car. The first illustrated model is **ET5 Touring**; other models use a neutral NIO icon until their own artwork is added. Its AI-generated illustration is bundled locally, not fetched from NIO or another service. Light and dark themes are supported.

After installing the integration:

1. In **Settings → Dashboards → Resources**, add `/nio_telematics/nio-vehicle-card.js` as a **JavaScript module**, then reload Home Assistant in your browser.
2. Edit a dashboard, choose **Add card → NIO Vehicle Dashboard**, and select your NIO. The simpler **NIO Vehicle** card remains available too.
3. The overview works with NIO alone. In **Settings**, choose the model and language. SoC, range, odometer, charging state and charge limit use their NIO entities by default; you can select a different Home Assistant entity for any of them. EVCC users can choose a detected charger to fill connection and power in one step. Any HA charger can supply those two readings manually, and EVCC is not required.
4. To record trips and charging history, enable **Trip and charging history** and enter usable battery capacity and the range at 100% charge. Odometer and range sources must be available. History starts from actual recorded readings; it cannot reconstruct missing journeys. For home charging imports, the optional session entity must expose EVCC-compatible session data.

The overview offers 14 European language choices. History is Dutch on a Dutch installation and uses English for other languages; further translations are in progress. The ET5 Touring image currently has one colour. Model-specific images and colours are planned, not silently simulated.

History is stored by Home Assistant outside HACS-managed integration files, so updates preserve it. Changing its energy inputs starts a new baseline without rewriting old trips. Five optional, advanced cost-source entities can split completed sessions when dated evidence is available. Missing history and the initial battery-stock price stay unknown, never €0 by assumption. Electricity-price and reimbursement entities are references, not a way to backprice old trips. Charging rules remain in Home Assistant.

Settings now has short help beside optional inputs and a **Backup & restore** section. An HA administrator can download a JSON copy of this car's dashboard settings and trip/charging history, then preview and explicitly confirm a restore to the same car. Export your current copy before replacing history. OAuth credentials and the full VIN are not exported, but the file contains private trip and cost details: store it securely. This is a dashboard/ledger backup, not a whole-Home-Assistant backup.

## Install

[![Open this repository in HACS](https://my.home-assistant.io/badges/hacs_repository.svg)](https://my.home-assistant.io/redirect/hacs_repository/?owner=nicolasvangeluwe&repository=nio-home-assistant&category=integration)

1. Add this repository to HACS as an **Integration** ([how to add a custom repository](https://www.hacs.xyz/docs/faq/custom_repositories/)), download the latest development release, then restart Home Assistant.
2. Create a **Personal Application** in the [NIO developer console](https://open-eu.nio.com/console) with OAuth Authorization Code. Set its only redirect URI to `https://my.home-assistant.io/redirect/oauth`. Although NIO's guide describes comma-separated callbacks, its live authorization service currently rejects an individual callback from such a list; use a separate NIO application for another client.
3. In **Settings → Devices & services**, add **Open Telematics for NIO (EU)**. Enter the application's Client ID and Secret, authorize with NIO, then enter your car's name and VIN.

You can enable additional sensors on the vehicle's **Entities** page. Existing Home Assistant enable/disable choices survive updates. For manual installation, copy `custom_components/nio_telematics` into your Home Assistant configuration and restart.

To switch to a different NIO Personal Application later, add its Client ID and Secret in Home Assistant's **Application Credentials**, then use **Reconfigure** on the existing vehicle integration. Select the new application and authorize it; the vehicle and its existing entities stay in place. An expired grant uses the same credential picker during reauthentication.

## Try it and tell us what you find

If you own an EU NIO, please give it a try. A quick note with your **model, country and which readings work** is genuinely useful—especially from a car other than my ET5 Touring. Share your results in the [EU owner discussion](https://github.com/nicolasvangeluwe/nio-home-assistant/discussions/6), or [report a bug](https://github.com/nicolasvangeluwe/nio-home-assistant/issues). Do not share credentials, tokens, a full VIN or precise location.

This is a personal project built with substantial AI assistance and shared for other owners to use and improve. It is not affiliated with or endorsed by NIO or Home Assistant. Thanks to [@Laddvin](https://github.com/Laddvin) for spotting the first real data and finding the working SoC feed, and [@lubbyhst](https://github.com/lubbyhst) for independent testing and early improvements. Contributions are welcome; see [CONTRIBUTING.md](CONTRIBUTING.md).
