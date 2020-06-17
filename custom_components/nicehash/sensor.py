"""
Sensor platform for NiceHash
"""
from datetime import datetime, timedelta
import logging
import os

from homeassistant.components.sensor import PLATFORM_SCHEMA
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import ATTR_ATTRIBUTION
from homeassistant.core import Config, HomeAssistant
from homeassistant.helpers.entity import Entity
from homeassistant.util import Throttle

from .const import (
    BALANCE_TYPE_AVAILABLE,
    BALANCE_TYPE_PENDING,
    BALANCE_TYPE_TOTAL,
    CURRENCY_BTC,
    CURRENCY_EUR,
    CURRENCY_USD,
    DEFAULT_NAME,
    DEVICE_STATUS_INACTIVE,
    DOMAIN,
    ICON_CURRENCY_BTC,
    ICON_CURRENCY_EUR,
    ICON_CURRENCY_USD,
    ICON_TEMPERATURE,
)
from .nicehash import NiceHashPrivateClient, NiceHashPublicClient

ATTRIBUTION = "Data provided by NiceHash"
FORMAT_DATETIME = "%d-%m-%Y %H:%M"
SCAN_INTERVAL_RIGS = timedelta(minutes=1)
SCAN_INTERVAL_ACCOUNTS = timedelta(minutes=60)

_LOGGER = logging.getLogger(__name__)


async def async_setup_platform(
    hass: HomeAssistant, config: Config, async_add_entities, discovery_info=None
):
    """Setup NiceHash sensor platform"""
    _LOGGER.debug("Creating new NiceHash sensor components")

    data = hass.data[DOMAIN]
    organization_id = data.get("organization_id")
    client = data.get("client")
    currency = data.get("currency")
    accounts_coordinator = data.get("accounts_coordinator")
    rigs_coordinator = data.get("rigs_coordinator")

    # Add account balance sensors
    balance_sensors = [
        NiceHashBalanceSensor(
            accounts_coordinator,
            organization_id,
            currency=CURRENCY_BTC,
            balance_type=BALANCE_TYPE_AVAILABLE,
        ),
        NiceHashBalanceSensor(
            accounts_coordinator,
            organization_id,
            currency=CURRENCY_BTC,
            balance_type=BALANCE_TYPE_PENDING,
        ),
        NiceHashBalanceSensor(
            accounts_coordinator,
            organization_id,
            currency=CURRENCY_BTC,
            balance_type=BALANCE_TYPE_TOTAL,
        ),
    ]
    if currency == CURRENCY_USD or currency == CURRENCY_EUR:
        balance_sensors.append(
            NiceHashBalanceSensor(
                accounts_coordinator,
                organization_id,
                currency=currency,
                balance_type=BALANCE_TYPE_AVAILABLE,
            )
        )
        balance_sensors.append(
            NiceHashBalanceSensor(
                accounts_coordinator,
                organization_id,
                currency=currency,
                balance_type=BALANCE_TYPE_PENDING,
            )
        )
        balance_sensors.append(
            NiceHashBalanceSensor(
                accounts_coordinator,
                organization_id,
                currency=currency,
                balance_type=BALANCE_TYPE_TOTAL,
            )
        )
    else:
        _LOGGER.warn("Invalid currency: must be EUR or USD")

    async_add_entities(balance_sensors, True)

    # Add mining rig sensors
    rig_data = await client.get_mining_rigs()
    mining_rigs = rig_data["miningRigs"]
    # Add temperature sensors
    async_add_entities(
        [NiceHashRigTemperatureSensor(rigs_coordinator, rig) for rig in mining_rigs],
        True,
    )


class NiceHashBalanceSensor(Entity):
    """NiceHash Account Balance Sensor"""

    def __init__(
        self,
        coordinator,
        organization_id,
        currency,
        balance_type=BALANCE_TYPE_AVAILABLE,
    ):
        """Initialize the sensor"""
        _LOGGER.debug(f"Account Balance Sensor: {balance_type} {currency}")
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
        """No need to pool, Coordinator notifies entity of updates"""
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
        self._pending = float(total.get("pending"))
        self._available = float(total.get("available"))
        self._total_balance = float(total.get("totalBalance"))

        if self.balance_type == BALANCE_TYPE_TOTAL:
            balance = self._total_balance
        elif self.balance_type == BALANCE_TYPE_PENDING:
            balance = self._pending
        else:
            balance = self._available

        if self.currency == CURRENCY_BTC:
            return balance
        else:
            exchange_rates = self.coordinator.data.get("exchange_rates")
            self._exchange_rate = exchange_rates.get(f"{CURRENCY_BTC}-{self.currency}")
            return round(balance * self._exchange_rate, 2)

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
            ATTR_ATTRIBUTION: ATTRIBUTION,
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


class NiceHashRigTemperatureSensor(Entity):
    """NichHash Mining Rig Temperature Sensor"""

    def __init__(self, coordinator, rig):
        """Initialize the sensor"""
        self.coordinator = coordinator
        self._rig_id = rig["rigId"]
        self._name = rig["name"]
        self._temps = []
        self._num_devices = 0
        self._num_active_devices = 0
        _LOGGER.debug(f"Mining Rig Temperature Sensor: {self._name} ({self._rig_id})")

    @property
    def name(self):
        """Sensor name"""
        return self._name

    @property
    def unique_id(self):
        """Unique entity id"""
        return self._rig_id

    @property
    def should_poll(self):
        """No need to pool, Coordinator notifies entity of updates"""
        return False

    @property
    def available(self):
        """Whether sensor is available"""
        return self.coordinator.last_update_success

    @property
    def state(self):
        """Sensor state"""
        mining_rigs = self.coordinator.data.get("miningRigs")
        try:
            rig_data = mining_rigs.get(self._rig_id)
            devices = rig_data.get("devices")
            highest_temp = 0
            self._temps = []
            self._num_devices = len(devices)

            if self._num_devices > 0:
                _LOGGER.debug(f"{self._name}: Found {self._num_devices} devices")
                for device in devices:
                    status = device.get("status").get("enumName")
                    # Ignore inactive devices
                    if status == DEVICE_STATUS_INACTIVE:
                        continue
                    temp = int(device.get("temperature"))
                    self._temps.append(temp)
                    if temp > highest_temp:
                        highest_temp = temp

                self._num_active_devices = len(self._temps)
                return highest_temp
            else:
                _LOGGER.debug(f"{self._name}: No devices found")
                self._num_devices = 0
                return 0
        except Exception as e:
            _LOGGER.error(f"Unable to get mining rig {self._rig_id}\n{e}")
            return 0

    @property
    def icon(self):
        """Sensor icon"""
        return ICON_TEMPERATURE

    @property
    def unit_of_measurement(self):
        """Sensor unit of measurement"""
        # Not Celsius because then HA might convert to Fahrenheit
        return "C"

    @property
    def device_state_attributes(self):
        """Sensor device state attributes"""
        return {
            ATTR_ATTRIBUTION: ATTRIBUTION,
            "temperatures": self._temps,
            "active_devices": self._num_active_devices,
            "total_devices": self._num_devices,
        }

    async def async_added_to_hass(self):
        """Connect to dispatcher listening for entity data notifications"""
        self.async_on_remove(
            self.coordinator.async_add_listener(self.async_write_ha_state)
        )

    async def async_update(self):
        """Update entity"""
        await self.coordinator.async_request_refresh()
