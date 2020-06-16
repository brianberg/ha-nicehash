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

    client = hass.data[DOMAIN]["client"]
    currency = hass.data[DOMAIN]["currency"]

    # Add account balance sensor
    async_add_entities(
        [NiceHashBalanceSensor(client, currency, SCAN_INTERVAL_ACCOUNTS)], True
    )

    # Add mining rig sensors
    rig_data = await client.get_mining_rigs()
    mining_rigs = rig_data["miningRigs"]
    # Add temperature sensors
    async_add_entities(
        [
            NiceHashRigTemperatureSensor(client, rig, SCAN_INTERVAL_RIGS)
            for rig in mining_rigs
        ],
        True,
    )


class NiceHashBalanceSensor(Entity):
    """NiceHash Account Balance Sensor"""

    def __init__(self, client, currency, update_frequency):
        """Initialize the sensor"""
        _LOGGER.debug(f"Account Balance Sensor: {currency}")
        self._client = client
        self._public_client = NiceHashPublicClient()
        self._currency = currency
        self._state = None
        self._last_update = None
        self.async_update = Throttle(update_frequency)(self._async_update)

    @property
    def name(self):
        """Sensor name"""
        return f"{DEFAULT_NAME} Account Balance"

    @property
    def unique_id(self):
        """Unique entity id"""
        return f"{self._client.organization_id}:{self._currency}"

    @property
    def icon(self):
        """Sensor icon"""
        return ICON_CURRENCY_BTC

    @property
    def state(self):
        """Sensor state"""
        return self._state

    @property
    def unit_of_measurement(self):
        """Sensor unit of measurement"""
        return self._currency

    @property
    def device_state_attributes(self):
        """Sensor device attributes"""
        return {"last_update": self._last_update}

    async def _async_update(self):

        try:
            account_data = await self._client.get_accounts()
            available = float(account_data["total"]["available"])

            if self._currency == CURRENCY_BTC:
                # Account balance is in BTC
                self._state = available
            else:
                # Convert to selected currency via exchange rates
                exchange_rates = await self._public_client.get_exchange_rates()
                self._last_update = datetime.today().strftime(FORMAT_DATETIME)
                for rate in exchange_rates:
                    isBTC = rate["fromCurrency"] == CURRENCY_BTC
                    toCurrency = rate["toCurrency"]
                    if isBTC and toCurrency == self._currency:
                        rate = float(rate["exchangeRate"])
                        self._state = round(available * rate, 2)
        except Exception as err:
            _LOGGER.error(f"Unable to get account balance\n{err}")
            pass


class NiceHashRigTemperatureSensor(Entity):
    """NichHash Mining Rig Temperature Sensor"""

    def __init__(self, client, rig, update_frequency):
        """Initialize the sensor"""
        self._client = client
        self._rig_id = rig["rigId"]
        self._name = rig["name"]
        _LOGGER.debug(f"Mining Rig Temperature Sensor: {self._name} ({self._rig_id})")
        self._state = None
        self._last_update = None
        self.async_update = Throttle(update_frequency)(self._async_update)

    @property
    def name(self):
        """Sensor name"""
        return self._name

    @property
    def unique_id(self):
        """Unique entity id"""
        return self._rig_id

    @property
    def state(self):
        """Sensor state"""
        return self._state

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
        """Sensore device state attributes"""
        return {
            "last_update": self._last_update,
        }

    async def _async_update(self):
        try:
            data = await self._client.get_mining_rig(self._rig_id)
            self._last_update = datetime.today().strftime(FORMAT_DATETIME)
            devices = data["devices"]
            highest_temp = 0

            if len(devices) > 0:
                _LOGGER.debug(f"{self._name}: Found {len(devices)} devices")
                for device in devices:
                    temp = int(device["temperature"])
                    if temp < 0:
                        # Ignore inactive devices
                        continue
                    if temp > highest_temp:
                        highest_temp = temp
                    self._state = highest_temp
            else:
                _LOGGER.debug(f"{self._name}: No devices found")
                self._state = None

        except Exception as err:
            _LOGGER.error(f"Unable to get mining rig {self._rig_id}\n{err}")
            pass
