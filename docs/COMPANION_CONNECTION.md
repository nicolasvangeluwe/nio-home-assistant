# Optional Companion connection — design handoff

Status: contract proposal only, 20 October 2026. No Companion connection method, backend client, account linking, migration, or HA deployment exists in this integration. Direct NIO OAuth remains the sole supported route. A targeted live HA check on 20 October found the existing `nio_telematics` entry loaded; it did not validate any Companion service or switch.

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

No runtime code or tests are added by this handoff because implementing a speculative login or response parser would create a nonfunctional connection option and risk existing Direct NIO users.
