"""
NiceHash Account Sensors
"""
import logging

from homeassistant.const import ATTR_ATTRIBUTION
from homeassistant.helpers.entity import Entity

from .const import (
    BALANCE_TYPE_AVAILABLE,
    BALANCE_TYPE_PENDING,
    BALANCE_TYPE_TOTAL,
    CURRENCY_BTC,
    CURRENCY_EUR,
    CURRENCY_USD,
    DEFAULT_NAME,
    ICON_CURRENCY_BTC,
    ICON_CURRENCY_EUR,
    ICON_CURRENCY_USD,
    NICEHASH_ATTRIBUTION,
)
from .coordinators import AccountsDataUpdateCoordinator

_LOGGER = logging.getLogger(__name__)


class BalanceSensor(Entity):
    """
    Displays [available|pending|total] balance of an account for a currency
    """

    def __init__(
        self,
        coordinator: AccountsDataUpdateCoordinator,
        organization_id: str,
        currency: str,
        balance_type=BALANCE_TYPE_AVAILABLE,
    ):
        """Initialize the sensor"""
        self.coordinator = coordinator
        self.currency = currency
        self.organization_id = organization_id
        self.balance_type = balance_type
        self._available = 0.00
        self._pending = 0.00
        self._total_balance = 0.00
        self._exchange_rate = 0.00

    @property
    def name(self):
        """Sensor name"""
        balance_type = self.balance_type[0].upper() + self.balance_type[1:]
        return f"{DEFAULT_NAME} {balance_type} Account Balance {self.currency}"

    @property
    def unique_id(self):
        """Unique entity id"""
        return f"{self.organization_id}:{self.currency}:{self.balance_type}"

    @property
    def should_poll(self):
        """No need to poll, Coordinator notifies entity of updates"""
        return False

    @property
    def available(self):
        """Whether sensor is available"""
        return self.coordinator.last_update_success

    @property
    def state(self):
        """Sensor state"""
        accounts = self.coordinator.data.get("accounts")
        total = accounts.get("total")
        pending = float(total.get("pending"))
        available = float(total.get("available"))
        total_balance = float(total.get("totalBalance"))

        if self.currency == CURRENCY_BTC:
            self._pending = pending
            self._available = available
            self._total_balance = total_balance
        else:
            exchange_rates = self.coordinator.data.get("exchange_rates")
            exchange_rate = exchange_rates.get(f"{CURRENCY_BTC}-{self.currency}")
            self._pending = round(pending * exchange_rate, 2)
            self._available = round(available * exchange_rate, 2)
            self._total_balance = round(total_balance * exchange_rate, 2)
            self._exchange_rate = exchange_rate

        if self.balance_type == BALANCE_TYPE_TOTAL:
            return self._total_balance
        elif self.balance_type == BALANCE_TYPE_PENDING:
            return self._pending

        return self._available

    @property
    def icon(self):
        """Sensor icon"""
        if self.currency == CURRENCY_EUR:
            return ICON_CURRENCY_EUR
        elif self.currency == CURRENCY_USD:
            return ICON_CURRENCY_USD
        return ICON_CURRENCY_BTC

    @property
    def unit_of_measurement(self):
        """Sensor unit of measurement"""
        return self.currency

    @property
    def device_state_attributes(self):
        """Sensor device state attributes"""
        return {
            ATTR_ATTRIBUTION: NICEHASH_ATTRIBUTION,
            "total": self._total_balance,
            "available": self._available,
            "pending": self._pending,
            "exchange_rate": self._exchange_rate,
        }

    async def async_added_to_hass(self):
        """Connect to dispatcher listening for entity data notifications"""
        self.async_on_remove(
            self.coordinator.async_add_listener(self.async_write_ha_state)
        )

    async def async_update(self):
        """Update entity"""
        await self.coordinator.async_request_refresh()
