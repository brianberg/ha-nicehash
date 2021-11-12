"""
Sensor platform for NiceHash
"""
import logging

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import ATTR_ATTRIBUTION
from homeassistant.core import Config, HomeAssistant

from .const import (
    BALANCE_TYPE_AVAILABLE,
    BALANCE_TYPE_PENDING,
    BALANCE_TYPE_TOTAL,
    CURRENCY_BTC,
    CURRENCY_EUR,
    CURRENCY_USD,
    DOMAIN,
    DEVICE_LOAD,
    DEVICE_RPM,
    DEVICE_SPEED_RATE,
    DEVICE_SPEED_ALGORITHM,
)
from .nicehash import (
    MiningRig,
    MiningRigDevice,
    NiceHashPrivateClient,
    NiceHashPublicClient,
)
from .control_switches import (
    GPUSwitch
)


_LOGGER = logging.getLogger(__name__)


async def async_setup_platform(
    hass: HomeAssistant, config: Config, async_add_entities, discovery_info=None
):
    """Setup NiceHash sensor platform"""
    _LOGGER.debug("Creating new NiceHash switch components")

    data = hass.data[DOMAIN]
    # Configuration
    organization_id = data.get("organization_id")
    client = data.get("client")
    # Options
    currency = data.get("currency")
    balances_enabled = data.get("balances_enabled")
    payouts_enabled = data.get("payouts_enabled")
    rigs_enabled = data.get("rigs_enabled")
    devices_enabled = data.get("devices_enabled")


    # Mining rig and device sensors
    if rigs_enabled or devices_enabled:
        rigs_coordinator = data.get("rigs_coordinator")
        rig_data = await client.get_mining_rigs()
        mining_rigs = rig_data.get("miningRigs")
        _LOGGER.debug(f"Found {len(mining_rigs)} rigs")

        if devices_enabled:
            _LOGGER.debug("Device sensors enabled")
            device_switches = create_device_switches(mining_rigs, rigs_coordinator,client)
            async_add_entities(device_switches, True)



def create_device_switches(mining_rigs, coordinator, client):
    device_switches = []
    for rig_data in mining_rigs:
        rig = MiningRig(rig_data)
        devices = rig.devices.values()
        _LOGGER.debug(
            f"Found {len(devices)} device switches(s) for {rig.name} ({rig.id})"
        )
        for device in devices:
            _LOGGER.debug(f"Creating {device.name} ({device.id}) switches")
            device_switches.append(GPUSwitch(coordinator, rig, device, client))

    return device_switches
    