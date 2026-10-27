# Optional Companion connection — design handoff

## 28 October recovery candidate after public dev.4

Public `v0.4.0-dev.4` contains only the Direct NIO flow. Installing it through
HACS replaced the earlier private Companion-capable files; the existing ET5
Touring entry now reaches Direct scope-revision reauthentication instead of the
Companion bridge. The maintained candidate is based on dev.4 and includes the
Companion source, same-entry change flow, transport and ledger protections.
Regression tests cover Companion setup and reauthentication with no Direct
scope revision or OAuth application selection. No HA files, entry, credential,
ledger or provider grant have been changed by preparing this candidate.

A future HACS release must ship every Companion module and its flow, not just a
local overlay; otherwise another HACS update will remove the bridge again. Before
a live switch, verify whether the original entry still stores a persistent HA
consumer credential and its source choice. If it does not, use the native
`Add service > Change connection for an existing vehicle` path, validate the
owner-bound vehicle against Companion, and confirm the switch on the same entry.
Never reauthenticate through a Direct NIO application to repair this route, and
never delete/recreate the car entry or its ledger. After installation, verify the
entry is loaded, the core entities retain their IDs, source timestamps advance,
and the Car ledger/history remains intact. An attended rollout and separately
authorized HA restart remain pending.

Status: 21 October source implementation under validation; not released or installed.
Direct remains the live connection. The config flow now offers Direct or Companion
and an explicit same-entry source switch. The backend's persistent `hap1_` HA
credential has no local expiration and is separate from NIO and owner web login.
The transport retains `ha1_` proof compatibility for isolated tests, but HA setup
rejects that expiring proof credential. Earlier sections below retain the design
and 20 October proof history; their preparation-only status is superseded here.

## Implemented connection and rollout boundary — 21 October

- Cache-only `GET /ha/v1/vehicle` at the agreed private backend origin; no NIO
  polling or grant refresh from the Companion adapter. HA reads every 30 seconds.
  Owner-wide admission can reject consecutive setup reads: a 429 permits one
  bounded cache retry after `Retry-After` (default 1 second, inline maximum 5).
  Longer hints defer regular polling; authentication and source-reauth errors
  are not immediately retried. Response streaming remains limited to 64 KiB.
- New setup and existing-entry Reconfigure offer connection selection. VIN and
  backend vehicle key are checked; preflight requires valid SoC, verified range
  and odometer source samples no older than 15 minutes, checked locally as well
  as by backend quality. Confirmation repeats the preflight before stopping Direct.
  For a paused car, use Add service → Change connection for an existing vehicle
  → select its existing title → Companion. HA's disabled-entry menu hides
  Reconfigure; this native route requires no Direct enable, raw API request,
  duplicated vehicle or new VIN input. It transitions the same flow to native
  reconfigure context, re-resolves the registered target and rechecks identity
  at commit. Cancellation before confirmation changes no source or enable state.
- The source change uses HA's unload/update/setup APIs, retaining the same entry,
  unique/device/entity IDs, options and archive. Failed setup restores original
  entry data and attempts to reload it. Failure of that recovery is explicit;
  upstream grant invalidation cannot be repaired by restoring saved entry data.
  If Direct was deliberately paused for provider handover, confirmation writes
  the validated Companion source first, then enables it through HA's native API.
  Failed setup restores the original disabled state without restarting Direct
  against a backend that may now own the same provider client.
- The nine-field contract populates existing core entities. Other Direct sensors
  remain registered but unavailable. Backend-present physically valid stale SoC,
  range and odometer remain visible with `source_quality=stale`, `fresh=false`,
  `data_retained=true` and unchanged source clocks, including after restart.
  Missing, conflicting, unverified and future-clock fields are withheld; no Direct
  restored value is borrowed. Stale charging, vehicle-state and current fields
  remain unavailable. API availability describes a readable cache, not field freshness.
- A source `503 source_reauthorization_required` or disconnected source creates
  an HA Repair linking to `/connections`, retains the HA credential and retries.
  Recovery clears the Repair automatically. Only consumer rejection `401` starts
  HA credential reauthentication. Temporary failures keep normal retry behavior.
- Optional ledger source/generation changes begin a new persisted energy baseline;
  no difference is calculated against the prior source, and archives are preserved.
  Both native sources must have `fresh` other than false as well as pass the
  existing 900-second source-age gate; retained stale values cannot create samples,
  source baselines, trips, consumption or charging evidence.
- Diagnostics redact the HA credential and backend vehicle key. Never copy an
  upstream NIO token or owner login session into this setup.

Release and live cutover still require backend readiness, persistent issuance,
real range-unit coverage, owner review and attended coordination. No release,
tag, HA install/reload/restart or live source switch accompanies this code change.

Targeted live consumer review on 21 October: native SoC is used by
`emhass_ev_completion`, `emhass_ev_session`, `evcc_solar_charging_guard` and
`emhass_update_mobility_ledger`. Existing household macros intentionally allow
24-hour source age and require post-connection source samples for active solar
forecast/completion context; completion additionally needs fresh physical charger
evidence. Keeping the original source timestamp preserves those existing policies.
No household automation, macro or charging-policy change accompanies this adapter.

## Product boundary

At first setup, the owner should eventually be able to choose **Direct NIO** or **Companion account** for a vehicle. Direct NIO must remain independently usable, including by people without a Companion account. The Companion route would consume the owner's authorized, cached vehicle data from the Companion backend; it must not receive a copied NIO refresh token, reuse a mobile session, run a second upstream NIO collector, or turn HA into an OAuth callback splitter. The connection is read-only first. Charging policy and vehicle controls remain outside this proposal.

The current flow inherits Home Assistant's OAuth handler, obtains NIO application credentials and a token, then collects a user-supplied VIN. Setup always creates a direct NIO client and coordinator. Existing entries have no connection-method field; any future migration must interpret their absence as **Direct NIO**, with no mandatory reconfiguration or Companion sign-in.

## Identity and history invariants

- Keep the integration domain `nio_telematics` and the existing config entry when switching a vehicle. The entry's unique ID and device identifier are based on the normalized VIN; sensor unique IDs are `VIN_sensor-key`. Never create a second entry for the same car merely to change its source.
- Validate the Companion account's ownership and authoritative vehicle identity before accepting a new entry or a source switch. A display name, model, or user-entered VIN alone is insufficient proof. Reject an owner/vehicle mismatch and preserve the previous source.
- Dashboard preferences and optional ledger records use the config entry ID. Preserve that ID, archived evidence, HA entity IDs and compatible Recorder statistics. A switch starts a new source/provenance baseline for calculations; never difference a new source's first value against the previous source as driving or charging energy.
- A proposed switch must be explicit and transactional: validate credential, vehicle mapping, capability coverage and a representative cached snapshot; only then unload the old data client, change the entry and reload. On failed validation, retain the old configuration. On failed reload, restore it. Do not operate both collectors for one entry during or after the switch. Do not revoke either upstream grant implicitly.

## Backend contract needed before implementation

The backend owner must provide a versioned, tested contract for:

1. **Consumer authorization:** a separate HA-specific, least-privilege, revocable credential; explicit owner consent; selected owner/vehicle binding; safe renewal and revocation. It must not expose NIO application secrets, upstream tokens, or the Companion mobile session. Define how HA distinguishes expired/revoked authorization from a temporary outage.
2. **Vehicle discovery and identity:** an authoritative, stable VIN or a verified identity mapping, with ownership checks on every access and no cross-owner or cross-vehicle reads. Define transfer/removal behavior and duplicate-entry handling.
3. **Cached telemetry:** a versioned schema with units, per-field source timestamps, backend receipt timestamps, source/provenance, quality, supported/unsupported capability markers, and freshness rules. Specify field coverage relative to today's direct NIO entities. An absent, denied or stale field must not be represented as a fresh zero or silently borrow another vehicle's data.
4. **Request behavior:** consumer polling or push semantics, cache lifetime, conditional reads if supported, pagination where relevant, retry/backoff and rate-limit responses. HA reads must not multiply upstream NIO calls. Specify offline, recovery and delayed/sparse-event behavior.
5. **Disconnect and data handling:** revoking only this HA consumer versus disconnecting the owner's NIO source, retention/deletion/export implications, audit events, and EU processing/hosting boundaries. Provider terms and permission for the intended distribution remain an explicit gate.

The URL, endpoint paths, authentication protocol, token format, field schema, refresh interval and response codes are deliberately **not** assumed here. The current artwork CDN and proof Worker are not a production telemetry API.

## HA adapter and rollout gates

Once that contract is real, add a source-specific adapter that normalizes Companion snapshots into the integration's existing vehicle data model. Keep source timestamps separate from HA poll times, preserve last-valid values only under the established per-field retention rules, and surface stale/unsupported/revoked states honestly. Source and freshness should be visible in diagnostics without leaking credentials or precise private telemetry.

Before a public release, test: unchanged legacy Direct entries; new Direct and Companion setup; authorization renewal/revocation; wrong owner/vehicle and duplicate VIN; partial, sparse, delayed and stale snapshots; 429/5xx retry versus rejected authorization; rollback on failed switch/reload; no duplicate upstream collector; stable entry/device/entity IDs and ledger archive across both switch directions and restarts. Verify a real backend contract and an attended HA migration before documenting Companion setup as available. Direct NIO remains the fallback, not a forced migration.

The isolated version-1 parser and HTTP client have no import path from the live setup/coordinator. The client accepts a separate `ha1_` consumer credential, reads only the cached `/ha/v1/vehicle` endpoint over HTTPS, refuses redirects, limits response size, classifies consumer 401 separately from upstream repair and retryable failures, and validates the returned VIN (and optionally the previously pinned vehicle key). The staged preflight is read-only and does not unload or update the HA entry. A supported login, scheduled consumer polling, credential renewal, config-flow selection or source switch remains absent; these would be nonfunctional and risky before the backend protocol is ready.

## 20 October readiness and Wednesday continuity boundary

The owner wants to begin NIO Connect, but requires the HA car connection working again by **Wednesday 21 October 2026, 20:00 Europe/Brussels**. Any attended experiment has a **19:00 hard stop**, leaving an hour for direct-HA recovery and verification. That buffer is not a guarantee that a deleted client or revoked grant can be recovered in an hour. Therefore do not delete, rotate, revoke, or replace the working HA developer application as part of this proof. Do not change its callback, OAuth grant, config entry, or polling schedule merely to prepare a Companion connection.

Read-only HA check on 20 October: one ET5 Touring `nio_telematics` entry is loaded and offers Reconfigure. Native SoC is 48.5%, remaining range 269 km and odometer 6,428 km; API availability is partial and charging state unknown. The SoC's last valid source sample is 20:59 Brussels and its current state is marked retained. These observations establish a useful Direct baseline, not that all endpoints are fresh or that a second client can coexist. No credential or complete VIN was read into this document.

The latest retained provider evidence says the HA connection was recovered using a dedicated personal application with only `https://my.home-assistant.io/redirect/oauth`. NIO's guide describes comma-separated HTTPS callbacks, but the live authorization validator rejected individual callbacks from a comma-joined registration. A separate Companion callback was accepted in a portal registration earlier, **not** proven to authorize alongside HA; do not confuse portal acceptance with working OAuth, independent refresh-token families, or safe shared pacing. The HA pacer is process-local and keyed by client ID; it cannot coordinate a separate Companion backend. The documented vehicle rate limit is per client ID, not per process or callback. Current client-count restrictions and provider grant behavior need fresh confirmation, not assumptions from an older portal session.

Safe sequence for this deadline:

1. Leave the current Direct HA entry and dedicated application untouched. Read-only portal inspection may determine whether NIO permits a **parallel** backend application with its own callback and client ID; enterprise verification is still pending and must not be treated as available tomorrow.
2. If an independent backend client is legitimately available, prove its callback, grant, one-car ownership, token refresh and paced read-only snapshots without modifying or sharing HA credentials. Confirm source timestamps, units, field coverage and backend-cache behavior. No HA switch follows automatically.
3. Only after the backend supplies the consumer contract above may the HA integration implement an opt-in Companion source behind a separately revocable HA-consumer credential. Test it against synthetic and isolated data first. Preserve the existing Direct path and entry identity; any live switch must be attended, validated before commit, and reversible without provider-client deletion.
4. At 19:00 Wednesday, stop any unproven live experiment. Verify the Direct entry is loaded, its relevant sensors and source timestamps, and OAuth refresh/log health by 20:00. If a parallel client or safe rollback cannot be established, defer backend proof or HA source switching; do **not** sacrifice the working HA application to meet a feature target.

Removing a Companion HA consumer must revoke only that consumer's backend access. Companion history deletion and provider/NIO grant revocation are separate owner actions. A source-switch rollback restores the prior HA entry data; it cannot resurrect a provider application that was deleted or a refresh grant invalidated upstream.

## 20 October backend proof contract review

The backend's initial `docs/backend/HA_CONSUMER_API_2026-10-20.md` specified a private `GET /ha/v1/vehicle` proof source with one authoritative vehicle and a separate `ha1_` bearer scoped to the HA consumer. A protected cache-only proof route and one-time bearer ceremony were subsequently mounted and tested, but there is no production HA onboarding or renewal flow. Its proof credential expires within 24 hours, so it is not a supported daily HA connection. A `401 unauthorized` is HA-consumer reauthentication; `503 source_reauthorization_required` is upstream NIO repair and must not launch an HA credential loop. `503 source_disconnected` is a separate owner action; `429` and `503 unavailable` are retryable. The isolated parser and HTTP client enforce these distinctions, but HA's live coordinator does not use them.

The backend's nine fields map only partly to existing HA entities:

| Backend field | Existing HA meaning | Current gap |
| --- | --- | --- |
| `socPercent` | Battery state of charge | Direct HA intentionally rejects the `vehicle_status` zero placeholder. After this review the backend projector and isolated HA parser both require `soc_status`; native SoC zero remains valid. Real-car coverage still needs proof. |
| `targetSocPercent`, `maximumSocPercent` | Charging target, maximum SoC | Distinct fields; do not substitute target for the user's configured maximum. Coverage and clock evidence remain unproved for another car. |
| `batteryCurrentA` | High-voltage battery current | Mapping is plausible by unit/field, but needs one-car comparison. |
| `vehicleState` | Vehicle state | Enum is aligned with the current dynamics sensor; per-field clock must be retained. |
| `energyChargingState`, `dynamicsChargingState` | Charging state | Distinct NIO enums/sources. The current HA sensor can use an energy observation or a vehicle fallback; do not merge them into an invented universal state. Define precedence and availability with real evidence. |
| `rangeKm`, `odometerKm` | Remaining range, odometer | Each field is independent. Version-1 parsing accepts a server-verified km value with correct endpoint, clock and quality, while an unverified field remains null/`unit_unverified`. A verified odometer does not verify range or satisfy the existing-car switch gate by itself. No live HA unit policy is implied here. |

All other direct endpoint sensors/diagnostics, position, trip and body/cabin fields are absent. The backend explicitly reports no location, controls or history capability. The installed HA vehicle uses native SoC, range, odometer and vehicle state; a switch now would lose material functionality. The parser validates version, ownership claim, VIN shape, all nine field contracts, UTC source/receipt timestamps, freshness quality, expected units/enums and error-code boundaries. It rejects dynamics-only SoC and never treats a stale, future-clock or unverified-unit value as a usable current HA reading. Accepting a backend-labelled valid km value depends on the backend's trusted unit policy; the HA parser cannot independently prove physical units. This is a compatibility guard, **not** proof that the backend's ownership assertion is true; only its trusted server adapters can establish that.

Before a live HACS option: the backend must activate real owner/vehicle evidence, establish an independent NIO client or proven safe coexistence, verify range/odometer scaling and source parity, provide durable consumer issuance/renewal/revocation and a stable cache/feed, and prove isolated read/recovery behavior. Then HA needs a source adapter, visible config flow, switch/rollback tests and an attended migration. None is authorized merely by the staged parser/transport.

For the **attended shared-client renewal test**, the existing HA config entry was paused by disabling its exact entry through HA's integration enable/disable control (`ha_set_integration` with that entry ID and `enabled: false`). This unloaded Direct polling without deleting the entry, token or entity registry. After the backend stopped provider work and the original callback was restored, the same entry was re-enabled and read back as loaded; `soc_status` supplied a fresh source sample without a new consent. Sensors were unavailable during the pause. This proves the HA-side pause/restore on this occasion, **not** a complete provider-grant rollback or future token-refresh survival; enabling HA cannot resurrect a revoked NIO refresh grant. The Wednesday 19:00/20:00 recovery boundary still applies to any further attended experiment.

## 20 October isolated live transport proof

An approved, separate 24-hour HA-consumer bearer was passed to the staged Python HTTP client in memory only. Against the protected backend's real, non-synthetic cached DTO, the client parsed the response, withheld stale SoC, rejected a source switch for insufficient coverage, rejected a mismatched VIN, and classified an invalid consumer bearer as requiring **consumer** reauthentication. The backend then revoked only this HA bearer; a subsequent read returned HTTP 401. No bearer, VIN, private reading or raw response is stored in this repository. An additional 11 generated synthetic backend DTO vectors and four error mappings passed the Python parser, including an odometer-only verified-unit case.

The trusted backend has a vehicle-specific odometer unit policy for this car; range remains unverified and unavailable in the Companion DTO. The private backend's provider/collector gates were off after proof. The owner's original Direct HA entry was re-enabled and delivered a fresh, non-retained `soc_status` sample without new consent. This verifies a narrow cache-only transport and Direct recovery, **not** a supported daily HA source: the proof bearer expires after 24 hours, issuance/renewal is not a public product flow, range and other direct capabilities are missing, and no HACS config flow, migration, installation or release was performed.
