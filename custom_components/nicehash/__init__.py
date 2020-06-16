"""
Integrates NiceHash with Home Assistant

For more details about this integration, please refer to
https://github.com/brianberg/ha-nicehash
"""
import asyncio
from datetime import timedelta
import logging
import voluptuous as vol

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_DEVICES, CONF_TIMEOUT
from homeassistant.core import Config, HomeAssistant
from homeassistant.helpers import discovery
import homeassistant.helpers.config_validation as cv
from homeassistant.exceptions import ConfigEntryNotReady

from .const import (
    CONF_API_KEY,
    CONF_API_SECRET,
    CONF_CURRENCY,
    CONF_ORGANIZATION_ID,
    CURRENCY_BTC,
    DOMAIN,
    STARTUP_MESSAGE,
)
from .nicehash import NiceHashPrivateClient

_LOGGER = logging.getLogger(__name__)

CONFIG_SCHEMA = vol.Schema(
    {
        DOMAIN: vol.Schema(
            {
                vol.Required(CONF_ORGANIZATION_ID): cv.string,
                vol.Required(CONF_API_KEY): cv.string,
                vol.Required(CONF_API_SECRET): cv.string,
                vol.Required(CONF_CURRENCY, default=CURRENCY_BTC): cv.string,
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
    currency = nicehash_config.get(CONF_CURRENCY)

    client = NiceHashPrivateClient(organization_id, api_key, api_secret)

    try:
        await client.get_accounts()
        hass.data[DOMAIN]["client"] = client
        hass.data[DOMAIN]["currency"] = currency
        await discovery.async_load_platform(hass, "sensor", DOMAIN, {}, config)
        return True
    except Exception as err:
        _LOGGER.error(f"Unable to access NiceHash accounts\n{err}")
        return False
