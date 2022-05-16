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
SUPPORTED_CURRENCIES = [
    "ERN","HKD","GGP","RSD","SHP","USD","MYR","PYG","RON","DOP","TWD","AWG",
    "CVE","BND","RUB","NGN","XCD","JEP","ZWL","HNL","NZD","AFN","MUR","DKK",
    "CNY","JOD","CHF","COP","XAF","XAG","ZMK","GNF","ZMW","GIP","BTC","MKD",
    "WST","IDR","IQD","BHD","YER","MAD","KGS","PHP","PEN","BMD","DJF","MVR",
    "QAR","JPY","SCR","IMP","KRW","HRK","SOS","VUV","NIO","KYD","LAK","ISK",
    "BOB","IRR","NPR","EGP","BBD","CAD","XAU","CUP","SDG","PKR","UZS","CLF",
    "CUC","STD","MGA","FJD","DZD","TJS","EURKM","SZL","THB","SRD","BDT",
    "BTN","CZK","AMD","UGX","TRY","AUD","UAH","HUF","SLL","VND","RWF","LBP",
    "ANG","SAR","LVL","KHR","BYR","TTD","OMR","LTL","GTQ","ALL","MRO","MWK",
    "LSL","SBD","BGN","LRD","JMD","CRC","ETB","NAD","GYD","LKR","INR","SEK",
    "KES","KMF","VEF","ARS","HTG","BAM","BWP","GEL","KZT","AED","KWD","XDR",
    "EUR","TND","MDL","LYD","BSD","GHS","MOP","PAB","ZAR","AZN","TOP","SVC",
    "KPW","TMT","BZD","GMD","XOF","UYU","MNT","NOK","XPF","BIF","BYN","FKP",
    "GBP","MXN","SYP","PGK","MZN","PLN","MMK","SGD","AOA","ILS","CLP","TZS",
    "CDF","BRL"
]
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
