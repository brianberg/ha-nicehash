"""
Constants for NiceHash
"""
# Base component constants
NAME = "NiceHash"
DOMAIN = "nicehash"
DOMAIN_DATA = f"{DOMAIN}_data"
VERSION = "0.1.0"

ISSUE_URL = "https://github.com/brianberg/ha-nicehash/issues"

# Icons
ICON = "mdi:pickaxe"
ICON_CURRENCY_BTC = "mdi:currency-btc"
ICON_CURRENCY_EUR = "mdi:currency-eur"
ICON_CURRENCY_USD = "mdi:currency-usd"
ICON_TEMPERATURE = "mdi:thermometer"

# Platforms
SENSOR = "sensor"
PLATFORMS = [SENSOR]


# Configuration and options
CONF_ENABLED = "enabled"
CONF_API_KEY = "api_key"
CONF_API_SECRET = "api_secret"
CONF_ORGANIZATION_ID = "organization_id"
CONF_CURRENCY = "currency"


# Defaults
DEFAULT_NAME = NAME

# Startup
STARTUP_MESSAGE = f"""
-------------------------------------------------------------------
{NAME}
Version: {VERSION}
This is a custom integration!
If you have any issues with this you need to open an issue here:
{ISSUE_URL}
-------------------------------------------------------------------
"""

# NiceHash
NICEHASH_API_URL = "https://api2.nicehash.com"
CURRENCY_BTC = "BTC"
CURRENCY_USD = "USD"
CURRENCY_EUR = "EUR"
BALANCE_TYPE_AVAILABLE = "available"
BALANCE_TYPE_PENDING = "pending"
BALANCE_TYPE_TOTAL = "total"
DEVICE_STATUS_INACTIVE = "INACTIVE"
