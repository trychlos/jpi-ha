"""JPI Coordinator."""

from datetime import datetime, timedelta
import logging
from typing import override

from pyjpi import BatteryInfo

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed
from homeassistant.util import dt as dt_util

from .const import (
    DEF_POLLING_INTERVAL,
    DOMAIN,
    JPI_CONF_DEVICE_OPTIONS,
    JPI_CONF_POLLING_INTERVAL,
)
from .device_config import JPIDeviceConfig
from .device_info import JPIDeviceInfo

# Define a logger.
_LOGGER = logging.getLogger(__name__)

# A JPI config entry stores its coordinator as runtime data.
type JPIConfigEntry = ConfigEntry[JPICoordinator]


class JPICoordinatorData(BatteryInfo):
    """Data returned by the JPI coordinator."""

    last_seen: datetime


class JPICoordinator(DataUpdateCoordinator[JPICoordinatorData]):
    """Coordinate JPI device updates."""

    def __init__(self, hass: HomeAssistant, entry: JPIConfigEntry) -> None:
        """Initialize the coordinator."""
        _LOGGER.debug("JPICoordinator::__init__()")
        conf = JPIDeviceConfig(entry)
        interval = timedelta(
            seconds=conf.get(JPI_CONF_DEVICE_OPTIONS, {}).get(
                JPI_CONF_POLLING_INTERVAL, DEF_POLLING_INTERVAL
            )
        )
        super().__init__(
            hass,
            _LOGGER,
            config_entry=entry,
            name=f"{DOMAIN} {conf.url()}",
            update_interval=interval,
        )

        self._entry = entry
        self._device_config = conf
        self._device_info: JPIDeviceInfo | None = None

    @override
    async def _async_update_data(self) -> JPICoordinatorData:
        """Fetch new state data for the sensors."""
        try:
            result = await self.hass.data[DOMAIN]["jpi"].battInfo(
                self._device_config.url()
            )
        except Exception as err:
            raise UpdateFailed(f"Unable to fetch battery information: {err}") from err

        if not result:
            raise UpdateFailed("Unable to fetch battery information")

        return JPICoordinatorData(**result, last_seen=dt_util.now())

    async def compute_device_info(self) -> None:
        """Instanciate a JPIDeviceInfo object which provides manufacturer and model names."""
        self._device_info = JPIDeviceInfo()
        await self._device_info.fetch_device_info(self.hass, self._device_config)

    def device_config(self) -> JPIDeviceConfig:
        """Return the device configuration."""
        return self._device_config

    def device_info(self) -> JPIDeviceInfo:
        """Return information about the device."""
        assert self._device_info is not None
        return self._device_info
