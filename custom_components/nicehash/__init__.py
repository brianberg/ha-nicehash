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
    CURRENCY_USD,
    DOMAIN,
    STARTUP_MESSAGE,
)
from .nicehash import NiceHashPrivateClient
from .data_coordinators import (
    NiceHashAccountsDataUpdateCoordinator,
    NiceHashMiningRigsDataUpdateCoordinator,
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
    organization_id = nicehash_config.get(CONF_ORGANIZATION_ID)
    api_key = nicehash_config.get(CONF_API_KEY)
    api_secret = nicehash_config.get(CONF_API_SECRET)
    currency = nicehash_config.get(CONF_CURRENCY).upper()

    client = NiceHashPrivateClient(organization_id, api_key, api_secret)

    accounts_coordinator = NiceHashAccountsDataUpdateCoordinator(hass, client)
    rigs_coordinator = NiceHashMiningRigsDataUpdateCoordinator(hass, client)

    await accounts_coordinator.async_refresh()

    if not accounts_coordinator.last_update_success:
        _LOGGER.error("Unable to get NiceHash accounts")
        raise PlatformNotReady

    await rigs_coordinator.async_refresh()

    if not rigs_coordinator.last_update_success:
        _LOGGER.error("Unable to get NiceHash mining rigs")
        raise PlatformNotReady

    hass.data[DOMAIN]["organization_id"] = organization_id
    hass.data[DOMAIN]["client"] = client
    hass.data[DOMAIN]["currency"] = currency
    hass.data[DOMAIN]["accounts_coordinator"] = accounts_coordinator
    hass.data[DOMAIN]["rigs_coordinator"] = rigs_coordinator

    await discovery.async_load_platform(hass, "sensor", DOMAIN, {}, config)

    return True
