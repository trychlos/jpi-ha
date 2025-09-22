"""JPI Coordinator."""

from __future__ import annotations

import async_timeout
from datetime import timedelta
import logging

from homeassistant.components.sensor import SensorEntity
from homeassistant.core import HomeAssistant
from homeassistant.helpers import entity_registry as er
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .const import DEF_POLLING_INTERVAL, DOMAIN, JPI_CONF_DEVICE_OPTIONS, JPI_CONF_POLLING_INTERVAL
from .device_config import JPIDeviceConfig
from .device_info import JPIDeviceInfo

# Define a logger.
_LOGGER = logging.getLogger( __name__ )

# Create ConfigEntry type alias with runtime data object.
# This tells the type checker: “when I say JPIConfigEntry, I mean a ConfigEntry whose runtime_data is of type JPIRuntimeData."
type JPIConfigEntry = ConfigEntry[JPICoordinator]  # noqa: F821


class JPICoordinator( DataUpdateCoordinator[dict] ):

    def __init__( self, hass: HomeAssistant, entry: JPIConfigEntry ):
        _LOGGER.debug( f"JPICoordinator::__init__()" )
        conf = JPIDeviceConfig( entry )
        interval = timedelta( seconds=conf.get( JPI_CONF_DEVICE_OPTIONS, {} ).get( JPI_CONF_POLLING_INTERVAL, DEF_POLLING_INTERVAL ))
        super().__init__( hass, _LOGGER, name=f"{DOMAIN} {conf.url()}", update_interval=interval )

        self._entry = entry
        self._device_config = conf
        self._device_info = None
        self._battery_sensor = None

    #def _get_sensor_entity_ids_for_entry( self, entry_id: str) -> list[str]:
    #    reg = er.async_get( self.hass )
    #    entries = er.async_entries_for_config_entry( reg, entry_id )
    #    return [e.entity_id for e in entries if e.domain == "sensor"]

    async def _async_update_data( self ):
        """Fetch new state data for the sensors."""
        if self._battery_sensor is not None:
            return await self._battery_sensor._async_update_data()

    async def compute_device_info( self ):
        """Instanciate a JPIDeviceInfo object which provides manufacturer and model names."""
        self._device_info = JPIDeviceInfo()
        await self._device_info.fetch_device_info( self.hass, self._device_config )

    def device_config( self ):
        return self._device_config

    def device_info( self ):
        return self._device_info
