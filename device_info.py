"""The JPI Device Informations, aka Manufacturer Model"""

from __future__ import annotations

import logging

from pyjpi import JPIError

from homeassistant.core import HomeAssistant

from .const import DOMAIN
from .device_config import JPIDeviceConfig

# Define a logger.
_LOGGER = logging.getLogger( __name__ )

class JPIDeviceInfo:
    """A class dedicated to get device informations"""

    def __init__( self ):
        self._manufacturer = None
        self._model = None

    async def fetch_device_info( self, hass: HomeAssistant, config: JPIDeviceConfig ):
        url = config.url()
        jpi = hass.data[DOMAIN]['jpi']
        try:
            resp = await jpi.getDeviceName(url)
        except JPIError:
            _LOGGER.debug("Unable to fetch JPI device information", exc_info=True)
            return False
        ok = False
        if resp:
            manufacturer, model = resp.split( ' ', 1 )
            self._manufacturer = manufacturer
            self._model = model
            ok = True
        return ok

    def manufacturer( self ):
        return self._manufacturer
    
    def model( self ):
        return self._model
