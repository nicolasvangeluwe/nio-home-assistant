"""Application credentials support for NIO Open Telematics."""

from __future__ import annotations

from http import HTTPStatus
from typing import Any, override

from aiohttp import BasicAuth, ClientError, RequestInfo
from homeassistant.components.application_credentials import ClientCredential
from homeassistant.core import HomeAssistant
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from homeassistant.helpers.config_entry_oauth2_flow import (
    AbstractOAuth2Implementation,
    LocalOAuth2ImplementationWithPkce,
    OAuth2TokenRequestError,
    OAuth2TokenRequestReauthError,
    OAuth2TokenRequestTransientError,
)
from multidict import CIMultiDict, CIMultiDictProxy
from yarl import URL

from .const import AUTHORIZE_PATH, OAUTH_BASE_URL, OAUTH_SCOPES, TOKEN_PATH
from .oauth import (
    REAUTH_RESULT_CODES,
    TRANSIENT_RESULT_CODES,
    InvalidTokenResponseError,
    unwrap_token_response,
)


class NioOAuth2Implementation(LocalOAuth2ImplementationWithPkce):
    """Handle NIO's PKCE, Basic authentication, and wrapped token envelope."""

    _credential_name: str | None = None

    @property
    @override
    def extra_authorize_data(self) -> dict[str, str]:
        """Request NIO's vehicle-read grant while retaining HA's PKCE fields."""
        return {**super().extra_authorize_data, "scope": " ".join(OAUTH_SCOPES)}

    @property
    @override
    def name(self) -> str:
        """Show the owner's saved application-credential label in HA flows."""
        return self._credential_name or self.client_id

    def _safe_token_error(
        self,
        error_type: type[OAuth2TokenRequestError],
        *,
        status: int,
        message: str,
    ) -> OAuth2TokenRequestError:
        """Build a HA OAuth error without request credentials or response text."""
        return error_type(
            request_info=RequestInfo(
                URL(self.token_url), "POST", CIMultiDictProxy(CIMultiDict())
            ),
            status=status,
            message=message,
            domain=self.domain,
        )

    @override
    async def _async_refresh_token(self, token: dict[str, Any]) -> dict[str, Any]:
        """Refresh using NIO's documented form fields and retain old values."""
        new_token = await self._token_request(
            {
                "grant_type": "refresh_token",
                "refresh_token": token["refresh_token"],
            }
        )
        return {**token, **new_token}

    @override
    async def _token_request(self, data: dict[str, Any]) -> dict[str, Any]:
        session = async_get_clientsession(self.hass)
        # NIO requires HTTP Basic client authentication. Do not duplicate the
        # credentials in the form body or expose them in logs.
        try:
            response = await session.post(
                self.token_url,
                data=data,
                auth=BasicAuth(self.client_id, self.client_secret),
                headers={"Accept": "application/json"},
            )
        except (ClientError, TimeoutError):
            raise self._safe_token_error(
                OAuth2TokenRequestTransientError,
                status=0,
                message="NIO OAuth token service is temporarily unreachable",
            ) from None

        try:
            payload = await response.json(content_type=None)
        except (ClientError, TimeoutError):
            raise self._safe_token_error(
                OAuth2TokenRequestTransientError,
                status=response.status,
                message="NIO OAuth token response could not be read",
            ) from None
        except (ValueError, TypeError):
            payload = None

        try:
            token = unwrap_token_response(payload)
        except InvalidTokenResponseError as err:
            result_code = err.result_code
            token = None
        else:
            result_code = None

        if result_code in REAUTH_RESULT_CODES:
            raise self._safe_token_error(
                OAuth2TokenRequestReauthError,
                status=response.status,
                message=f"NIO rejected the OAuth authorization ({result_code})",
            )
        if (
            result_code in TRANSIENT_RESULT_CODES
            or response.status == HTTPStatus.TOO_MANY_REQUESTS
            or 500 <= response.status <= 599
        ):
            raise self._safe_token_error(
                OAuth2TokenRequestTransientError,
                status=response.status,
                message="NIO OAuth token service is temporarily unavailable",
            )
        if 400 <= response.status <= 499:
            raise self._safe_token_error(
                OAuth2TokenRequestReauthError,
                status=response.status,
                message="NIO rejected the OAuth token request",
            )
        if token is None:
            raise self._safe_token_error(
                OAuth2TokenRequestError,
                status=response.status,
                message="Invalid NIO OAuth token response",
            )
        return token


async def async_get_auth_implementation(
    hass: HomeAssistant,
    auth_domain: str,
    credential: ClientCredential,
) -> AbstractOAuth2Implementation:
    """Return NIO's custom OAuth implementation."""
    implementation = NioOAuth2Implementation(
        hass,
        auth_domain,
        credential.client_id,
        authorize_url=f"{OAUTH_BASE_URL}{AUTHORIZE_PATH}",
        token_url=f"{OAUTH_BASE_URL}{TOKEN_PATH}",
        client_secret=credential.client_secret,
        code_verifier_length=128,
    )
    implementation._credential_name = credential.name
    return implementation


async def async_get_description_placeholders(
    hass: HomeAssistant,
) -> dict[str, str]:
    """Return application-credential help links."""
    return {
        "console_url": "https://open-eu.nio.com/console",
        "redirect_url": "https://my.home-assistant.io/redirect/oauth",
    }
