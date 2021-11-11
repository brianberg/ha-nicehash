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
from .const import DOMAIN
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


    def _get_device(self):
        try:
            mining_rigs = self.coordinator.data.get("miningRigs")
            rig = MiningRig(mining_rigs.get(self._rig_id))
            return rig.devices.get(self._device_id)
        except Exception as e:
            _LOGGER.error(f"Unable to get mining device ({self._device_id})\n{e}")


class GPUSwitch(DeviceSwitch):

    _is_on = False

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
        return self._is_on

    def turn_on(self, **kwargs):
        """Turn the switch on."""
        self._is_on = True
        asyncio.run(self._client.toggle_device(self._device_id, "START", self._rig_id))

    def turn_off(self, **kwargs):
        """Turn the switch off."""
        self._is_on = False
        asyncio.run(self._client.toggle_device(self._device_id, "STOP", self._rig_id))