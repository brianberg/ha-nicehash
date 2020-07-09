"""
NiceHash Rig Device Sensors
"""
from datetime import datetime
import logging

from homeassistant.const import ATTR_ATTRIBUTION
from homeassistant.helpers.entity import Entity

from .const import (
    DEVICE_STATUS_UNKNOWN,
    DEVICE_LOAD,
    DEVICE_RPM,
    DEVICE_SPEED_ALGORITHM,
    DEVICE_SPEED_RATE,
    ICON_PICKAXE,
    ICON_PULSE,
    ICON_THERMOMETER,
    ICON_SPEEDOMETER,
    NICEHASH_ATTRIBUTION,
)

_LOGGER = logging.getLogger(__name__)


class NiceHashDeviceSensor(Entity):
    """
    Mining rig device sensor
    """

    def __init__(self, coordinator, rig, device):
        """Initialize the sensor"""
        self.coordinator = coordinator
        self._rig_id = rig.get("rigId")
        self._rig_name = rig.get("name")
        self._device_name = device.get("name")
        self._device_id = device.get("id")
        self._status = DEVICE_STATUS_UNKNOWN
        self._load = 0
        self._rpm = 0
        self._algorithm = None
        self._speed = 0
        self._speed_title = "Unknown"
        self._speed_unit = "MH"
        self._temperature = 0

    @property
    def name(self):
        """Sensor name"""
        return f"{self._device_name}"

    @property
    def should_poll(self):
        """No need to poll, Coordinator notifies entity of updates"""
        return False

    @property
    def available(self):
        """Whether sensor is available"""
        return self.coordinator.last_update_success

    @property
    def icon(self):
        """Sensor icon"""
        return ICON_PICKAXE

    @property
    def unit_of_measurement(self):
        """Sensor unit of measurement"""
        return None

    @property
    def device_state_attributes(self):
        """Sensor device state attributes"""
        return {
            ATTR_ATTRIBUTION: NICEHASH_ATTRIBUTION,
            "status": self._status,
            "algorithm": self._algorithm,
            "speed": self._speed,
            "speed_unit": f"{self._speed_unit}/s",
            "temperature": self._temperature,
            "load": f"{self._load}%",
            "rpm": self._rpm,
        }

    async def async_added_to_hass(self):
        """Connect to dispatcher listening for entity data notifications"""
        self.async_on_remove(
            self.coordinator.async_add_listener(self.async_write_ha_state)
        )

    async def async_update(self):
        """Update entity"""
        await self.coordinator.async_request_refresh()
        mining_rigs = self.coordinator.data.get("miningRigs")
        try:
            rig_data = mining_rigs.get(self._rig_id)
            devices = rig_data.get("devices")
            for device in devices:
                if device.get("id") == self._device_id:
                    algorithms = device.get("speeds")
                    if len(algorithms) > 0:
                        status = device.get("status")
                        self._status = status.get("description")
                        algorithm = algorithms[0]
                        self._load = float(device.get("load"))
                        self._rpm = float(device.get("revolutionsPerMinute"))
                        self._algorithm = algorithm.get("title")
                        self._speed = float(algorithm.get("speed"))
                        self._speed_title = algorithm.get("title")
                        self._speed_unit = algorithm.get("displaySuffix")
                        self._temperature = int(device.get("temperature"))
                    else:
                        self._status = DEVICE_STATUS_UNKNOWN
                        self._load = 0
                        self._rpm = 0
                        self._speed = 0
                        self._speed_title = "Unknown"
                        self._speed_unit = "MH"
                        self._algorithm = None
        except Exception as e:
            _LOGGER.error(f"Unable to get mining device ({self._device_id}) speed\n{e}")
            self._status = DEVICE_STATUS_UNKNOWN
            self._load = 0
            self._rpm = 0
            self._speed = 0
            self._speed_title = "Unknown"
            self._speed_unit = "MH"
            self._algorithm = None


class NiceHashDeviceStatusSensor(NiceHashDeviceSensor):
    """
    Displays status of a mining rig device
    """

    @property
    def name(self):
        """Sensor name"""
        return f"{self._device_name} Status"

    @property
    def unique_id(self):
        """Unique entity id"""
        return f"{self._device_id}:status"

    @property
    def state(self):
        """Sensor state"""
        return self._status

    @property
    def icon(self):
        """Sensor icon"""
        return ICON_PULSE


class NiceHashDeviceSpeedSensor(NiceHashDeviceSensor):
    """
    Displays speed of a mining rig device
    """

    @property
    def name(self):
        """Sensor name"""
        return f"{self._device_name} Speed"

    @property
    def unique_id(self):
        """Unique entity id"""
        return f"{self._device_id}:speed"

    @property
    def state(self):
        """Sensor state"""
        return self._speed

    @property
    def icon(self):
        """Sensor icon"""
        return ICON_SPEEDOMETER

    @property
    def unit_of_measurement(self):
        """Sensor unit of measurement"""
        return f"{self._speed_unit}/s"


class NiceHashDeviceAlgorithmSensor(NiceHashDeviceSensor):
    """
    Displays algorithm of a mining rig device
    """

    @property
    def name(self):
        """Sensor name"""
        return f"{self._device_name} Algorithm"

    @property
    def unique_id(self):
        """Unique entity id"""
        return f"{self._device_id}:algorithm"

    @property
    def state(self):
        """Sensor state"""
        return self._algorithm

    @property
    def icon(self):
        """Sensor icon"""
        return ICON_PICKAXE


class NiceHashDeviceTemperatureSensor(NiceHashDeviceSensor):
    """
    Displays temperature of a mining rig device
    """

    @property
    def name(self):
        """Sensor name"""
        return f"{self._device_name} Temperature"

    @property
    def unique_id(self):
        """Unique entity id"""
        return f"{self._device_id}:temperature"

    @property
    def state(self):
        """Sensor state"""
        return self._temperature

    @property
    def icon(self):
        """Sensor icon"""
        return ICON_THERMOMETER

    @property
    def unit_of_measurement(self):
        """Sensor unit of measurement"""
        # Not Celsius because then HA might convert to Fahrenheit
        return "C"


class NiceHashDeviceLoadSensor(NiceHashDeviceSensor):
    """
    Displays load of a mining rig device
    """

    @property
    def name(self):
        """Sensor name"""
        return f"{self._device_name} Load"

    @property
    def unique_id(self):
        """Unique entity id"""
        return f"{self._device_id}:load"

    @property
    def state(self):
        """Sensor state"""
        return self._load

    @property
    def icon(self):
        """Sensor icon"""
        return ICON_SPEEDOMETER

    @property
    def unit_of_measurement(self):
        """Sensor unit of measurement"""
        return "%"


class NiceHashDeviceRPMSensor(NiceHashDeviceSensor):
    """
    Displays RPM of a mining rig device
    """

    @property
    def name(self):
        """Sensor name"""
        return f"{self._device_name} RPM"

    @property
    def unique_id(self):
        """Unique entity id"""
        return f"{self._device_id}:rpm"

    @property
    def state(self):
        """Sensor state"""
        return self._rpm

    @property
    def icon(self):
        """Sensor icon"""
        return ICON_SPEEDOMETER

    @property
    def unit_of_measurement(self):
        """Sensor unit of measurement"""
        return "RPM"

