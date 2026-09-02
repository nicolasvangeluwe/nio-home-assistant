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

SCOPE_ENERGY_READ: Final = "vehicle:energy:read"
SCOPE_DYNAMICS_READ: Final = "vehicle:dynamics:read"
OAUTH_SCOPES: Final = [SCOPE_ENERGY_READ, SCOPE_DYNAMICS_READ]

DEFAULT_SCAN_INTERVAL: Final = timedelta(minutes=10)
ATTR_EVENT_TIME: Final = "event_time"
