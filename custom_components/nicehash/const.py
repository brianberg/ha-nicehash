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
ICON_CURRENCY_BTC = "mdi:currency-btc"
ICON_CURRENCY_EUR = "mdi:currency-eur"
ICON_CURRENCY_USD = "mdi:currency-usd"
ICON_EXCAVATOR = "mdi:excavator"
ICON_MEMORY = "mdi:memory"
ICON_PICKAXE = "mdi:pickaxe"
ICON_PULSE = "mdi:pulse"
ICON_THERMOMETER = "mdi:thermometer"
ICON_SPEEDOMETER = "mdi:speedometer"

# Platforms
SENSOR = "sensor"
PLATFORMS = [SENSOR]


# Configuration and options
CONF_API_KEY = "api_key"
CONF_API_SECRET = "api_secret"
CONF_ORGANIZATION_ID = "organization_id"
CONF_CURRENCY = "currency"
CONF_BALANCES_ENABLED = "balances"
CONF_RIGS_ENABLED = "rigs"
CONF_DEVICES_ENABLED = "devices"
CONF_PAYOUTS_ENABLED = "payouts"

# Defaults
DEFAULT_NAME = NAME
FORMAT_DATETIME = "%d-%m-%Y %H:%M"

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
NICEHASH_ATTRIBUTION = "Data provided by NiceHash"
# Currency
CURRENCY_BTC = "BTC"
CURRENCY_USD = "USD"
CURRENCY_EUR = "EUR"
# Balance type
BALANCE_TYPE_AVAILABLE = "available"
BALANCE_TYPE_PENDING = "pending"
BALANCE_TYPE_TOTAL = "total"
# Device status
DEVICE_STATUS_UNKNOWN = "UNKNOWN"
DEVICE_STATUS_DISABLED = "DISABLED"
DEVICE_STATUS_INACTIVE = "INACTIVE"
DEVICE_STATUS_MINING = "MINING"
DEVICE_STATUS_BENCHMARKING = "BENCHMARKING"
DEVICE_STATUS_ERROR = "ERROR"
DEVICE_STATUS_PENDING = "PENDING"
DEVICE_STATUS_OFFLINE = "OFFLINE"
# Device stat
DEVICE_SPEED_RATE = "device-speed-rate"
DEVICE_SPEED_ALGORITHM = "device-speed-algorithm"
DEVICE_LOAD = "device-load"
DEVICE_RPM = "device-rpm"
# Payout types
PAYOUT_USER = "USER"
# Magic numbers
MAX_TWO_BYTES = 65536
