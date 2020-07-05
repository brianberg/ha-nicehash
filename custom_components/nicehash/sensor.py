"""
Sensor platform for NiceHash
"""
import logging

from homeassistant.components.sensor import PLATFORM_SCHEMA
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import ATTR_ATTRIBUTION
from homeassistant.core import Config, HomeAssistant
from homeassistant.helpers.entity import Entity

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
from .nicehash import NiceHashPrivateClient, NiceHashPublicClient
from .sensors import (
    NiceHashBalanceSensor,
    NiceHashRigStatusSensor,
    NiceHashRigTemperatureSensor,
    NiceHashRigProfitabilitySensor,
    NiceHashDeviceAlgorithmSensor,
    NiceHashDeviceSpeedSensor,
    NiceHashDeviceStatusSensor,
    NiceHashDeviceLoadSensor,
    NiceHashDeviceRPMSensor,
    NiceHashDeviceTemperatureSensor,
)

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
    mining_rigs = rig_data.get("miningRigs")

    # Add status sensors
    async_add_entities(
        [NiceHashRigStatusSensor(rigs_coordinator, rig) for rig in mining_rigs], True,
    )
    # Add temperature sensors
    async_add_entities(
        [NiceHashRigTemperatureSensor(rigs_coordinator, rig) for rig in mining_rigs],
        True,
    )
    # Add profitability sensors
    async_add_entities(
        [NiceHashRigProfitabilitySensor(rigs_coordinator, rig) for rig in mining_rigs],
        True,
    )
    # Add device sensors
    device_sensors = []
    for rig in mining_rigs:
        devices = rig.get("devices")
        for i in range(len(devices)):
            device = devices[i]
            device_sensors.append(
                NiceHashDeviceAlgorithmSensor(rigs_coordinator, rig, device)
            )
            device_sensors.append(
                NiceHashDeviceSpeedSensor(rigs_coordinator, rig, device)
            )
            device_sensors.append(
                NiceHashDeviceStatusSensor(rigs_coordinator, rig, device)
            )
            device_sensors.append(
                NiceHashDeviceTemperatureSensor(rigs_coordinator, rig, device)
            )
            device_sensors.append(
                NiceHashDeviceLoadSensor(rigs_coordinator, rig, device)
            )
            device_sensors.append(
                NiceHashDeviceRPMSensor(rigs_coordinator, rig, device)
            )

    async_add_entities(device_sensors, True)
