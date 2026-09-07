"""Application-credential regression tests for NIO Open Telematics."""

from pathlib import Path

SOURCE = (
    Path(__file__).parents[1]
    / "custom_components"
    / "nio_telematics"
    / "application_credentials.py"
).read_text(encoding="utf-8")


def test_authorize_request_uses_nios_default_scope_set() -> None:
    """The implementation must not override PKCE data with a scope parameter."""

    assert "OAUTH_SCOPES" not in SOURCE
    assert '"scope"' not in SOURCE
    assert "'scope'" not in SOURCE


def test_credentials_help_uses_home_assistant_oauth_redirect() -> None:
    """The credentials help exposes Home Assistant's exact OAuth callback."""
    assert '"redirect_url": "https://my.home-assistant.io/redirect/oauth"' in SOURCE
