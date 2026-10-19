# Changelog

The changelog is the authoritative release history for this integration.
Use this before releases and when opening PRs.

## Unreleased

- Align native SoC with odometer source timestamps instead of pairing a newer
  percentage with an older distance report. Retain unchanged SoC reports,
  reconcile bounded late arrival readings, and keep later stationary losses
  outside the driving trip. Treat sparse native intervals as unknown rather
  than measured consumption.
- Preserve charging/source boundaries, stored trip IDs and raw evidence during
  audited native-trip repair. Restore the optional dashboard's grouped-trip,
  battery-history and driving-segment snapshot fields.
- Keep the already-resolved timezone and rolling 100 km calculations from
  v0.4.0-dev.4. These changes are source-only until a future release and HA
  installation are separately verified.

## 0.4.0-dev.4

- Pass Home Assistant's already-resolved timezone object to the optional car
  ledger and backup validation. Local-day grouping remains unchanged, without
  potentially blocking zone-file reads on the Home Assistant event loop. This
  addresses the HACS review feedback from Frenck.
- Carry the verified native-SoC rolling 100 km range calculation into the
  maintained package. A charge no longer resets that driving-distance window;
  source epochs and incomplete energy still remain distinct. This preserves
  the narrow fix already active on the maintainer's Home Assistant instance.

## 0.4.0-dev.3

- Request the NIO Personal Application's ten read-only vehicle scopes during
  initial authorization and reauthentication, including Vehicle and Energy.
  Home Assistant's PKCE fields are preserved. Owners no longer need to edit
  an OAuth URL to obtain telemetry access.
- Require one native Home Assistant reauthentication for existing entries so
  their tokens receive the new scope request; preserve the vehicle entry,
  entity IDs, dashboard preferences and trip/charging history.
- Document that a successful login may still leave NIO-denied feeds unavailable.
  The Danish Firefly `access_denied` report persisted even with explicit scopes
  and is not claimed fixed by this change.
- Remove the Home Assistant badge from the locally bundled NOMI-inspired icon
  and use a transparent background while preserving its face and underline.
  Add a geometry-matched light variant for dark Home Assistant themes.

## 0.4.0-dev.2

- Show each saved Home Assistant application credential's own name in the
  reauthentication/reconfiguration picker, with its client ID as a fallback
  when no name was saved. The selected implementation and OAuth behavior are
  unchanged.
- Reduce and separate the upper-left Home Assistant badge on the locally
  bundled integration icon. The approved face and underline are unchanged.
- NIO's live authorization service rejected individually requested callback
  URLs when two callbacks were stored comma-separated, despite its published
  setup guidance. For now, use a dedicated NIO Personal Application with only
  `https://my.home-assistant.io/redirect/oauth` as its redirect URI. The
  existing HA vehicle entry can be reconfigured to its new credentials; its
  entity IDs, dashboard preferences, and stored trip/charging history remain.

## 0.4.0-dev.1

- Add Home Assistant's application-credential picker to reauthentication and
  reconfiguration. Owners can choose a replacement NIO Personal Application
  without removing their vehicle; the existing entry, entity IDs, dashboard
  settings and trip/charging history remain in place. The selected client and
  token are saved only after successful OAuth authorization.
- Rename the displayed integration and HACS repository to **Open Telematics
  for NIO (EU)** to make its independent, unofficial status clearer. The
  technical domain and existing entity IDs are unchanged.
- Includes the NOMI-inspired, locally bundled icon introduced in dev.3.
  The separate HACS catalogue image is not changed by this release.

## 0.3.0-dev.3

- Replace the bundled local integration icon with the selected NOMI-inspired
  face, underline and upper-left Home Assistant marker. Include 256 px and
  512 px icon files and retain full-resolution artwork for the separate
  companion-app handoff.
- This changes artwork only. Vehicle polling, entities, dashboard behavior,
  saved preferences and trip/charging history are unchanged. The HACS
  catalogue image is managed separately from the locally bundled icon.

## 0.3.0-dev.2

- Refine the optional ET5 Touring dashboard hero with a locally bundled,
  front-three-quarter studio render, natural contact shadow and larger mobile
  placement. Remove the stacked synthetic shadow that made the prior image
  look toy-like. The existing artwork URL remains available for older cached
  cards.
- No changes to vehicle polling, entity IDs, the owner's separate Car board,
  ledger calculations or saved history.

## 0.3.0-dev.1

- Add contextual help beside optional dashboard inputs, including charger,
  calibration and history settings. NIO remains the default vehicle source;
  EVCC is optional. English, Dutch, German and French help is included, with
  English fallback for the other overview languages.
- Add a per-car, versioned JSON export of dashboard preferences and the
  optional trip/charging archive. OAuth credentials, tokens and the raw VIN
  are excluded. The file contains travel and cost history and should be kept
  private.
- Add an admin-only restore with vehicle matching, schema/source validation,
  an archive-size preview, explicit replacement confirmation and a stale-
  revision guard. Restore preserves unrelated config-entry options and rolls
  back the previous archive/settings if applying the backup fails. A backup
  without history changes preferences only; it does not erase saved trips.
- Keep the existing Car dashboard, vehicle entity IDs, telemetry polling and
  charging policy unchanged.

## 0.2.0-dev.5

- Make every dashboard/ledger input selectable per vehicle while retaining the
  discovered NIO entities as defaults. Existing EVCC and ledger settings remain
  compatible; changing energy sources begins a new ledger baseline without
  rewriting archived trips.
- Add an EVCC quick picker for matching charger connection/power entities, but
  also accept any Home Assistant charger with on/off or connected/disconnected
  state and power in W or kW. EVCC-compatible session history and five recorded
  cost sources remain optional and explicit; absent prices are never zero.
- Give the ET5 Touring image a softer ground shadow and use the approved
  lightweight power icon. The ET5-specific range silhouette is no longer shown
  for other models, which retain neutral artwork until their own assets exist.
- Add mapping and frontend regression checks. Vehicle polling, OAuth, entity
  IDs, charging policy and the owner's separate Car dashboard are unchanged.

## 0.2.0-dev.4

- Retain the last valid odometer reading when NIO's latest vehicle-status
  response omits mileage or uses an invalid marker. Keep the mileage's own
  source timestamp instead of falsely dating it to a newer sparse response.
- Restore the last valid odometer reading after Home Assistant restarts,
  including a one-time lookup of recent Recorder history if an older release
  left the entity `unknown`. Mark retained readings and preserve the entity ID.
- Add regression tests for sparse responses, invalid markers and recovery.
  SoC/range polling, ledger history, charging policy and dashboard layout are
  unchanged.

## 0.2.0-dev.3

- Request NIO's documented default ten-minute `soc_status/changes` window
  without explicit timestamps. Live NIO responses on October 13 rejected the
  equivalent timestamped request as `invalid_param`, preventing new SoC and
  range polls after restart. Sparse-field merging, separate source timestamps,
  retained last-valid values and the 15-second request pacing are unchanged.
- Add a regression assertion that the scheduled SoC request sends no query
  parameters. This does not change vehicle control or charging policy.

## 0.2.0-dev.2

- Show a live, provisional charging session as ongoing in the optional vehicle
  dashboard. Its changing projection timestamp is no longer displayed as a
  completed end time, and the unfinished session is not offered for receipt
  editing. Completed sessions keep their normal dates and controls.
- Refresh the bundled history module with this frontend change. Vehicle
  telemetry, polling, entity IDs, archived ledger data and existing dashboards
  are unchanged.

## 0.2.0-dev.1

- Add an opt-in, app-style NIO Vehicle Dashboard alongside the existing compact
  card and existing user dashboards. Its ET5 Touring illustration is bundled
  locally; other models deliberately show a neutral NIO icon instead of
  misleading ET5 artwork. Model and language remain per-vehicle choices.
- Show native SoC, range, odometer and charging information without EVCC.
  Optional EVCC readings and the existing, separately enabled trip/charging
  ledger add context. An empty ledger shows a clear Settings route; it does not
  invent trips, prices or history. Its primary labels use Dutch for Dutch users
  and English otherwise, with locale-aware numbers and dates.
- Preserve the existing compact card, entity IDs, telemetry/polling behavior,
  ledger archive, and the maintainer's personal Car dashboard. Correct the
  ledger's trip explanation so it does not claim every trip is range-derived
  after native SoC became available.
- Add frontend and integration regression checks for a no-EVCC setup, artwork
  selection, localization and bundled static assets. This is a development
  release for early testers, not a claim that every NIO model or colour has
  matching artwork.

## 0.1.1-dev.21

- Correct a historical false 1 km trip caused by a late odometer update near
  the end of a real drive. An admin-only, validated replay can merge the short
  incomplete tail into its preceding native-SoC trip while retaining the real
  trip ID, all raw samples and unrelated charging/history records. Future
  updates within the trip-idle window remain part of one trip; genuine later
  drives still start a new trip.
- Show an identified ongoing EVCC home session before it appears in completed
  session history. Its live card is a provisional view of the current energy
  and cost readings, not a completed charging record or new archived charge.
  It becomes the normal historical session when EVCC publishes the completed
  row. Prevent editing the unfinished entry as an archived receipt.
- Add regression coverage for late odometer/SoC alignment, idempotent merging,
  active-to-completed session transition and preserved evidence. No vehicle
  API calls, polling cadence, entity IDs or charging policy change.

## 0.1.1-dev.20

- Fix the optional Car ledger's native-SoC trip calculations. Fresh unchanged
  SoC and odometer reports now establish distance-window evidence; asynchronous
  readings no longer imply parking merely because an odometer value was cached.
  Short stops and small SoC corrections no longer invalidate an entire trip.
- Add an admin-only, idempotent repair operation for a selected archived native
  trip using retained timestamped source reports. It preserves the trip ID,
  other archives, charging records and original samples. Energy remains an
  estimate from whole-percent SoC; a battery correction cannot be identified
  as driving consumption with certainty.
- Bundle the previously HA-local recorded charging-cost split and ongoing-home-
  session handling so HACS updates preserve these capabilities and their
  separately stored history. Unknown initial battery value remains unknown;
  this release does not invent a driving price or alter charging policy.
- Add regression tests for trip replay, short stops, SoC rebounds, persistence,
  active-session completion and cost allocation. No entity IDs change.

## 0.1.1-dev.19

- Keep a vehicle's integration loaded when NIO returns `access_denied` for the
  `soc_status` feed. Report that endpoint as permission-denied, keep the SoC
  entity unavailable while denied, and continue showing any other permitted
  telemetry instead of starting a futile reauthentication loop.
- While the energy feed is denied, prioritize other endpoints and retry energy
  about every ten minutes so a later NIO entitlement change can recover
  without restarting Home Assistant. Actual expired/rejected OAuth tokens
  still trigger Home Assistant's reauthentication flow.
- Add regression coverage for a denied energy feed, continued vehicle-status
  polling and later energy recovery. No OAuth scope request, entity ID,
  dashboard or charging-policy changes. Thanks to @frankweiby for the
  Norwegian ET5 Touring trace that exposed this behavior.

## 0.1.1-dev.18

- Document the required Lovelace JavaScript-module resource registration for
  the optional NIO Vehicle card. In live testing, serving the file and adding
  an extra frontend script did not reliably list the card in Home Assistant's
  picker; adding the resource did, and the card displayed live vehicle data.
- Remove the unreliable extra-script registration for this card to avoid
  duplicate loading when the resource is registered. No vehicle telemetry,
  ledger, existing dashboard, or entity ID changes.

## 0.1.1-dev.17

- Add an optional NIO Vehicle Lovelace card with local, bundled model-class
  artwork, theme-aware mobile/desktop layout and 14 European language choices.
  It reads the existing NIO SoC, range, odometer, charging state and charge
  limit sensors; no new vehicle API calls or external image service are needed.
- Add per-vehicle settings in both the card and the integration's Configure
  flow. EVCC connection/power/history and household price/reimbursement
  entities are optional; leaving them empty does not affect vehicle telemetry.
  Price and reimbursement are displayed as references, not used to infer costs.
- Allow users to enable the bundled trip/charging ledger from those settings.
  Existing ledger configurations are adopted rather than silently disabled.
  Changing energy sources or calibration, or resuming history after a pause,
  starts a fresh calculation baseline without erasing archived trips or
  charging sessions; history remains stored outside HACS-managed files. No
  charging control is added.
- Add dashboard-preference and history-migration regression tests. The card is
  opt-in and does not create or replace any existing Home Assistant dashboard.

## 0.1.1-dev.16

- Bundle the previously local, optional Car ledger and card with the NIO
  integration so HACS updates no longer delete their code. Existing ledger
  settings and history remain in Home Assistant Store outside shipped files;
  the storage keys and WebSocket/card interfaces are unchanged.
- Keep the native-SoC energy source and migration boundary: the first native
  sample starts a new baseline, without recalculating archived range-derived
  trips or charging sessions. The ledger remains opt-in and does not implement
  charging policy or send vehicle commands.
- Remove household-specific 90 kWh / 557 km defaults from the bundled ledger;
  these values must come from the per-car saved configuration. Existing saved
  settings are reused automatically. A public first-time setup UI is still
  pending, so the ledger remains experimental.
- Add the 20 standalone trip/charging/native-SoC regression tests to CI.

## 0.1.1-dev.15

- Filter invalid numeric sentinels and non-finite readings before they can
  appear as vehicle measurements or replace retained SoC/range values. Preserve
  legitimate zero SoC and range readings.
- Classify NIO's `invalid_param`, `resource_not_found` and `access_denied`
  envelopes even when the HTTP response is 400 or 404. Authentication and
  rate-limit handling remain unchanged.
- Keep diagnostic entity attributes bounded and redact vehicle identifiers,
  battery-pack serials, precise location and signed URLs.
- Display individual cell-voltage values as volts to three decimal places,
  following the independently tested ET7 response; do not apply the previous
  additional divide-by-1000 conversion.
- Adapted the data-quality and diagnostic-privacy improvements from
  [@lubbyhst's PR #7](https://github.com/nicolasvangeluwe/nio-home-assistant/pull/7)
  onto the current paced-polling and retained-value implementation. Its
  separate on-demand ADAS/NOMI/recall query service is not included.

## 0.1.1-dev.14

- Shorten the HACS-visible README to current capabilities, installation and an
  invitation for EU owners to test and report results. Keep implementation
  history in this changelog rather than in the introduction.
- Clarify the two distinct SoC-response fields using NIO's published schema:
  `max_soc` is the **user-set maximum SoC limit** (90% on the test ET5 Touring),
  whereas `chrg_final_soc` is the **charging target** field. The latter has
  reported 0% while parked; that observation does not override the configured
  90% limit. Existing sensor IDs and their source-field mappings remain
  unchanged. `lock_soc` is a separate system-enforced limit.
- No telemetry or polling code changes. Existing installed entities and
  household Car-ledger files are unaffected by this documentation release.

## 0.1.1-dev.13

- Route the observed single-pack voltage and current to dedicated sensors,
  with cell and temperature-probe counts as optional diagnostic sensors.
  Never combine readings when a car reports multiple packs; the existing
  pack-count entity keeps per-pack details as attributes.
- Enable maximum SoC, high-voltage current, pack count, pack voltage and pack
  current by default on new installs. Existing HA entity-registry choices are
  preserved and can be changed on the device's Entities page.
- Add tests for real, missing, malformed and multi-pack readings.
- Reorganize the README around the entities owners receive: seven core
  sensors plus energy diagnostics, optional sensor groups, and the values
  actually observed on the test ET5 Touring. Native SoC and range are
  explicitly confirmed.
- Move implementation and release history out of the main explanation; replace
  the outdated rally-style appeal with a brief invitation for EU owner reports.

## 0.1.1-dev.12

- Replace the outdated early sensor test table with a shorter, current README:
  verified native SoC/range, paced polling, retained-value freshness, disabled
  diagnostics, and the remaining NIO-side limitations.
- Documentation-only release; integration behavior is unchanged from dev.11.

## 0.1.1-dev.11

- Refresh the HACS-visible README snapshot with the verified live SoC/range
  results and the dev.10 polling/diagnostic behavior. HACS reads the README
  from the selected release tag, so the dev.10 installation displayed older
  dev.7-era text despite the current default branch being correct.
- Documentation-only follow-up; telemetry behavior is identical to dev.10.

## 0.1.1-dev.10

- Treat zero-valued SoC-status battery temperature extrema as absent rather
  than displaying a misleading -40 °C. Live pack probes reported 17–19 °C
  while these two top-level fields were zero.
- Redact battery-pack serials from optional debug logging. The compact pack
  diagnostic continues to omit serials and per-cell arrays.
- Includes the faster, paced polling and sparse-energy retention from dev.8
  and the shared-backoff race fix from dev.9. Neither earlier tag was released.

## 0.1.1-dev.9

- Close a concurrency race discovered during final review of the shared
  request pacer: a waiting vehicle request no longer holds the pacing lock,
  so a rate-limit response can extend its deadline before it starts.
- Add a regression test for backoff arriving while another request waits.
- `v0.1.1-dev.8` was tagged for validation but not published as a release;
  use this version for the completed development release.

## 0.1.1-dev.8

- Poll one vehicle API resource per cycle with a shared 15-second minimum
  between requests per OAuth client, including concurrent vehicles and manual
  refreshes. Read the overlapping ten-minute SoC change window three times
  before each rotating background request; the ten minutes are a history
  window, not the polling delay.
- Merge sparse and duplicate energy events by field and retain independent
  source timestamps for SoC and range. Keep earlier valid values when a later
  event omits them.
- Recognize NIO's rate-limit envelopes, including HTTP 403 with a throttling
  message, honor Retry-After, and apply bounded shared backoff. Genuine
  authentication and missing-scope failures keep their prior handling.
- Expose the documented highest/lowest SoC-status battery temperatures and a
  compact battery-pack diagnostic as disabled-by-default sensors. Add a safe
  field-name list to the SoC sensor so owners can report which energy fields
  their vehicle actually sends; no serials, cell arrays or credentials are
  exposed through the new diagnostic.
- Add scheduling, pacing, sparse-field, duplicate, throttling and temperature
  regression tests. The optional, household-installed car ledger is not part
  of this public HACS package; its separate native-SoC migration is still
  being verified locally and its history remains outside shipped files.

## 0.1.1-dev.7

- Source battery SoC from NIO's `soc_status/changes` feed instead of the
  placeholder zero in `vehicle_status/latest`; preserve the last valid value
  through empty polls and Home Assistant restarts.
- Keep the newest non-null energy field from each event in a ten-minute change
  window, so a range-only event cannot hide an earlier SoC event.
- Expose the SoC source, sample time, and retained-state flag. Do not restore
  the old snapshot-derived zero when upgrading. Until this vehicle actually
  sends an SoC change record, the official sensor will be unknown rather than
  falsely showing zero.
- Add regression coverage for source priority, sparse records, and restoration.
  Thanks to @Laddvin for identifying the working change-feed approach and
  @lubbyhst for independently testing it and proposing a fix in PR #7.

## 0.1.1-dev.6

- On the first upgrade from older versions, recover the last numeric range
  from that sensor's own recent Home Assistant Recorder history if its final
  pre-upgrade state was `unknown`.
- Keep the history lookup optional and limited to the range entity; add tests
  proving newer `unknown` records do not displace the last real reading.

## 0.1.1-dev.5

- Retain the last valid official remaining-range reading when NIO's sparse
  change feed omits it or the latest vehicle snapshot has no real range.
- Restore the remaining-range sensor's last valid value after a Home Assistant
  restart and expose whether its displayed value is retained.
- Add a regression test for an energy record followed by an empty poll.
- The integration's upstream SoC field remains unchanged; household-specific
  range-to-charge calculation belongs in Home Assistant, not this integration.

## 0.1.1-dev.4

- Treat NIO's HTTP-success `invalid_grant` token response as a rejected OAuth
  authorization so Home Assistant starts its native reauthentication flow.
- Keep temporary token-service and network failures retryable instead of
  prompting for authorization.
- Prevent OAuth exceptions from exposing request credentials or provider
  response text, and add regression tests for wrapped error responses.

## 0.1.1-dev.3

- Credit the project's first external tester and contributor, `@lubbyhst`.
- Add a prominent public call for EU NIO owners to test, report redacted API
  results, and help establish a working NIO developer-support channel.
- Expand the installation guide with exact HACS custom-repository, download,
  restart, and Home Assistant configuration steps.
- Add and link a dedicated EU telemetry report discussion with a structured,
  privacy-safe model and country compatibility template.
- Add a one-click My Home Assistant button for opening the custom repository
  directly in HACS.
- Declare the currently documented European NIO markets in `hacs.json` for
  country-aware HACS discovery and the default-repository submission.

## 0.1.1-dev.2

- Prepare and maintain this public changelog file for HACS users.
- Document the exact Home Assistant OAuth redirect URI in the installation
  guide and application-credentials prompt.
- Add contribution guidelines covering issue-first coordination, testing,
  privacy, and pull requests.

## 0.1.1-dev.1

- Add one enabled diagnostic `API availability` sensor that summarizes all
  endpoint results as `available`, `partial`, or `unavailable`.
- Expose grouped working, empty, permission-denied, and errored endpoint lists
  as attributes so users can decide which detailed sensors are worth enabling.
- Add `source_endpoint` and live `endpoint_status` attributes to detailed
  telemetry sensors when they are enabled.
- Move to an unambiguous SemVer prerelease format so HACS orders future
  development releases correctly.
- Correct odometer scaling: NIO's live `mileage` value is already expressed in
  kilometres and must not be divided by ten.

## 0.1.0-dev10

- Omit the OAuth `scope` parameter so NIO grants the application's full
  permitted scope set, as defined by the provider's default behavior.
- Avoid `invalid_scope` failures caused when an explicit combined scope list
  contains a permission unavailable to the application.
- Advance the permission-policy revision so existing installations receive the
  corrected native reauthentication prompt.

## 0.1.0-dev9

- Fix scope reauthorization started from Home Assistant Repairs by explicitly
  selecting the OAuth implementation stored on the existing config entry.
- Publish development builds as normal GitHub releases so HACS can expose their
  release notes; development status remains explicit in the version and notes.

## 0.1.0-dev8

- Record a revision for the requested NIO OAuth scope set.
- Prompt existing installations through Home Assistant's native reauthentication
  flow once when the integration's requested permissions expand.
- Avoid relying on the provider returning a complete `scope` field in token
  responses, preventing false or repeating reauthentication prompts.

## 0.1.0-dev7

- Avoid hard-failing setup when an optional endpoint is blocked by missing OAuth
  scope by marking that endpoint as `permission_denied` instead of converting the
  whole integration state to `setup_error`.
- Keep reauthentication path available when required authentication scopes are
  missing for core endpoints.

## 0.1.0-dev6

- Improve OAuth permission-handling so scope/permission changes surface as a clear
  reauthentication requirement instead of generic failures.
- Keep OAuth reauthorization integrated with Home Assistant’s native flow (including
  token refresh into the existing config entry via reauth).
- Add a changelog file and public link from README for release transparency.
- Bump integration version to `0.1.0-dev6`.

## 0.1.0-dev5

- Expand telemetry coverage to all documented read-only endpoint families.
- Add richer endpoint-status tracking and preserve last-seen optional feed values.
- Add first batch of non-critical optional diagnostic sensor entities.
- Improve token refresh robustness and wrapped OAuth token parsing.

## 0.1.0-dev4

- Refine SoC-window probing and retain previous snapshots when change endpoints are
  temporarily empty.
- Keep vehicle status as a required feed and merge energy fields when available.

## 0.1.0-dev3

- Introduce OAuth2 Authorization Code + PKCE and application-credential setup.
- Add initial sensor coverage for SoC/range/charging state and basic diagnostics.

## 0.1.0-dev2

- Initial API client and integration skeleton for official NIO Open Telematics endpoints.
