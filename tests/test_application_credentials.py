"""Application-credential regression tests for NIO Open Telematics."""

from pathlib import Path
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from aiohttp import BasicAuth
from homeassistant.components.application_credentials import ClientCredential
from homeassistant.core import HomeAssistant
from homeassistant.helpers.config_entry_oauth2_flow import (
    OAuth2TokenRequestError,
    OAuth2TokenRequestReauthError,
    OAuth2TokenRequestTransientError,
)

from custom_components.nio_telematics.application_credentials import (
    NioOAuth2Implementation,
    async_get_auth_implementation,
)
from custom_components.nio_telematics.const import DOMAIN, OAUTH_SCOPES

SOURCE = (
    Path(__file__).parents[1]
    / "custom_components"
    / "nio_telematics"
    / "application_credentials.py"
).read_text(encoding="utf-8")


def test_authorize_request_includes_supported_scopes_and_pkce(
    hass: HomeAssistant,
) -> None:
    """HA setup requests vehicle data without requiring URL edits by owners."""
    data = implementation(hass).extra_authorize_data

    assert data["scope"] == " ".join(OAUTH_SCOPES)
    assert "vehicle:read" in OAUTH_SCOPES
    assert "vehicle:energy:read" in OAUTH_SCOPES
    assert "vehicle:connectivity:read" not in OAUTH_SCOPES
    assert "aftersales:read" not in OAUTH_SCOPES
    assert data["code_challenge"]
    assert data["code_challenge_method"] == "S256"
    assert "client-secret-marker" not in str(data)


def test_credentials_help_uses_home_assistant_oauth_redirect() -> None:
    """The credentials help exposes Home Assistant's exact OAuth callback."""
    assert '"redirect_url": "https://my.home-assistant.io/redirect/oauth"' in SOURCE


async def test_credential_picker_shows_saved_name(hass: HomeAssistant) -> None:
    """The implementation picker distinguishes multiple saved NIO clients."""
    named = await async_get_auth_implementation(
        hass, "nio-named", ClientCredential("client-one", "secret", "Home Assistant")
    )
    unnamed = await async_get_auth_implementation(
        hass, "nio-unnamed", ClientCredential("client-two", "secret")
    )

    assert named.name == "Home Assistant"
    assert unnamed.name == "client-two"
    assert named.domain == "nio-named"
    assert unnamed.domain == "nio-unnamed"


def implementation(hass: HomeAssistant) -> NioOAuth2Implementation:
    """Create a NIO OAuth implementation with deliberately sensitive credentials."""
    return NioOAuth2Implementation(
        hass,
        DOMAIN,
        "client-id-secret-marker",
        authorize_url="https://open-eu.nio.com/oauth2/authorize",
        token_url="https://open-eu.nio.com/api/2/oauth/token",
        client_secret="client-secret-marker",
    )


def token_response(status: int, payload: object) -> MagicMock:
    """Build a token response without a real network request."""
    response = MagicMock(status=status)
    response.json = AsyncMock(return_value=payload)
    return response


@pytest.mark.parametrize("status", [200, 400])
async def test_invalid_grant_envelope_requires_reauth(
    hass: HomeAssistant, caplog: pytest.LogCaptureFixture, status: int
) -> None:
    """NIO's HTTP-success invalid_grant must use HA's native reauth error."""
    session = MagicMock()
    session.post = AsyncMock(
        return_value=token_response(
            status,
            {
                "result_code": "invalid_grant",
                "display_msg": "client-secret-marker",
                "debug_msg": "refresh-token-marker",
            },
        )
    )
    oauth = implementation(hass)

    with (
        patch(
            "custom_components.nio_telematics.application_credentials.async_get_clientsession",
            return_value=session,
        ),
        pytest.raises(OAuth2TokenRequestReauthError) as error,
    ):
        await oauth._async_refresh_token(
            {"refresh_token": "refresh-token-marker", "access_token": "old-token"}
        )

    assert session.post.await_args.kwargs["auth"] == BasicAuth(
        "client-id-secret-marker", "client-secret-marker"
    )
    assert session.post.await_args.kwargs["data"] == {
        "grant_type": "refresh_token",
        "refresh_token": "refresh-token-marker",
    }
    assert not error.value.request_info.headers
    assert "invalid_grant" in str(error.value)
    for secret in ("client-id-secret-marker", "client-secret-marker", "refresh-token-marker"):
        assert secret not in str(error.value)
        assert secret not in caplog.text


@pytest.mark.parametrize(
    ("status", "payload"),
    [
        (200, {"result_code": "temporarily_unavailable"}),
        (200, {"result_code": "server_error"}),
        (503, {"result_code": "unknown"}),
        (429, {"result_code": "unknown"}),
    ],
)
async def test_temporary_token_errors_remain_retryable(
    hass: HomeAssistant, status: int, payload: dict
) -> None:
    """Transient envelopes and HTTP failures must not demand reauthentication."""
    session = MagicMock()
    session.post = AsyncMock(return_value=token_response(status, payload))
    with (
        patch(
            "custom_components.nio_telematics.application_credentials.async_get_clientsession",
            return_value=session,
        ),
        pytest.raises(OAuth2TokenRequestTransientError),
    ):
        await implementation(hass)._token_request({"grant_type": "refresh_token"})


async def test_token_network_timeout_is_retryable(hass: HomeAssistant) -> None:
    """No response from NIO must be retryable and must not expose credentials."""
    session = MagicMock()
    session.post = AsyncMock(side_effect=TimeoutError("client-secret-marker"))
    with (
        patch(
            "custom_components.nio_telematics.application_credentials.async_get_clientsession",
            return_value=session,
        ),
        pytest.raises(OAuth2TokenRequestTransientError) as error,
    ):
        await implementation(hass)._token_request({"grant_type": "refresh_token"})

    assert "client-secret-marker" not in str(error.value)


async def test_malformed_success_envelope_is_not_reauth(hass: HomeAssistant) -> None:
    """A malformed provider response is not evidence of a rejected grant."""
    session = MagicMock()
    session.post = AsyncMock(return_value=token_response(200, {"result_code": "success"}))
    with (
        patch(
            "custom_components.nio_telematics.application_credentials.async_get_clientsession",
            return_value=session,
        ),
        pytest.raises(OAuth2TokenRequestError) as error,
    ):
        await implementation(hass)._token_request({"grant_type": "refresh_token"})

    assert not isinstance(error.value, OAuth2TokenRequestReauthError)
    assert not isinstance(error.value, OAuth2TokenRequestTransientError)
