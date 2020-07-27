"""
NiceHash Rig Payout Sensors
"""
from datetime import datetime
import logging

from homeassistant.const import ATTR_ATTRIBUTION
from homeassistant.helpers.entity import Entity

from .const import (
    CURRENCY_BTC,
    DEFAULT_NAME,
    FORMAT_DATETIME,
    ICON_CURRENCY_BTC,
    ICON_PULSE,
    ICON_THERMOMETER,
    NICEHASH_ATTRIBUTION,
    PAYOUT_USER,
)
from .coordinators import (
    MiningPayoutsDataUpdateCoordinator,
    MiningRigsDataUpdateCoordinator,
)
from .nicehash import MiningRig, Payout

_LOGGER = logging.getLogger(__name__)


class RecentMiningPayoutSensor(Entity):
    """
    Displays most recent mining payout
    """

    def __init__(
        self, coordinator: MiningPayoutsDataUpdateCoordinator, organization_id: str
    ):
        """Initialize the sensor"""
        self.coordinator = coordinator
        self.organization_id = organization_id
        self._id = None
        self._created = None
        self._currency = None
        self._amount = 0.00
        self._fee = 0.00

    @property
    def name(self):
        """Sensor name"""
        return f"{DEFAULT_NAME} Recent Mining Payout"

    @property
    def unique_id(self):
        """Unique entity id"""
        return f"{self.organization_id}:payouts:recent"

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
        try:
            for raw_payout in self.coordinator.data:
                payout = Payout(raw_payout)
                if payout.account_type == PAYOUT_USER:
                    self._id = payout.id
                    self._amount = payout.amount
                    self._currency = payout.currency
                    self._created = datetime.fromtimestamp(payout.created / 1000.0)
                    self._fee = payout.fee
        except Exception as e:
            _LOGGER.error(f"Unable to get most recent \n{e}")
            self._id = None
            self._created = None
            self._currency = None
            self._amount = 0.00
            self._fee = 0.00

        return self._amount - self._fee

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
        created = None
        if self._created:
            created = self._created.strftime(FORMAT_DATETIME)
        return {
            ATTR_ATTRIBUTION: NICEHASH_ATTRIBUTION,
            "amount": self._amount,
            "created": created,
            "fee": self._fee,
        }

    async def async_added_to_hass(self):
        """Connect to dispatcher listening for entity data notifications"""
        self.async_on_remove(
            self.coordinator.async_add_listener(self.async_write_ha_state)
        )

    async def async_update(self):
        """Update entity"""
        await self.coordinator.async_request_refresh()
