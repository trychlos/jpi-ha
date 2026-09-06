"""Services for JPI integration."""

import logging

from homeassistant.core import HomeAssistant, callback

# Define a logger.
_LOGGER = logging.getLogger(__name__)


@callback
async def async_setup_services(hass: HomeAssistant) -> None:
    """Set up services for JPI integration."""

    # hass.services.async_register(
    #    DOMAIN,
    #    SERVICE_SET_GUEST_WIFI_PW,
    #    _async_set_guest_wifi_password,
    #    SERVICE_SCHEMA_SET_GUEST_WIFI_PW,
    # )
