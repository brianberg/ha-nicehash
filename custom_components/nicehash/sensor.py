"""
Sensor platform for NiceHash
"""
import logging

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
from .nicehash import (
    MiningRig,
    MiningRigDevice,
    NiceHashPrivateClient,
    NiceHashPublicClient,
)
from .account_sensors import BalanceSensor
from .payout_sensors import RecentMiningPayoutSensor
from .rig_sensors import (
    RigAlgorithmSensor,
    RigHighTemperatureSensor,
    RigLowTemperatureSensor,
    RigProfitabilitySensor,
    RigStatusSensor,
    RigSpeedSensor,
)
from .device_sensors import (
    DeviceAlgorithmSensor,
    DeviceSpeedSensor,
    DeviceStatusSensor,
    DeviceLoadSensor,
    DeviceRPMSensor,
    DeviceTemperatureSensor,
)

_LOGGER = logging.getLogger(__name__)


async def async_setup_platform(
    hass: HomeAssistant, config: Config, async_add_entities, discovery_info=None
):
    """Setup NiceHash sensor platform"""
    _LOGGER.debug("Creating new NiceHash sensor components")

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

    # Account balance sensors
    if balances_enabled:
        accounts_coordinator = data.get("accounts_coordinator")
        balance_sensors = create_balance_sensors(
            organization_id, currency, accounts_coordinator
        )
        async_add_entities(balance_sensors, True)

    # Payout sensors
    if payouts_enabled:
        _LOGGER.debug("Payout sensors enabled")
        payouts_coordinator = data.get("payouts_coordinator")
        payout_sensors = create_payout_sensors(organization_id, payouts_coordinator)
        async_add_entities(payout_sensors)

    # Mining rig and device sensors
    if rigs_enabled or devices_enabled:
        rigs_coordinator = data.get("rigs_coordinator")
        rig_data = await client.get_mining_rigs()
        mining_rigs = rig_data.get("miningRigs")
        _LOGGER.debug(f"Found {len(mining_rigs)} rigs")

        if rigs_enabled:
            _LOGGER.debug("Rig sensors enabled")
            rig_sensors = create_rig_sensors(mining_rigs, rigs_coordinator)
            async_add_entities(rig_sensors, True)

        if devices_enabled:
            _LOGGER.debug("Device sensors enabled")
            device_sensors = create_device_sensors(mining_rigs, rigs_coordinator)
            async_add_entities(device_sensors, True)


def create_balance_sensors(organization_id, currency, coordinator):
    _LOGGER.debug(f"Creating BTC account balance sensors")
    balance_sensors = [
        BalanceSensor(
            coordinator,
            organization_id,
            currency=CURRENCY_BTC,
            balance_type=BALANCE_TYPE_AVAILABLE,
        ),
        BalanceSensor(
            coordinator,
            organization_id,
            currency=CURRENCY_BTC,
            balance_type=BALANCE_TYPE_PENDING,
        ),
        BalanceSensor(
            coordinator,
            organization_id,
            currency=CURRENCY_BTC,
            balance_type=BALANCE_TYPE_TOTAL,
        ),
    ]
    if currency == CURRENCY_USD or currency == CURRENCY_EUR:
        _LOGGER.debug(f"Creating {currency} account balance sensors")
        balance_sensors.append(
            BalanceSensor(
                coordinator,
                organization_id,
                currency=currency,
                balance_type=BALANCE_TYPE_AVAILABLE,
            )
        )
        balance_sensors.append(
            BalanceSensor(
                coordinator,
                organization_id,
                currency=currency,
                balance_type=BALANCE_TYPE_PENDING,
            )
        )
        balance_sensors.append(
            BalanceSensor(
                coordinator,
                organization_id,
                currency=currency,
                balance_type=BALANCE_TYPE_TOTAL,
            )
        )
    else:
        _LOGGER.warn("Invalid currency: must be EUR or USD")

    return balance_sensors


def create_payout_sensors(organization_id, coordinator):
    _LOGGER.debug(f"Creating payout sensors")
    payout_sensors = []
    payout_sensors.append(RecentMiningPayoutSensor(coordinator, organization_id))

    return payout_sensors


def create_rig_sensors(mining_rigs, coordinator):
    rig_sensors = []
    for rig_data in mining_rigs:
        rig = MiningRig(rig_data)
        _LOGGER.debug(f"Creating {rig.name} ({rig.id}) sensors")
        rig_sensors.append(RigAlgorithmSensor(coordinator, rig))
        rig_sensors.append(RigHighTemperatureSensor(coordinator, rig))
        rig_sensors.append(RigLowTemperatureSensor(coordinator, rig))
        rig_sensors.append(RigProfitabilitySensor(coordinator, rig))
        rig_sensors.append(RigSpeedSensor(coordinator, rig))
        rig_sensors.append(RigStatusSensor(coordinator, rig))

    return rig_sensors


def create_device_sensors(mining_rigs, coordinator):
    device_sensors = []
    for rig_data in mining_rigs:
        rig = MiningRig(rig_data)
        devices = rig.devices.values()
        _LOGGER.debug(
            f"Found {len(devices)} device sensor(s) for {rig.name} ({rig.id})"
        )
        for device in devices:
            _LOGGER.debug(f"Creating {device.name} ({device.id}) sensors")
            device_sensors.append(DeviceAlgorithmSensor(coordinator, rig, device))
            device_sensors.append(DeviceSpeedSensor(coordinator, rig, device))
            device_sensors.append(DeviceStatusSensor(coordinator, rig, device))
            device_sensors.append(DeviceTemperatureSensor(coordinator, rig, device))
            device_sensors.append(DeviceLoadSensor(coordinator, rig, device))
            device_sensors.append(DeviceRPMSensor(coordinator, rig, device))

    return device_sensors
