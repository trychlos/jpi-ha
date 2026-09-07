"""Base JPI entity."""

import logging

from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .coordinator import JPICoordinator

# Define a logger.
_LOGGER = logging.getLogger(__name__)


class JPIEntity(CoordinatorEntity[JPICoordinator]):
    """Base entity for the JPI integration."""

    _attr_has_entity_name = True
    _attr_should_poll = False

    def __init__(self, coordinator: JPICoordinator) -> None:
        """Initialize the entity."""
        _LOGGER.debug("JPIEntity::__init__()")
        super().__init__(coordinator)
        self._coordinator = coordinator
        self._config = coordinator.device_config()
