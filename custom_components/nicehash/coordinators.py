"""
NiceHash Data Update Coordinators
"""
from datetime import timedelta
import logging

from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import (
    DataUpdateCoordinator,
    UpdateFailed,
)

from .const import (
    CURRENCY_BTC,
    DOMAIN,
)
from .nicehash import NiceHashPrivateClient, NiceHashPublicClient

SCAN_INTERVAL_RIGS = timedelta(minutes=1)
SCAN_INTERVAL_ACCOUNTS = timedelta(minutes=60)
SCAN_INTERVAL_PAYOUTS = timedelta(minutes=60)

_LOGGER = logging.getLogger(__name__)


class AccountsDataUpdateCoordinator(DataUpdateCoordinator):
    """Manages fetching accounts data from NiceHash API"""

    def __init__(self, hass: HomeAssistant, client: NiceHashPrivateClient):
        """Initialize"""
        self.name = f"{DOMAIN}_accounts_coordinator"
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
                # Only care about the Bitcoin exchange rates
                if fromCurrency == CURRENCY_BTC:
                    toCurrency = rate.get("toCurrency")
                    exchange_rate = float(rate.get("exchangeRate"))
                    rates_dict[f"{fromCurrency}-{toCurrency}"] = exchange_rate
            return {
                "accounts": accounts,
                "exchange_rates": rates_dict,
            }
        except Exception as e:
            raise UpdateFailed(e)


class MiningRigsDataUpdateCoordinator(DataUpdateCoordinator):
    """Manages fetching mining rigs data from NiceHash API"""

    def __init__(self, hass: HomeAssistant, client: NiceHashPrivateClient):
        """Initialize"""
        self.name = f"{DOMAIN}_mining_rigs_coordinator"
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


class MiningPayoutsDataUpdateCoordinator(DataUpdateCoordinator):
    """Manages fetching mining rig payout data from NiceHash API"""

    def __init__(self, hass: HomeAssistant, client: NiceHashPrivateClient):
        """Initialize"""
        self.name = f"{DOMAIN}_mining_payouts_coordinator"
        self._client = client

        super().__init__(
            hass, _LOGGER, name=self.name, update_interval=SCAN_INTERVAL_PAYOUTS
        )

    async def _async_update_data(self):
        """Update mining payouts data"""
        try:
            data = await self._client.get_rig_payouts(42)  # 6 (per day) * 7 days
            payouts = data.get("list")
            payouts.sort(key=lambda payout: payout.get("created"))
            return payouts
        except Exception as e:
            raise UpdateFailed(e)
