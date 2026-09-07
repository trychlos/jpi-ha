"""Integrate Android devices running the JPI application."""

import logging

from pyjpi import jpiInit

from homeassistant.core import HomeAssistant
from homeassistant.exceptions import ConfigEntryNotReady
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from homeassistant.helpers.typing import ConfigType

from .const import DOMAIN, JPI_CONF_LEGACY_IDENTIFIER, PLATFORMS
from .coordinator import JPIConfigEntry, JPICoordinator
from .device_config import JPIDeviceConfig
from .services import async_setup_services

# Define a logger.
_LOGGER = logging.getLogger(__name__)


async def async_migrate_entry(
    hass: HomeAssistant,
    entry: JPIConfigEntry,
) -> bool:
    """Preserve identifiers assigned before config-entry version 2."""
    if entry.version == 1:
        data = {
            **entry.data,
            JPI_CONF_LEGACY_IDENTIFIER: JPIDeviceConfig(entry).name(),
        }
        hass.config_entries.async_update_entry(
            entry,
            data=data,
            version=2,
        )

    return True


async def async_setup(hass: HomeAssistant, config: ConfigType) -> bool:
    """Set up the JPI integration."""
    _LOGGER.debug("async_setup()")

    hass.data[DOMAIN] = {
        "entries": {},
        "jpi": await jpiInit(async_get_clientsession(hass)),
    }

    # Register the services.
    await async_setup_services(hass)

    # Log a message indicating that the integration is ready.
    _LOGGER.debug("integration is ready")

    # Return boolean to indicate that initialization was successful.
    return True


async def async_setup_entry(hass: HomeAssistant, entry: JPIConfigEntry) -> bool:
    """Set up JPI from a configuration entry."""
    _LOGGER.debug("async_setup_entry() entry_id=%s", entry.entry_id)

    # if entry.runtime_data is None: # AttributeError: 'ConfigEntry' object has no attribute 'runtime_data'
    # if hass.data[DOMAIN]['entries'].[entry.entry_id] is None: # KeyError: '01K5A3H0AGWKMT6YMN5T49Z3JG'

    # _LOGGER.debug( f"hass.data[DOMAIN]['entries']={hass.data[DOMAIN]['entries']}" )

    if hass.data[DOMAIN]["entries"].get(entry.entry_id, None) is None:
        coordinator = JPICoordinator(hass, entry)

        try:
            await coordinator.async_config_entry_first_refresh()
        except Exception as err:
            # Tell HA to retry this entry later (automatic backoff)
            raise ConfigEntryNotReady(f"Initial fetch failed: {err}") from err

        entry.runtime_data = coordinator
        await coordinator.compute_device_info()

        hass.data[DOMAIN]["entries"][entry.entry_id] = entry

        _LOGGER.debug("installing on_unload listener")
        entry.async_on_unload(
            entry.add_update_listener(_async_reload_entry)
        )  # picks up changed interval

    _LOGGER.debug("calling hass.config_entries.async_forward_entry_setups()")
    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)

    return True


async def _async_reload_entry(hass: HomeAssistant, entry: JPIConfigEntry) -> None:
    _LOGGER.debug("async_reload_entry() entry_id=%s", entry.entry_id)
    await hass.config_entries.async_reload(entry.entry_id)


async def async_remove_entry(hass: HomeAssistant, entry: JPIConfigEntry) -> None:
    """Remove a configured entry."""
    unload_ok = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
    if unload_ok:
        hass.data[DOMAIN]["entries"].pop(entry.entry_id, None)
        del entry.runtime_data
        _LOGGER.debug("async_remove_entry() entry_id=%s", entry.entry_id)


async def async_unload_entry(hass: HomeAssistant, entry: JPIConfigEntry) -> bool:
    """Unload a configured entry."""
    unload_ok = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
    if unload_ok:
        hass.data[DOMAIN]["entries"].pop(entry.entry_id, None)
        del entry.runtime_data
        _LOGGER.debug("async_unload_entry() entry_id=%s", entry.entry_id)
    return unload_ok
