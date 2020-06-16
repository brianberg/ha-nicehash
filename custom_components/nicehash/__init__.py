"""
Integrates NiceHash with Home Assistant

For more details about this integration, please refer to
https://github.com/brianberg/ha-nicehash
"""
from datetime import timedelta
import logging
import voluptuous as vol

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_DEVICES, CONF_TIMEOUT
from homeassistant.core import Config, HomeAssistant
from homeassistant.helpers import discovery
import homeassistant.helpers.config_validation as cv
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed
from homeassistant.exceptions import PlatformNotReady

from .const import (
    CONF_API_KEY,
    CONF_API_SECRET,
    CONF_CURRENCY,
    CONF_ORGANIZATION_ID,
    CURRENCY_BTC,
    DOMAIN,
    STARTUP_MESSAGE,
)
from .nicehash import NiceHashPrivateClient, NiceHashPublicClient

SCAN_INTERVAL_RIGS = timedelta(minutes=1)
SCAN_INTERVAL_ACCOUNTS = timedelta(minutes=60)

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

    hass.data[DOMAIN]["client"] = client
    hass.data[DOMAIN]["currency"] = currency
    hass.data[DOMAIN]["accounts_coordinator"] = accounts_coordinator
    hass.data[DOMAIN]["rigs_coordinator"] = rigs_coordinator

    await discovery.async_load_platform(hass, "sensor", DOMAIN, {}, config)

    return True


class NiceHashAccountsDataUpdateCoordinator(DataUpdateCoordinator):
    """Manages fetching accounts data from NiceHash API"""

    def __init__(self, hass: HomeAssistant, client: NiceHashPrivateClient):
        """Initialize"""
        self.name = f"{DOMAIN}_Accounts_Coordinator"
        self._client = client

        super().__init__(
            hass, _LOGGER, name=self.name, update_interval=SCAN_INTERVAL_ACCOUNTS
        )

    async def _async_update_data(self):
        """Update accounts data and exchange rates"""
        try:
            accounts = await self._client.get_accounts()
            exchange_rates = await NiceHashPublicClient().get_exchange_rates()
            rates_dict = dict()
            for rate in exchange_rates:
                fromCurrency = rate.get("fromCurrency")
                toCurrency = rate.get("toCurrency")
                exchange_rate = float(rate.get("exchangeRate"))
                rates_dict[f"{fromCurrency}-{toCurrency}"] = exchange_rate
            return {
                "accounts": accounts,
                "exchange_rates": rates_dict,
            }
        except Exception as e:
            raise UpdateFailed(e)


class NiceHashMiningRigsDataUpdateCoordinator(DataUpdateCoordinator):
    """Manages fetching mining rigs data from NiceHash API"""

    def __init__(self, hass: HomeAssistant, client: NiceHashPrivateClient):
        """Initialize"""
        self.name = f"{DOMAIN}_Mining_Rigs_Coordinator"
        self._client = client

        super().__init__(
            hass, _LOGGER, name=self.name, update_interval=SCAN_INTERVAL_RIGS
        )

    async def _async_update_data(self):
        """Update mining rigs data"""
        try:
            data = await self._client.get_mining_rigs()
            mining_rigs = data.get("miningRigs")
            rigs_dict = dict()
            for rig in mining_rigs:
                rig_id = rig.get("rigId")
                rigs_dict[f"{rig_id}"] = rig
            data["miningRigs"] = rigs_dict
            return data
        except Exception as e:
            raise UpdateFailed(e)
