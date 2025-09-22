"""The base JPI entity"""

from __future__ import annotations

import logging

from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .coordinator import JPICoordinator

# Define a logger.
_LOGGER = logging.getLogger( __name__ )

class JPIEntity( CoordinatorEntity[JPICoordinator] ):
    """The base entity of JPI integration"""

    _attr_has_entity_name = True
    _attr_should_poll = False

    def __init__( self, coordinator: JPICoordinator ) -> None:
        _LOGGER.debug( f"JPIEntity::__init__()" )
        super().__init__( coordinator )
        self._coordinator = coordinator
        self._config = coordinator.device_config()
