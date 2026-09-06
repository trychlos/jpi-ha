"""JPI battery sensor."""

from datetime import datetime
import logging
from typing import override

from homeassistant.components.sensor import (
    SensorDeviceClass,
    SensorEntity,
    SensorStateClass,
)
from homeassistant.const import PERCENTAGE
from homeassistant.core import HomeAssistant
from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import DOMAIN
from .coordinator import JPIConfigEntry, JPICoordinator
from .entity import JPIEntity

# Define a logger.
_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: HomeAssistant, entry: JPIConfigEntry, async_add_entities: AddEntitiesCallback
) -> None:
    """Set up JPI sensors for a config entry."""
    coordinator = entry.runtime_data
    async_add_entities([JPIBatterySensor(coordinator)])


class JPIBatterySensor(JPIEntity, SensorEntity):
    """Represent the battery of a JPI device."""

    _attr_device_class = SensorDeviceClass.BATTERY
    _attr_state_class = SensorStateClass.MEASUREMENT
    _attr_native_unit_of_measurement = PERCENTAGE

    def __init__(self, coordinator: JPICoordinator) -> None:
        """Initialize the battery sensor."""
        _LOGGER.debug("JPIBatterySensor::__init__()")
        super().__init__(coordinator)
        SensorEntity.__init__(self)

        # Entity display name because _attr_has_entity_name=True,
        # this will be shown as "<Device Name>: Battery" in the UI
        # Use i18n hook.
        _attr_translation_key = "battery"

        # Unique id for THIS entity (must be unique per entity)
        self._attr_unique_id = f"{self._config.id()}_battery"
        # end the end
        _LOGGER.debug("'%s' battery sensor initialized", self._config.name())

    @property
    @override
    def native_value(self) -> int:
        """Return the battery level."""
        if (data := self._coordinator.data) is None:
            return 0
        return data["level"]

    @property
    @override
    def extra_state_attributes(self) -> dict[str, bool | datetime | int]:
        """Return the state attributes."""
        if (data := self._coordinator.data) is None:
            return {
                "last_seen": 0,
                "charging": False,
                "power": False,
            }
        return {
            "last_seen": data["last_seen"],
            "charging": data["charging"],
            "power": data["power"],
        }

    @property
    @override
    def device_info(self) -> DeviceInfo:
        """Tell HA which device this entity belongs to."""
        device_info = self._coordinator.device_info()
        return DeviceInfo(
            identifiers={(DOMAIN, self._config.id())},  # creates the device
            name=self._config.name(),  # device name in UI
            manufacturer=device_info.manufacturer(),
            model=device_info.model(),
            # configuration_url=self._url,                # optional: clickable link
            # via_device=(DOMAIN, "your_hub_id"),       # only if this device is behind a hub
        )
