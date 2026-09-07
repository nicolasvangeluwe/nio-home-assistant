# Contributing

Thanks for helping improve this experimental integration.

## Before writing code

Please open a GitHub issue or discussion before starting a change. Describe the
problem, the NIO application type and region, the vehicle model, and the
credential-safe result you observed. This helps us compare NIO API behaviour
before maintaining multiple implementations of the same fix.

The maintainer may implement small or integration-wide changes directly. If a
pull request would be useful, agree on its direction in the issue first. A fork
used for testing or preparing a pull request is welcome, but this repository is
the only documented source for HACS installation and releases.

## Pull requests

- Keep changes focused and preserve existing entity IDs where possible.
- Use only the official NIO Open Telematics API; do not add reverse-engineered
  NIO app endpoints.
- Add or update tests for behaviour changes.
- Update relevant documentation, but do not bump the integration version or
  create release notes unless requested by the maintainer.
- Ensure pytest, hassfest, and HACS validation pass.

## Privacy and security

Never post or commit Client IDs, Client Secrets, OAuth tokens, authorization
codes, full VINs, precise locations, or unredacted Home Assistant diagnostics.
Redact vehicle identifiers and personal telemetry before sharing examples.

## Project status

This is an independent, unofficial personal project built with substantial AI
assistance. Contributions and testing are appreciated, but the project is not
affiliated with or supported by NIO, Home Assistant, or OpenAI.
