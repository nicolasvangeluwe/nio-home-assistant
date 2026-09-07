"""Application-credential regression tests for NIO Open Telematics."""

from pathlib import Path

from custom_components.nio_telematics.application_credentials import (
    async_get_description_placeholders,
)


def test_authorize_request_uses_nios_default_scope_set() -> None:
    """The implementation must not override PKCE data with a scope parameter."""
    source = (
        Path(__file__).parents[1]
        / "custom_components"
        / "nio_telematics"
        / "application_credentials.py"
    ).read_text(encoding="utf-8")

    assert "OAUTH_SCOPES" not in source
    assert '"scope"' not in source
    assert "'scope'" not in source


async def test_credentials_help_uses_home_assistant_oauth_redirect() -> None:
    """The credentials help exposes Home Assistant's exact OAuth callback."""
    placeholders = await async_get_description_placeholders(None)  # type: ignore[arg-type]

    assert placeholders["redirect_url"] == (
        "https://my.home-assistant.io/redirect/oauth"
    )
