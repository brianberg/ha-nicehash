"""
NiceHash Rig Sensors
"""
from datetime import datetime
import logging

from homeassistant.const import ATTR_ATTRIBUTION
from homeassistant.helpers.entity import Entity

from .const import (
    CURRENCY_BTC,
    DEVICE_STATUS_UNKNOWN,
    FORMAT_DATETIME,
    ICON_CURRENCY_BTC,
    ICON_PULSE,
    ICON_THERMOMETER,
    NICEHASH_ATTRIBUTION,
)

_LOGGER = logging.getLogger(__name__)


class RigTemperatureSensor(Entity):
    """
    Displays highest temperature of active mining rig devices
    """

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
        """No need to poll, Coordinator notifies entity of updates"""
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
        return ICON_THERMOMETER

    @property
    def unit_of_measurement(self):
        """Sensor unit of measurement"""
        # Not Celsius because then HA might convert to Fahrenheit
        return "C"

    @property
    def device_state_attributes(self):
        """Sensor device state attributes"""
        return {
            ATTR_ATTRIBUTION: NICEHASH_ATTRIBUTION,
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


class RigStatusSensor(Entity):
    """
    Displays status of a mining rig
    """

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
        """No need to poll, Coordinator notifies entity of updates"""
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
            ATTR_ATTRIBUTION: NICEHASH_ATTRIBUTION,
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


class RigProfitabilitySensor(Entity):
    """
    Displays profitability of a mining rig
    """

    def __init__(self, coordinator, rig):
        """Initialize the sensor"""
        self.coordinator = coordinator
        self._rig_id = rig["rigId"]
        self._rig_name = rig["name"]
        self._profitability = 0
        self._unpaid_amount = 0
        _LOGGER.debug(
            f"Mining Rig Profitability Sensor: {self._rig_name} ({self._rig_id})"
        )

    @property
    def name(self):
        """Sensor name"""
        return f"{self._rig_name} Profitability"

    @property
    def unique_id(self):
        """Unique entity id"""
        return f"{self._rig_id}:profitability"

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
        mining_rigs = self.coordinator.data.get("miningRigs")
        try:
            rig_data = mining_rigs.get(self._rig_id)
            self._profitability = rig_data.get("profitability")
            self._unpaid_amount = rig_data.get("unpaidAmount")
        except Exception as e:
            _LOGGER.error(f"Unable to get mining rig ({self._rig_id}) status\n{e}")
            self._profitability = 0
            self._unpaid_amount = 0

        return self._profitability

    @property
    def icon(self):
        """Sensor icon"""
        return ICON_CURRENCY_BTC

    @property
    def unit_of_measurement(self):
        """Sensor unit of measurement"""
        return CURRENCY_BTC

    @property
    def device_state_attributes(self):
        """Sensor device state attributes"""
        return {
            ATTR_ATTRIBUTION: NICEHASH_ATTRIBUTION,
            "profitability": self._profitability,
            "unpaid_amount": self._unpaid_amount,
        }

    async def async_added_to_hass(self):
        """Connect to dispatcher listening for entity data notifications"""
        self.async_on_remove(
            self.coordinator.async_add_listener(self.async_write_ha_state)
        )

    async def async_update(self):
        """Update entity"""
        await self.coordinator.async_request_refresh()
