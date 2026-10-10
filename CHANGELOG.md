# Changelog

The changelog is the authoritative release history for this integration.
Use this before releases and when opening PRs.

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
