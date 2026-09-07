# Changelog

The changelog is the authoritative release history for this integration.
Use this before releases and when opening PRs.

## Unreleased

- Credit the project's first external tester and contributor, `@lubbyhst`.
- Add a prominent public call for EU NIO owners to test, report redacted API
  results, and help establish a working NIO developer-support channel.
- Expand the installation guide with exact HACS custom-repository, download,
  restart, and Home Assistant configuration steps.

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
