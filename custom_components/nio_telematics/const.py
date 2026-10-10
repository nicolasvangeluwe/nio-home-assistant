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

# NIO grants the application's full permitted scope set when the OAuth
# authorization request omits ``scope``. Do not send an explicit list: NIO
# rejects the entire request if it contains a scope unavailable to that app.
OAUTH_SCOPE_REVISION: Final = 2

DEFAULT_SCAN_INTERVAL: Final = timedelta(seconds=15)
ATTR_EVENT_TIME: Final = "event_time"
