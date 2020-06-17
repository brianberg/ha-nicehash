"""
NiceHash Mining Rig Temperature Sensor
"""
from datetime import datetime
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
    DEVICE_STATUS_UNKNOWN,
    ICON_CURRENCY_BTC,
    ICON_CURRENCY_EUR,
    ICON_CURRENCY_USD,
    ICON_PULSE,
    ICON_TEMPERATURE,
)

ATTRIBUTION = "Data provided by NiceHash"
FORMAT_DATETIME = "%d-%m-%Y %H:%M"

_LOGGER = logging.getLogger(__name__)


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
    """Displays highest temperature of active mining rig devices"""

    def __init__(self, coordinator, rig):
        """Initialize the sensor"""
        self.coordinator = coordinator
        self._rig_id = rig["rigId"]
        self._rig_name = rig["name"]
        self._temps = []
        self._num_devices = 0
        _LOGGER.debug(
            f"Mining Rig Temperature Sensor: {self._rig_name} ({self._rig_id})"
        )

    @property
    def name(self):
        """Sensor name"""
        return f"{self._rig_name} Temperature"

    @property
    def unique_id(self):
        """Unique entity id"""
        return f"{self._rig_id}:temperature"

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
        self._highest_temp = 0
        try:
            rig_data = mining_rigs.get(self._rig_id)
            devices = rig_data.get("devices")
            self._temps = []
            self._num_devices = len(devices)

            if self._num_devices > 0:
                for device in devices:
                    temp = int(device.get("temperature"))
                    self._temps.append(temp)
                    if temp > self._highest_temp:
                        self._highest_temp = temp
            else:
                self._num_devices = 0
        except Exception as e:
            _LOGGER.error(f"Unable to get mining rig ({self._rig_id}) temperature\n{e}")

        return self._highest_temp

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
            "highest_temperature": self._highest_temp,
            "temperatures": self._temps,
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


class NiceHashRigStatusSensor(Entity):
    """Displays status of a mining rig"""

    def __init__(self, coordinator, rig):
        """Initialize the sensor"""
        self.coordinator = coordinator
        self._rig_id = rig["rigId"]
        self._rig_name = rig["name"]
        self._status = DEVICE_STATUS_UNKNOWN
        self._status_time = None
        self._num_devices = 0
        self._unit_of_measurement = "\u200b"
        _LOGGER.debug(f"Mining Rig Status Sensor: {self._rig_name} ({self._rig_id})")

    @property
    def name(self):
        """Sensor name"""
        return f"{self._rig_name} Status"

    @property
    def unique_id(self):
        """Unique entity id"""
        return f"{self._rig_id}:status"

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
        status = DEVICE_STATUS_UNKNOWN
        try:
            rig_data = mining_rigs.get(self._rig_id)
            devices = rig_data.get("devices")
            status = rig_data.get("minerStatus")
            status_time_ms = int(rig_data.get("statusTime"))
            self._num_devices = len(devices)
            self._status_time = datetime.fromtimestamp(status_time_ms / 1000.0)
        except Exception as e:
            _LOGGER.error(f"Unable to get mining rig ({self._rig_id}) status\n{e}")
            self._status_time = None
            status = DEVICE_STATUS_UNKNOWN

        self._status = status[0].upper() + status.lower()[1:]
        return self._status

    @property
    def icon(self):
        """Sensor icon"""
        return ICON_PULSE

    @property
    def unit_of_measurement(self):
        """Sensor unit of measurement"""
        return self._unit_of_measurement

    @property
    def device_state_attributes(self):
        """Sensor device state attributes"""
        return {
            ATTR_ATTRIBUTION: ATTRIBUTION,
            "status": self._status,
            "status_time": self._status_time.strftime(FORMAT_DATETIME),
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
