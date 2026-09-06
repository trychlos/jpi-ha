"""The configuration of the JPI device, based on a JPIConfigEntry"""

from __future__ import annotations

import logging
from typing import Any
from urllib.parse import urlparse

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_URL

# Define a logger.
_LOGGER = logging.getLogger( __name__ )

class JPIDeviceConfig:
    """
    The configuration of the JPI device, based on a JPIConfigEntry.
    Instanciation can be called with:
    - user_input from ConfigFlow (so a 'dict')
    - or an ConfigEntry instance
    """

    def __init__(self, entry: ConfigEntry | dict[str, Any]):
        _LOGGER.debug( f"JPIDeviceConfig::__init__()" )
        self._entry = None
        # if the provide entry is really a JPIConfigEntry
        if isinstance( entry, ConfigEntry ):
            _LOGGER.debug( f"JPIConfigEntry: {entry.data}" )
            self._entry = entry.data
        # if the provided 'entry' is actually a user input from ConfigFlow
        # but the url is missing from user_input when reconfiguring
        # so only use in 'user' case on first configuration
        elif isinstance( entry, dict ):
            for k,v in entry.items():
                _LOGGER.debug( f"user_input: key={k}, value={v}" )
            self._entry = entry
        else:
            for k,v in entry.items():
                _LOGGER.debug( f"user_input: key={k}, value={v}" )
            raise TypeError( f"Unsupported type: {type( entry )!r}" )

    def _data( self ):
        """Get the data from the entry."""
        return self._entry

    def get( self, key, default ):
        """Return the configuration value associated with the key."""
        return self._data().get( key, default )

    def id( self ):
        """Compute the (unique) ID attributed to this JPIConfigEntry."""
        return self.name()

    def name( self ):
        """Compute the (unique) name from the URL."""
        url = self.url()
        parsed = urlparse( url )
        host = parsed.hostname.split('.')[0]
        return host.upper()

    def url( self ):
        """Return the URL got from the provided JPIConfigEntry."""
        return self._data().get( CONF_URL, None )
