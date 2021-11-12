"""
NiceHash Rig controls
"""
from datetime import datetime
import logging

from homeassistant.const import ATTR_ATTRIBUTION
from homeassistant.helpers.entity import Entity
from homeassistant.components.switch import SwitchEntity

from .coordinators import MiningRigsDataUpdateCoordinator
from .nicehash import MiningRig, MiningRigDevice, NiceHashPrivateClient
from .const import DOMAIN, NICEHASH_ATTRIBUTION
import asyncio

class DeviceSwitch(SwitchEntity):
    def __init__(
        self,
        coordinator: MiningRigsDataUpdateCoordinator,
        rig: MiningRig,
        device: MiningRigDevice,
        client: NiceHashPrivateClient,
    ):
        """Initialize the switch"""        
        self.coordinator = coordinator
        self._rig_id = rig.id
        self._rig_name = rig.name
        self._device_id = device.id
        self._device_name = device.name
        self._client = client
        self._status = device.status


    def _get_device(self):
        try:
            mining_rigs = self.coordinator.data.get("miningRigs")
            rig = MiningRig(mining_rigs.get(self._rig_id))
            return rig.devices.get(self._device_id)
        except Exception as e:
            _LOGGER.error(f"Unable to get mining device ({self._device_id})\n{e}")


class GPUSwitch(DeviceSwitch):

    _is_on = False
    _last_response = "N/A"

    @property
    def name(self):
        """switch name"""
        return f"{self._device_name} Switch"

    @property
    def unique_id(self):
        """Unique entity id"""
        return f"{self._device_id}:switch"

    @property
    def is_on(self):
        device = self._get_device()
        if device.status == "Mining":
            self._is_on = True
        elif device:
            self._is_on = False
        else:
            self._is_on = "unavailable"    
        return self._is_on

    @property
    def device_state_attributes(self):
        """Sensor device state attributes"""
        return {
            ATTR_ATTRIBUTION: NICEHASH_ATTRIBUTION,
            "status": self._status,
            "device": self._device_name,
            "last_response": self._last_response,
        }

    def turn_on(self, **kwargs):
        """Turn the switch on."""
        self._is_on = True
        response = asyncio.run(self._client.toggle_device(self._device_id, "START", self._rig_id))        
        self._last_response = "Success!" if response["success"] else response["message"]

    def turn_off(self, **kwargs):
        """Turn the switch off."""
        self._is_on = False
        response = asyncio.run(self._client.toggle_device(self._device_id, "STOP", self._rig_id))        
        self._last_response = "Success!" if response["success"] else response["message"]