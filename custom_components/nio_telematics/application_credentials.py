"""Application credentials support for NIO Open Telematics."""

from __future__ import annotations

from http import HTTPStatus
from typing import Any, cast, override

from aiohttp import BasicAuth, ClientResponseError

from homeassistant.components.application_credentials import ClientCredential
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import (
    OAuth2TokenRequestError,
    OAuth2TokenRequestReauthError,
    OAuth2TokenRequestTransientError,
)
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from homeassistant.helpers.config_entry_oauth2_flow import (
    AbstractOAuth2Implementation,
    LocalOAuth2ImplementationWithPkce,
)

from .const import API_BASE_URL, AUTHORIZE_PATH, OAUTH_SCOPES, TOKEN_PATH
from .oauth import unwrap_token_response


class NioOAuth2Implementation(LocalOAuth2ImplementationWithPkce):
    """Handle NIO's PKCE, Basic authentication, and wrapped token envelope."""

    @property
    @override
    def extra_authorize_data(self) -> dict[str, str]:
        data = {"scope": " ".join(OAUTH_SCOPES)}
        data.update(super().extra_authorize_data)
        return data

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
            response.raise_for_status()
            payload = await response.json()
        except ClientResponseError as err:
            exception_type: type[OAuth2TokenRequestError]
            if err.status == HTTPStatus.TOO_MANY_REQUESTS or 500 <= err.status <= 599:
                exception_type = OAuth2TokenRequestTransientError
            elif 400 <= err.status <= 499:
                exception_type = OAuth2TokenRequestReauthError
            else:
                exception_type = OAuth2TokenRequestError
            raise exception_type(
                request_info=err.request_info,
                history=err.history,
                status=err.status,
                message=err.message,
                headers=err.headers,
                domain=self.domain,
            ) from err
        except (ValueError, TypeError) as err:
            raise OAuth2TokenRequestError(
                request_info=response.request_info,
                history=response.history,
                status=response.status,
                message="Invalid NIO OAuth token response",
                headers=response.headers,
                domain=self.domain,
            ) from err
        return unwrap_token_response(cast(dict[str, Any], payload))


async def async_get_auth_implementation(
    hass: HomeAssistant,
    auth_domain: str,
    credential: ClientCredential,
) -> AbstractOAuth2Implementation:
    """Return NIO's custom OAuth implementation."""
    return NioOAuth2Implementation(
        hass,
        auth_domain,
        credential.client_id,
        authorize_url=f"{API_BASE_URL}{AUTHORIZE_PATH}",
        token_url=f"{API_BASE_URL}{TOKEN_PATH}",
        client_secret=credential.client_secret,
        code_verifier_length=128,
    )


async def async_get_description_placeholders(
    hass: HomeAssistant,
) -> dict[str, str]:
    """Return application-credential help links."""
    return {"console_url": "https://open-eu.nio.com/console"}
