# NIO Open Telematics for Home Assistant

Early development foundation for a read-only Home Assistant integration using
NIO's official EU Open Telematics API.

Current milestone:

- parses official SoC status fields;
- creates battery, range, charging-state, target, current, and data-timestamp
  sensors;
- uses one coordinator and one Home Assistant device per VIN;
- redacts credentials and vehicle identifiers from diagnostics;
- handles authentication, permission, rate-limit, envelope, and transport
  errors separately.

The config flow now uses locally supplied NIO application credentials, OAuth
Authorization Code + PKCE, NIO's HTTP Basic token exchange, wrapped token
response, and automatic refresh through Home Assistant's OAuth session. The
official reference exposes vehicle telemetry by VIN and does not document a
vehicle-list endpoint, so setup validates a manually entered VIN after consent.
Tests in a Home Assistant environment, branding, repository URLs, and release
automation must be completed before installation through HACS.

Never commit a Client ID, Client Secret, VIN, access token, refresh token, or
diagnostic payload containing personal vehicle data.
