# Open Telematics for NIO (EU)

Bring your NIO into Home Assistant using NIO's official EU Open Telematics API. This is an independent, unofficial, read-only integration—not affiliated with or endorsed by NIO. It shows vehicle data but does not control charging or the car.

## What works today

On my EU ET5 Touring, it receives live **battery SoC, remaining range, odometer and vehicle state**, plus the user-set charge limit and battery-pack voltage/current. Pack, cell and temperature-probe counts are available as diagnostics. Other optional sensors cover charging, trips, location, body and cabin data; what NIO supplies may differ by car.

**Charge limit:** the entity labelled *Maximum state of charge* comes from NIO's `max_soc` field—the limit set in the car (90% on my test car). *Charging target* is a different API field and has reported 0% while parked; do not use that value as your saved charge limit.

SoC, range and odometer keep their last valid readings when NIO sends sparse updates or Home Assistant restarts. Check each sensor's sample time before relying on it for an automation. See the [changelog](CHANGELOG.md) for technical details and release history.

NIO may deny individual telemetry feeds for some vehicles or accounts. The integration keeps any permitted vehicle data available and identifies denied feeds in its API availability diagnostics; it cannot override NIO's access decision. An actual expired OAuth grant still requests reauthentication.

## Optional car app

The **NIO Vehicle Dashboard** is an opt-in, mobile-friendly car view with SoC, range, odometer, charge limit and four history tabs. It does not replace any existing dashboard or control the car. It includes locally bundled images for **ET5, ET5 Touring, ET7, EL6, EL7, EL8 and legacy ES8**, with 51 model/colour choices. The existing ET5 Touring image remains the automatic default for current users. Other models use a neutral range metric icon until their own is available. Images are served by Home Assistant, without an external image service. Light and dark themes are supported.

After installing the integration:

1. In **Settings → Dashboards → Resources**, add `/nio_telematics/nio-vehicle-card.js` as a **JavaScript module**, then reload Home Assistant in your browser.
2. Edit a dashboard, choose **Add card → NIO Vehicle Dashboard**, and select your NIO. The simpler **NIO Vehicle** card remains available too.
3. The overview works with NIO alone. In **Settings**, choose the model, colour and language. SoC, range, odometer, charging state and charge limit use their NIO entities by default; you can select a different Home Assistant entity for any of them. EVCC users can choose a detected charger to fill connection and power in one step. Any HA charger can supply those two readings manually, and EVCC is not required.
4. To record trips and charging history, enable **Trip and charging history** and enter usable battery capacity and the range at 100% charge. Odometer and range sources must be available. History starts from actual recorded readings; it cannot reconstruct missing journeys. For home charging imports, the optional session entity must expose EVCC-compatible session data.

Setup, options, the dashboard and history follow Home Assistant's language by default, with a choice of 14 languages in dashboard settings. The new translations are machine drafted; wording corrections are welcome. Model and colour can be changed later in the vehicle's integration options or dashboard settings. Artwork is illustrative; availability of a paint on a particular car or model year should be checked against the car itself.

History is stored by Home Assistant outside HACS-managed integration files, so updates preserve it. Changing its energy inputs starts a new baseline without rewriting old trips. Five optional, advanced cost-source entities can split completed sessions when dated evidence is available. Missing history and the initial battery-stock price stay unknown, never €0 by assumption. Electricity-price and reimbursement entities are references, not a way to backprice old trips. Charging rules remain in Home Assistant.

Settings now has short help beside optional inputs and a **Backup & restore** section. An HA administrator can download a JSON copy of this car's dashboard settings and trip/charging history, then preview and explicitly confirm a restore to the same car. Export your current copy before replacing history. OAuth credentials and the full VIN are not exported, but the file contains private trip and cost details: store it securely. This is a dashboard/ledger backup, not a whole-Home-Assistant backup.

## Install

**For normal Home Assistant use, choose Direct NIO.** Companion is a separate experimental testing route, not a requirement for using this integration. See the testing instructions below before selecting it.

1. Open **HACS** and search for **Open Telematics for NIO (EU)**. Download the latest development release, then restart Home Assistant.
2. For a **Direct NIO** connection, create a **Personal Application** in the [NIO developer console](https://open-eu.nio.com/console) with OAuth Authorization Code. Set its only redirect URI to `https://my.home-assistant.io/redirect/oauth`. Although NIO's guide describes comma-separated callbacks, its live authorization service currently rejects an individual callback from such a list; use a separate NIO application for another client.
3. In **Settings → Devices & services**, add **Open Telematics for NIO (EU)** and choose **Direct NIO**. Enter the application's Client ID and Secret, authorize with NIO, then enter your car's name and VIN. The integration requests the read-only vehicle scopes automatically; you do not need to edit the authorization URL.

**Fallback:** If the integration does not appear in HACS, [add this repository as a custom repository](https://www.hacs.xyz/docs/faq/custom_repositories/) with category **Integration**, then download it and restart Home Assistant.

[![Open this repository in HACS](https://my.home-assistant.io/badges/hacs_repository.svg)](https://my.home-assistant.io/redirect/hacs_repository/?owner=nicolasvangeluwe&repository=nio-home-assistant&category=integration)

**Companion bridge (experimental — testing only):** This option remains available and selectable for development testing and future beta testers. It is not recommended for normal Home Assistant use at this stage. Unless you are participating in Companion testing, choose **Direct NIO** instead; you do not need a Companion account for this integration.

If you are testing Companion and already have a connected car there:

1. Open the [Companion Connections page](https://nio-companion-proof.nio-companion-backend.workers.dev/connections) and create a persistent **Home Assistant link** for that car.
2. In the integration's connection chooser, select **Companion account** and enter the link's Home Assistant credential.
3. Let the integration validate the car and its recent readings before confirming the connection.

The bridge reads Companion's cached car data; NIO authorization is managed through Companion, not through a NIO developer application or OAuth callback in Home Assistant. It currently supplies core vehicle readings only; additional Direct NIO sensors may be unavailable. Never enter a NIO password, application secret or short-lived proof token in the bridge form.

To move an **existing vehicle** to Companion, use **Add service → Change connection for an existing vehicle**, choose that vehicle, select Companion and confirm after its identity/data check. The existing entry, entity IDs, dashboard options and stored history are preserved. A HACS update does not switch sources automatically; if a prior private Companion build was replaced by a Direct-only release, install a Companion-capable release first and use this same-entry flow only if its saved source/credential did not survive. If Companion itself needs NIO authorization, reconnect on its Connections page; only a rejected Home Assistant bridge credential needs HA reauthentication.

You can enable additional sensors on the vehicle's **Entities** page. Existing Home Assistant enable/disable choices survive updates. For manual installation, copy `custom_components/nio_telematics` into your Home Assistant configuration and restart.

For a Direct NIO connection, to switch to a different Personal Application later, add its Client ID and Secret in Home Assistant's **Application Credentials**, then use **Reconfigure** on the existing vehicle integration. Select the new application and authorize it; the vehicle and its existing entities stay in place. An expired grant uses the same credential picker during reauthentication.

A Direct NIO upgrade that changes requested permissions may prompt **Reauthenticate** in Home Assistant. Complete that flow once using your saved NIO application credential; do not delete and re-add the vehicle. A completed login does not guarantee NIO permits every vehicle feed: if the API availability diagnostic still reports `access_denied`, include your model, country, integration version and sanitized endpoint results in a [bug report](https://github.com/nicolasvangeluwe/nio-home-assistant/issues).

## Try it and tell us what you find

If you own an EU NIO, please give it a try. A quick note with your **model, country and which readings work** is genuinely useful—especially from a car other than my ET5 Touring. Share your results in the [EU owner discussion](https://github.com/nicolasvangeluwe/nio-home-assistant/discussions/6), or [report a bug](https://github.com/nicolasvangeluwe/nio-home-assistant/issues). Do not share credentials, tokens, a full VIN or precise location.

This is a personal project built with substantial AI assistance and shared for other owners to use and improve. It is not affiliated with or endorsed by NIO or Home Assistant. Thanks to [@Laddvin](https://github.com/Laddvin) for spotting the first real data and finding the working SoC feed, and [@lubbyhst](https://github.com/lubbyhst) for independent testing and early improvements. Contributions are welcome; see [CONTRIBUTING.md](CONTRIBUTING.md).
