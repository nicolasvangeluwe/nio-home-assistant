# Open Telematics for NIO (EU)

Bring your NIO into Home Assistant using NIO's official EU Open Telematics API. This is an independent, unofficial, read-only integration—not affiliated with or endorsed by NIO. It shows vehicle data but does not control charging or the car.

## What works today

On my EU ET5 Touring, it receives live **battery SoC, remaining range, odometer and vehicle state**, plus the user-set charge limit and battery-pack voltage/current. Pack, cell and temperature-probe counts are available as diagnostics. Other optional sensors cover charging, trips, location, body and cabin data; what NIO supplies may differ by car.

**Native charging state:** The native NIO charging-state sensor may be unavailable for some vehicles or samples. We have observed it missing on an ET5 Touring, and an EL6 owner reported it unknown while the car was charging; the cause is not confirmed. You can select your charger’s charging-state binary sensor or W/kW power sensor in the NIO Vehicle Dashboard settings. This works with chargers integrated through Home Assistant, including ZHA; EVCC is not required.

**Battery SoC:** the integration reads `soc_status/changes`. The zero in `vehicle_status/latest` can be a placeholder and is ignored; a real 0% reading from `soc_status` is still valid. This has been the source since [v0.1.1-dev.7](CHANGELOG.md#011-dev7). An abrupt Direct joint 0%/0km reading after a positive battery reading is held for confirmation: after at least 60 seconds, a successful energy read must advance both source timestamps. Retained values keep their original timestamps and are marked unfresh while pending. A repeated cached event cannot confirm itself; initial and near-empty (at most 1%) zero readings remain valid immediately.

**Charge limit:** the entity labelled *Maximum state of charge* comes from NIO's `max_soc` field—the limit set in the car (90% on my test car). *Charging target* is a different API field and has reported 0% while parked; do not use that value as your saved charge limit.

SoC, range and odometer keep their last valid readings when NIO sends sparse updates or Home Assistant restarts. Check each sensor's sample time before relying on it for an automation. See the [changelog](CHANGELOG.md) for technical details and release history.

NIO may deny individual telemetry feeds for some vehicles or accounts. The integration keeps any permitted vehicle data available and identifies denied feeds in its API availability diagnostics; it cannot override NIO's access decision. A missing optional change feed does not stop polling the other feeds. An actual expired OAuth grant still requests reauthentication.

## Optional car app

The **NIO Vehicle Dashboard** is an optional sidebar page created and maintained by the integration. It has **Car / History / Settings** navigation, a persistent mobile bottom bar, and light and dark themes. The car appears above the content on desktop. Native and calculated ranges use equal typography; calculated range needs sufficient recorded energy and distance readings. History retains charging, trips, energy and parked records, with shared day, week, month and year controls using Home Assistant's timezone.

Images for **ET5, ET5 Touring, ET7, EL6, EL7, EL8 and legacy ES8** are bundled locally, including model/colour choices. Other models use a neutral range metric icon until their own is available. No external image service is required. The dashboard does not control the car or change charging rules.

After installing the integration:

1. In **Settings → Devices & services → Open Telematics for NIO → Configure**, enable the NIO dashboard for your vehicle. The integration adds one **NIO** sidebar page. You do not need to create or maintain a separate dashboard, YAML or JavaScript resource.
2. Enable it for additional NIO vehicles to use the same page with a vehicle selector. The advanced dashboard path defaults to `nio`; enabled vehicles should use the same path. An occupied path is reported without overwriting the existing dashboard or creating a duplicate with a different name.
3. The overview works with NIO alone. In **Settings**, choose the model, colour and language. SoC, range, odometer, charging state and charge limit use their NIO entities by default; you can select a different Home Assistant entity for any of them. EVCC users can choose a detected charger to fill connection and power in one step. Any HA charger can supply those two readings manually, and EVCC is not required.
4. To record trips and charging history, enable **Trip and charging history** and enter usable battery capacity and the range at 100% charge. Odometer and range sources must be available. History starts from actual recorded readings; it cannot reconstruct missing journeys. For home charging imports, the optional session entity must expose EVCC-compatible session data.

Setup, options, the dashboard and history follow Home Assistant's language by default, with a choice of 14 languages in dashboard settings. The new translations are machine drafted; wording corrections are welcome. Model and colour can be changed later in the vehicle's integration options or dashboard settings. Artwork is illustrative; availability of a paint on a particular car or model year should be checked against the car itself.

History is stored by Home Assistant outside HACS-managed integration files, so updates preserve it. Changing its energy inputs starts a new baseline without rewriting old trips. Five optional, advanced cost-source entities can split completed sessions when dated evidence is available. Missing history and the initial battery-stock price stay unknown, never €0 by assumption. Electricity-price and reimbursement entities are references, not a way to backprice old trips. Charging rules remain in Home Assistant.

Settings groups the existing controls into **Appearance & language**, **Vehicle readings**, **Charger & cost sources**, and **History & backup**, with help beside optional inputs. An HA administrator can download a JSON copy of this car's dashboard settings and trip/charging history, then preview and explicitly confirm a restore to the same car. Export your current copy before replacing history. OAuth credentials and the full VIN are not exported, but the file contains private trip and cost details: store it securely. This is a dashboard/ledger backup, not a whole-Home-Assistant backup.

Disabling the managed page preserves recorded history, entities and other dashboards. Existing embedded `NIO Vehicle Dashboard` and compact `NIO Vehicle` cards remain supported; their manual resource setup is only needed when embedding a card yourself. To reuse an existing dashboard URL, first back up and explicitly remove that old dashboard through HA, then choose its free path in NIO options. The integration never silently adopts or deletes a foreign dashboard.

## Costs, currencies and data gaps

New charging records default to Home Assistant's configured currency; an explicit
source or manual currency takes precedence. Each recorded session keeps its own
currency, even if the instance currency later changes.
Existing records retain their earlier EUR meaning; the integration does not
convert amounts or add different currencies into one monetary total. Monetary
inputs and manual charging entries show their currency explicitly. Changing an
input's currency clears its amounts so you can enter values in the new unit.

If you previously converted DKK to EUR in a session sensor as a workaround, supply
actual DKK amounts for new sessions after this update. Previously imported EUR
records keep their original numbers and currency. A currency conflict during
reimport preserves the existing recorded amount instead of silently replacing it.
Declare the session source's actual currency in its `currency` attribute (or a
currency-bearing unit). History shows a migration notice when an undeclared
source meets older imported amounts in another currency. This notice cannot
detect an old numeric conversion by itself: check the source's amounts too.
For API consumers, historical `*_eur` field names remain for compatibility;
the accompanying currency metadata identifies the amount's unit.

A missing driving interval is marked and skipped. It does not create an external
charging session or erase an already recorded battery price. Later valid readings
continue using the recorded weighted price when its basis remains valid. Missing
gap energy and expense are not filled in. Detected charging without a price and
missing opening prices retain their own price checks. Raw archived records are
preserved, including a bounded display correction for old post-gap overlap.
For a charging overlap, a fully known battery price is retained only when all
overlapping sessions are confirmed, priced, in the same currency, and completed
within the interval. Unknown driving energy stays unaccounted. The following
native energy anchor restarts independently; proven older v2 anchor errors are
corrected in derived views without rewriting the archive. Existing Manual/Ignore
decisions keep priority until Undo.

**Unaccounted usage** lists those intervals separately. In a trip's details you
can complete a gap with known energy and an optional actual cost, or ignore it.
Both choices can be undone. Manual entries are identified, do not create a
charging session, and do not change the original readings. Observed battery
change is shown separately and is not assumed to be driving consumption. Use
**Add charge** for a known charging receipt, including holiday charging.

In **Parked** details, choose an individual interval and **Mark as measurement
error** to review an optional exclusion. This removes that interval from parked
totals and battery-value allocation while keeping its original readings.
**Measurement-error decisions** lists exclusions with **Undo decision**, even
when no included parked records remain. A narrowly matching inferred charging
candidate may be included in the preview; confirmed charging receipts are never
removed by this action. Changed source evidence makes the old decision inactive
and visible for review. Existing false losses are not automatically guessed away.

## Polling

In the vehicle integration's **Configure** form, you can set the normal polling
interval or enable **Adaptive polling**. EVCC and the NIO dashboard are optional.
Existing installations keep their previous timing until you change these options:
15 seconds for Direct NIO, 30 seconds for Companion cache reads.

For adaptive polling, select a charger connection entity and either a charging
state entity, a power entity, or both. Use independent charger readings for the
same car, not this integration's own NIO sensors or templates based on them.
Power sensors can report W or kW. The default idle interval is 120 seconds.
Polling slows only while the inputs confirm connected and not charging. Charging,
unplugging, missing data or uncertain inputs return it to the normal interval.
Periodic checks continue; polling is never stopped just because the car is idle.

Unknown or unavailable inputs, restored/assumed states and explicit stale-data
flags use normal polling. An unchanged value with an older report timestamp is
not treated as a failure: some HA integrations only write states when they
change. If a charger integration silently freezes a value while keeping it
available, these inputs cannot reveal that; the periodic vehicle checks still
continue. The form accepts normal intervals up to 120
seconds and idle intervals up to 240 seconds; Companion's normal minimum is 30
seconds. These settings trade update frequency for fewer requests, and do not
make NIO publish vehicle data sooner.

For **Direct NIO**, this reduces NIO API requests. For **Companion**, it only
reduces Home Assistant's reads of the Companion cache; Companion's own NIO
collection schedule is unchanged. Polling mode, effective interval and the
reason for a fallback are included in the integration's diagnostics.

## Install

**For normal Home Assistant use, choose Direct NIO.** Companion is a separate experimental testing route, not a requirement for using this integration. See the testing instructions below before selecting it.

1. Open **HACS** and search for **Open Telematics for NIO (EU)**. Download the latest development release, then restart Home Assistant.
2. For a **Direct NIO** connection, create a **Personal Application** in the [NIO developer console](https://open-eu.nio.com/console) with OAuth Authorization Code. Set its only redirect URI to `https://my.home-assistant.io/redirect/oauth`. Although NIO's guide describes comma-separated callbacks, its live authorization service currently rejects an individual callback from such a list; use a separate NIO application for another client.
3. In **Settings → Devices & services**, add **Open Telematics for NIO (EU)** and choose **Direct NIO**. Enter the application's Client ID and Secret, authorize with NIO, then enter your car's name and VIN. The integration requests the read-only vehicle scopes automatically; you do not need to edit the authorization URL.

**Fallback:** If the integration does not appear in HACS, [add this repository as a custom repository](https://www.hacs.xyz/docs/faq/custom_repositories/) with category **Integration**, then download it and restart Home Assistant.

[![Open this repository in HACS](https://my.home-assistant.io/badges/hacs_repository.svg)](https://my.home-assistant.io/redirect/hacs_repository/?owner=nicolasvangeluwe&repository=nio-home-assistant&category=integration)

**Companion bridge (experimental — testing only):** This option remains available and selectable for development testing and future beta testers. It is not recommended for normal Home Assistant use at this stage. Unless you are participating in Companion testing, choose **Direct NIO** instead; you do not need a Companion account for this integration.

The linked Companion portal is currently a **private, fixed-owner proof**, not public beta registration. Creating an Auth0 account or passkey does not grant access. A successful Auth0 login can therefore return “Sign-in could not be completed” for an account outside that proof. This is separate from NIO vehicle permissions and is not a country restriction. New users should use **Direct NIO**; reinstalling this integration or repeatedly signing up will not unlock the private portal.

If you are the authorized proof owner and already have a connected car there:

1. Open the [Companion Connections page](https://nio-companion-proof.nio-companion-backend.workers.dev/connections) and create a persistent **Home Assistant link** for that car.
2. In the integration's connection chooser, select **Companion account** and enter the link's Home Assistant credential.
3. Let the integration validate the car and its recent readings before confirming the connection.

The bridge reads Companion's cached car data; NIO authorization is managed through Companion, not through a NIO developer application or OAuth callback in Home Assistant. It currently supplies core vehicle readings only; additional Direct NIO sensors may be unavailable. Never enter a NIO password, application secret or short-lived proof token in the bridge form.

To move an **existing vehicle** to Companion, use **Add service → Change connection for an existing vehicle**, choose that vehicle, select Companion and confirm after its identity/data check. The existing entry, entity IDs, dashboard options and stored history are preserved. A HACS update does not switch sources automatically; if a prior private Companion build was replaced by a Direct-only release, install a Companion-capable release first and use this same-entry flow only if its saved source/credential did not survive. If Companion itself needs NIO authorization, reconnect on its Connections page; only a rejected Home Assistant bridge credential needs HA reauthentication.

You can enable additional sensors on the vehicle's **Entities** page. Existing Home Assistant enable/disable choices survive updates. For manual installation, copy `custom_components/nio_telematics` into your Home Assistant configuration and restart.

For a Direct NIO connection, to switch to a different Personal Application later, add its Client ID and Secret in Home Assistant's **Application Credentials**, then use **Reconfigure** on the existing vehicle integration. Select the new application and authorize it; the vehicle and its existing entities stay in place. An expired grant uses the same credential picker during reauthentication.

A Direct NIO upgrade that changes requested permissions may prompt **Reauthenticate** in Home Assistant. Complete that flow once using your saved NIO application credential; do not delete and re-add the vehicle. A completed login does not guarantee NIO permits every vehicle feed: if the API availability diagnostic still reports `access_denied`, include your model, country, integration version and sanitized endpoint results in a [bug report](https://github.com/nicolasvangeluwe/nio-home-assistant/issues).

**Known Firefly limitation:** a Danish Firefly owner confirmed that the explicit read-only scope request and same-entry reauthentication work on v0.4.0-dev.4, but API availability still reports `permission_denied` for the tested feeds and supplies no usable telemetry. This account/model case remains unresolved upstream; another scope request, a Companion account or this compatibility update does not establish Firefly support. See [the test report in issue #3](https://github.com/nicolasvangeluwe/nio-home-assistant/issues/3#issuecomment-6401341231).

## Try it and tell us what you find

If you own an EU NIO, please give it a try. A quick note with your **model, country and which readings work** is genuinely useful—especially from a car other than my ET5 Touring. Share your results in the [EU owner discussion](https://github.com/nicolasvangeluwe/nio-home-assistant/discussions/6), or [report a bug](https://github.com/nicolasvangeluwe/nio-home-assistant/issues). Do not share credentials, tokens, a full VIN or precise location.

This is a personal project built with substantial AI assistance and shared for other owners to use and improve. It is not affiliated with or endorsed by NIO or Home Assistant. Thanks to [@Laddvin](https://github.com/Laddvin) for spotting the first real data and finding the working SoC feed, and [@lubbyhst](https://github.com/lubbyhst) for independent testing and early improvements. Thanks also to [@CasperSK89](https://github.com/CasperSK89) for the EL6 report and logs that helped fix polling recovery and the HA 2026.12 update-listener warning. Contributions are welcome; see [CONTRIBUTING.md](CONTRIBUTING.md).
