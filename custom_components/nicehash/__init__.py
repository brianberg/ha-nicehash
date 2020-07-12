"""
Integrates NiceHash with Home Assistant

For more details about this integration, please refer to
https://github.com/brianberg/ha-nicehash
"""
import logging
import voluptuous as vol

from homeassistant.const import CONF_DEVICES, CONF_TIMEOUT
from homeassistant.core import Config, HomeAssistant
from homeassistant.helpers import discovery
import homeassistant.helpers.config_validation as cv
from homeassistant.exceptions import PlatformNotReady

from .const import (
    CONF_API_KEY,
    CONF_API_SECRET,
    CONF_CURRENCY,
    CONF_ORGANIZATION_ID,
    CONF_BALANCES_ENABLED,
    CONF_RIGS_ENABLED,
    CONF_DEVICES_ENABLED,
    CONF_PAYOUTS_ENABLED,
    CURRENCY_USD,
    DOMAIN,
    STARTUP_MESSAGE,
)
from .nicehash import NiceHashPrivateClient
from .coordinators import (
    AccountsDataUpdateCoordinator,
    MiningPayoutsDataUpdateCoordinator,
    MiningRigsDataUpdateCoordinator,
)

_LOGGER = logging.getLogger(__name__)

CONFIG_SCHEMA = vol.Schema(
    {
        DOMAIN: vol.Schema(
            {
                vol.Required(CONF_ORGANIZATION_ID): cv.string,
                vol.Required(CONF_API_KEY): cv.string,
                vol.Required(CONF_API_SECRET): cv.string,
                vol.Required(CONF_CURRENCY, default=CURRENCY_USD): cv.string,
                vol.Required(CONF_BALANCES_ENABLED, default=False): cv.boolean,
                vol.Required(CONF_RIGS_ENABLED, default=False): cv.boolean,
                vol.Required(CONF_DEVICES_ENABLED, default=False): cv.boolean,
                vol.Required(CONF_PAYOUTS_ENABLED, default=False): cv.boolean,
            }
        )
    },
    extra=vol.ALLOW_EXTRA,
)


async def async_setup(hass: HomeAssistant, config: Config):
    """Set up this integration"""
    if hass.data.get(DOMAIN) is None:
        hass.data.setdefault(DOMAIN, {})
        _LOGGER.debug(STARTUP_MESSAGE)

    nicehash_config = config[DOMAIN]
    # Configuration
    organization_id = nicehash_config.get(CONF_ORGANIZATION_ID)
    api_key = nicehash_config.get(CONF_API_KEY)
    api_secret = nicehash_config.get(CONF_API_SECRET)
    # Options
    currency = nicehash_config.get(CONF_CURRENCY).upper()
    balances_enabled = nicehash_config.get(CONF_BALANCES_ENABLED)
    rigs_enabled = nicehash_config.get(CONF_RIGS_ENABLED)
    devices_enabled = nicehash_config.get(CONF_DEVICES_ENABLED)
    payouts_enabled = nicehash_config.get(CONF_PAYOUTS_ENABLED)

    client = NiceHashPrivateClient(organization_id, api_key, api_secret)

    hass.data[DOMAIN]["organization_id"] = organization_id
    hass.data[DOMAIN]["client"] = client
    hass.data[DOMAIN]["currency"] = currency
    hass.data[DOMAIN]["balances_enabled"] = balances_enabled
    hass.data[DOMAIN]["rigs_enabled"] = rigs_enabled
    hass.data[DOMAIN]["devices_enabled"] = devices_enabled
    hass.data[DOMAIN]["payouts_enabled"] = payouts_enabled

    # Accounts
    if balances_enabled:
        _LOGGER.debug("Account balances enabled, fetching accounts...")
        accounts_coordinator = AccountsDataUpdateCoordinator(hass, client)
        await accounts_coordinator.async_refresh()

        if not accounts_coordinator.last_update_success:
            _LOGGER.error("Unable to get NiceHash accounts")
            raise PlatformNotReady

        hass.data[DOMAIN]["accounts_coordinator"] = accounts_coordinator

    # Payouts
    if payouts_enabled:
        _LOGGER.debug("Payouts enabled, fetching payouts data...")
        payouts_coordinator = MiningPayoutsDataUpdateCoordinator(hass, client)
        await payouts_coordinator.async_refresh()

        if not payouts_coordinator.last_update_success:
            _LOGGER.error("Unable to get NiceHash mining payouts")
            raise PlatformNotReady

        hass.data[DOMAIN]["payouts_coordinator"] = payouts_coordinator

    # Rigs
    if rigs_enabled or devices_enabled:
        _LOGGER.debug("Rigs or devices enabled, fetching rigs...")
        rigs_coordinator = MiningRigsDataUpdateCoordinator(hass, client)
        await rigs_coordinator.async_refresh()

        if not rigs_coordinator.last_update_success:
            _LOGGER.error("Unable to get NiceHash mining rigs")
            raise PlatformNotReady

        hass.data[DOMAIN]["rigs_coordinator"] = rigs_coordinator

    await discovery.async_load_platform(hass, "sensor", DOMAIN, {}, config)

    return True
