"""
Sensor platform for NiceHash
"""
from datetime import datetime, timedelta
import logging
import os

from homeassistant.components.sensor import PLATFORM_SCHEMA
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import Config, HomeAssistant
from homeassistant.helpers.entity import Entity
from homeassistant.util import Throttle

from .const import (
    CURRENCY_BTC,
    CURRENCY_EUR,
    CURRENCY_USD,
    DEFAULT_NAME,
    DOMAIN,
    ICON_CURRENCY_BTC,
    ICON_TEMPERATURE,
)
from .nicehash import NiceHashPrivateClient, NiceHashPublicClient

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
    client = data.get("client")
    currency = data.get("currency")
    accounts_coordinator = data.get("accounts_coordinator")
    rigs_coordinator = data.get("rigs_coordinator")

    # Add account balance sensor(s)
    btc_balance_sensor = NiceHashBalanceSensor(
        accounts_coordinator, client.organization_id, CURRENCY_BTC
    )
    if currency == CURRENCY_BTC:
        async_add_entities([btc_balance_sensor], True)
    else:
        async_add_entities(
            [
                btc_balance_sensor,
                NiceHashBalanceSensor(
                    accounts_coordinator, client.organization_id, currency
                ),
            ],
            True,
        )

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

    def __init__(self, coordinator, organization_id, currency):
        """Initialize the sensor"""
        _LOGGER.debug(f"Account Balance Sensor: {currency}")
        self.coordinator = coordinator
        self.currency = currency
        self._organization_id = organization_id
        self._available = 0.00
        self._pending = 0.00
        self._total_balance = 0.00
        self._exchange_rate = 0.00

    @property
    def name(self):
        """Sensor name"""
        return f"{DEFAULT_NAME} Account Balance {self.currency}"

    @property
    def unique_id(self):
        """Unique entity id"""
        return f"{self._organization_id}:{self.currency}"

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
        if self.currency == CURRENCY_BTC:
            return self._available
        else:
            exchange_rates = self.coordinator.data.get("exchange_rates")
            self._exchange_rate = exchange_rates.get(f"{CURRENCY_BTC}-{self.currency}")
            return round(self._available * self._exchange_rate, 2)

    @property
    def icon(self):
        """Sensor icon"""
        return ICON_CURRENCY_BTC

    @property
    def unit_of_measurement(self):
        """Sensor unit of measurement"""
        return self.currency

    @property
    def device_state_attributes(self):
        """Sensor device state attributes"""
        return {
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
            num_devices = len(devices)
            self._num_devices = num_devices

            if num_devices > 0:
                _LOGGER.debug(f"{self._name}: Found {num_devices} devices")
                self._temps = []
                for device in devices:
                    temp = int(device.get("temperature"))
                    self._temps.append(temp)
                    if temp < 0:
                        # Ignore inactive devices
                        continue
                    if temp > highest_temp:
                        highest_temp = temp
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
        return "C"

    @property
    def device_state_attributes(self):
        """Sensor device state attributes"""
        return {
            "temperatures": self._temps,
            "num_devices": self._num_devices,
        }

    async def async_added_to_hass(self):
        """Connect to dispatcher listening for entity data notifications"""
        self.async_on_remove(
            self.coordinator.async_add_listener(self.async_write_ha_state)
        )

    async def async_update(self):
        """Update entity"""
        await self.coordinator.async_request_refresh()
