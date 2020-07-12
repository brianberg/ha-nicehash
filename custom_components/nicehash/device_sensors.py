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
from .coordinators import MiningRigsDataUpdateCoordinator
from .nicehash import MiningRig, MiningRigDevice

_LOGGER = logging.getLogger(__name__)


class DeviceSensor(Entity):
    """
    Mining rig device sensor
    """

    def __init__(
        self,
        coordinator: MiningRigsDataUpdateCoordinator,
        rig: MiningRig,
        device: MiningRigDevice,
    ):
        """Initialize the sensor"""
        self.coordinator = coordinator
        self._rig_id = rig.id
        self._rig_name = rig.name
        self._device_id = device.id
        self._device_name = device.name

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

    async def async_added_to_hass(self):
        """Connect to dispatcher listening for entity data notifications"""
        self.async_on_remove(
            self.coordinator.async_add_listener(self.async_write_ha_state)
        )

    async def async_update(self):
        """Update entity"""
        await self.coordinator.async_request_refresh()

    def _get_device(self):
        try:
            mining_rigs = self.coordinator.data.get("miningRigs")
            rig = MiningRig(mining_rigs.get(self._rig_id))
            return rig.devices.get(self._device_id)
        except Exception as e:
            _LOGGER.error(f"Unable to get mining device ({self._device_id})\n{e}")


class DeviceStatusSensor(DeviceSensor):
    """
    Displays status of a mining rig device
    """

    _status = "Unknown"

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
        device = self._get_device()
        if device:
            self._status = device.status
        else:
            self._status = "Unknown"

        return self._status

    @property
    def icon(self):
        """Sensor icon"""
        return ICON_PULSE

    @property
    def device_state_attributes(self):
        """Sensor device state attributes"""
        return {
            ATTR_ATTRIBUTION: NICEHASH_ATTRIBUTION,
            "status": self._status,
            "rig": self._rig_name,
        }


class DeviceSpeedSensor(DeviceSensor):
    """
    Displays speed of a mining rig device
    """

    _algorithm = None
    _speed = 0.00
    _speed_unit = "MH"

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
        device = self._get_device()
        if device and len(device.speeds) > 0:
            algorithm = device.speeds[0]
            self._algorithm = algorithm.get("title")
            self._speed = algorithm.get("speed")
            self._speed_unit = algorithm.get("displaySuffix")
        else:
            self._algorithm = "Unknown"
            self._speed = 0.00
            self._speed_unit = "MH"

        return self._speed

    @property
    def icon(self):
        """Sensor icon"""
        return ICON_SPEEDOMETER

    @property
    def unit_of_measurement(self):
        """Sensor unit of measurement"""
        return f"{self._speed_unit}/s"

    @property
    def device_state_attributes(self):
        """Sensor device state attributes"""
        return {
            ATTR_ATTRIBUTION: NICEHASH_ATTRIBUTION,
            "algorithm": self._algorithm,
            "speed": self._speed,
            "speed_unit": self._speed_unit,
            "rig": self._rig_name,
        }


class DeviceAlgorithmSensor(DeviceSensor):
    """
    Displays algorithm of a mining rig device
    """

    _algorithm = None
    _speed = 0.00
    _speed_unit = "MH"

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
        device = self._get_device()
        if device and len(device.speeds) > 0:
            algorithm = device.speeds[0]
            self._algorithm = algorithm.get("title")
            self._speed = algorithm.get("speed")
            self._speed_unit = algorithm.get("displaySuffix")
        else:
            self._algorithm = "Unknown"
            self._speed = 0.00
            self._speed_unit = "MH"

        return self._algorithm

    @property
    def icon(self):
        """Sensor icon"""
        return ICON_PICKAXE

    @property
    def device_state_attributes(self):
        """Sensor device state attributes"""
        return {
            ATTR_ATTRIBUTION: NICEHASH_ATTRIBUTION,
            "algorithm": self._algorithm,
            "speed": self._speed,
            "speed_unit": self._speed_unit,
            "rig": self._rig_name,
        }


class DeviceTemperatureSensor(DeviceSensor):
    """
    Displays temperature of a mining rig device
    """

    _temperature = 0

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
        device = self._get_device()
        if device:
            self._temperature = device.temperature
        else:
            self._temperature = 0

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

    @property
    def device_state_attributes(self):
        """Sensor device state attributes"""
        return {
            ATTR_ATTRIBUTION: NICEHASH_ATTRIBUTION,
            "temperature": self._temperature,
            "rig": self._rig_name,
        }


class DeviceLoadSensor(DeviceSensor):
    """
    Displays load of a mining rig device
    """

    _load = 0

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
        device = self._get_device()
        if device:
            self._load = device.load
        else:
            self._load = 0

        return self._load

    @property
    def icon(self):
        """Sensor icon"""
        return ICON_SPEEDOMETER

    @property
    def unit_of_measurement(self):
        """Sensor unit of measurement"""
        return "%"

    @property
    def device_state_attributes(self):
        """Sensor device state attributes"""
        return {
            ATTR_ATTRIBUTION: NICEHASH_ATTRIBUTION,
            "load": self._load,
            "rig": self._rig_name,
        }


class DeviceRPMSensor(DeviceSensor):
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
        device = self._get_device()
        if device:
            self._rpm = device.rpm
        else:
            self._rpm = 0

        return self._rpm

    @property
    def icon(self):
        """Sensor icon"""
        return ICON_SPEEDOMETER

    @property
    def unit_of_measurement(self):
        """Sensor unit of measurement"""
        return "RPM"

    @property
    def device_state_attributes(self):
        """Sensor device state attributes"""
        return {
            ATTR_ATTRIBUTION: NICEHASH_ATTRIBUTION,
            "rpm": self._rpm,
            "rig": self._rig_name,
        }

