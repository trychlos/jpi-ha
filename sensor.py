"""A JPI device.
Implements BATTERY entity.
"""

from __future__ import annotations

from datetime import datetime
import logging

from homeassistant.components.sensor import (
    SensorDeviceClass,
    SensorEntity,
    SensorStateClass,
)
from homeassistant.const import PERCENTAGE
from homeassistant.core import HomeAssistant
from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN
from .entity import JPIEntity

# Define a logger.
_LOGGER = logging.getLogger( __name__ )


async def async_setup_entry( hass: HomeAssistant, entry: JPIConfigEntry, async_add_entities: AddEntitiesCallback) -> None:
    """Set up JPI sensors for a config entry."""
    coordinator = entry.runtime_data
    async_add_entities( [JPIBatterySensor( coordinator )])


class JPIBatterySensor( JPIEntity, SensorEntity ):
    """
    Representation of the BatterySensor of a JPI Device.
    The sensor object is instanciated by HA when a ConfigEntry is validated, after having instanciated a JPICoordinator.
    """
    _attr_device_class = SensorDeviceClass.BATTERY
    _attr_state_class = SensorStateClass.MEASUREMENT
    _attr_native_unit_of_measurement = PERCENTAGE

    def __init__( self, coordinator ):
        _LOGGER.debug( f"JPIBatterySensor::__init__()" )
        super().__init__( coordinator )
        SensorEntity.__init__( self )
        self._status = {
            "level": 0,
            "last_seen": 0,
            "charging": False,
            "power": False,
            "errors": 0
        }
        coordinator._battery_sensor = self

        # Entity display name – because _attr_has_entity_name=True,
        # this will be shown as "<Device Name>: Battery" in the UI
        # Use i18n hook.
        _attr_translation_key = "battery"

        # Unique id for THIS entity (must be unique per entity)
        self._attr_unique_id = f"{self._config.id()}_battery"
        # end the end
        _LOGGER.debug( f"'{self._config.name()}' battery sensor initialized" )

    @property
    def native_value( self ):
        data = self._coordinator.data or {}
        return data.get( 'level', 0 )

    @property
    def extra_state_attributes(self):
        """Return the state attributes."""
        data = self._coordinator.data or {}
        return {
            'last_seen': data.get( 'last_seen', 0 ),
            'charging': data.get( 'charging', False ),
            'power': data.get( 'power', False ),
            'errors': data.get( 'errors', False )
        }

    @property
    def device_info( self ) -> DeviceInfo:
        """Tell HA which device this entity belongs to."""
        device_info = self._coordinator.device_info()
        return DeviceInfo(
            identifiers={( DOMAIN, self._config.id())},    # creates the device
            name=self._config.name(),                      # device name in UI
            manufacturer=device_info.manufacturer(),
            model=device_info.model()
            #configuration_url=self._url,                # optional: clickable link
            # via_device=(DOMAIN, "your_hub_id"),       # only if this device is behind a hub
        )

    async def _async_update_data( self ):
        url = self._config.url()
        jpi = self.hass.data[DOMAIN]['jpi']
        # get battery informations
        result = await jpi.battInfo( url )
        if result:
            self._status = result
            self._status['errors'] = 0
            self._status['last_seen'] = datetime.now()
        else:
            self._status['errors'] += 1
            _LOGGER.warning( f"_async_update_data errors={self._status['errors']}" )
        _LOGGER.debug( f"_async_update_data config.name() result={self._status}" )
        return self._status

