"""Information about a JPI device."""

import logging

from pyjpi import JPIError

from homeassistant.core import HomeAssistant

from .const import DOMAIN
from .device_config import JPIDeviceConfig

# Define a logger.
_LOGGER = logging.getLogger(__name__)


class JPIDeviceInfo:
    """Fetch and expose JPI device information."""

    def __init__(self) -> None:
        """Initialize empty device information."""
        self._manufacturer: str | None = None
        self._model: str | None = None

    async def fetch_device_info(
        self, hass: HomeAssistant, config: JPIDeviceConfig
    ) -> bool:
        """Fetch manufacturer and model information."""
        url = config.url()
        jpi = hass.data[DOMAIN]["jpi"]
        try:
            resp = await jpi.getDeviceName(url)
        except JPIError:
            _LOGGER.debug("Unable to fetch JPI device information", exc_info=True)
            return False
        ok = False
        if resp:
            manufacturer, separator, model = resp.partition(" ")
            manufacturer = manufacturer.strip()
            model = model.strip()
            if not separator or not manufacturer or not model:
                _LOGGER.debug("Invalid JPI device name: %s", resp)
                return False
            self._manufacturer = manufacturer
            self._model = model
            ok = True
        return ok

    def manufacturer(self) -> str | None:
        """Return the device manufacturer."""
        return self._manufacturer

    def model(self) -> str | None:
        """Return the device model."""
        return self._model
