"""Constants for NIO Open Telematics."""

from datetime import timedelta
from typing import Final

DOMAIN: Final = "nio_telematics"
PLATFORMS: Final = ["sensor"]

API_BASE_URL: Final = "https://open-api-eu.nio.com"
OAUTH_BASE_URL: Final = "https://open-eu.nio.com"
AUTHORIZE_PATH: Final = "/oauth2/authorize"
TOKEN_PATH: Final = "/api/2/oauth/token"
TELEMATICS_PATH: Final = "/api/1/telematics"

CONF_VIN: Final = "vin"
CONF_VEHICLE_NAME: Final = "vehicle_name"
CONF_SCOPE_REVISION: Final = "scope_revision"
CONF_CONNECTION_METHOD: Final = "connection_method"
CONNECTION_DIRECT: Final = "direct"
CONNECTION_COMPANION: Final = "companion"
CONF_COMPANION_CREDENTIAL: Final = "companion_credential"
CONF_COMPANION_VEHICLE_KEY: Final = "companion_vehicle_key"
COMPANION_API_ORIGIN: Final = (
    "https://nio-companion-proof.nio-companion-backend.workers.dev"
)
COMPANION_CONNECTIONS_URL: Final = f"{COMPANION_API_ORIGIN}/connections"

# NIO's Personal Application console lists these read-only vehicle scopes.
# An omitted scope completed OAuth on a newly created app but its telemetry
# requests returned access_denied; an explicit grant restored live readings.
# Do not add unsupported legacy scopes such as vehicle:connectivity:read or
# aftersales:read: NIO rejects the complete authorization with invalid_scope.
OAUTH_SCOPES: Final = (
    "vehicle:read",
    "vehicle:dynamics:read",
    "vehicle:location:read",
    "vehicle:energy:read",
    "vehicle:body:read",
    "vehicle:cabin:read",
    "vehicle:powertrain:read",
    "vehicle:diagnostics:read",
    "vehicle:adas:read",
    "vehicle:nomi:read",
)
OAUTH_SCOPE_REVISION: Final = 3

DEFAULT_SCAN_INTERVAL: Final = timedelta(seconds=15)
ATTR_EVENT_TIME: Final = "event_time"
