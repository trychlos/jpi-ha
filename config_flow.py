"""Config flow for the JPI integration.
data is:
  url: http://hostname.example.com:9999
  device_options:
    polling_interval: 300
"""

from __future__ import annotations

import logging
from typing import Any
import validators
import voluptuous as vol

from homeassistant.config_entries import ConfigFlow, ConfigFlowResult
from homeassistant.const import CONF_URL
from homeassistant.core import HomeAssistant
from homeassistant.data_entry_flow import section
from homeassistant.exceptions import HomeAssistantError
from homeassistant.helpers import config_validation as cv

from .const import (
    DEF_POLLING_INTERVAL,
    DOMAIN,
    JPI_CONF_DEVICE_OPTIONS, JPI_CONF_POLLING_INTERVAL,
    PLATFORMS
)
from .device_config import JPIDeviceConfig
from .device_info import JPIDeviceInfo

# Define a logger.
_LOGGER = logging.getLogger( __name__ )

def get_schema( step_id: str, conf: JPIDeviceConfig = None ):
    """Compute the schema for the given step.
    Rationale: when reconfiguring, URL is not modifiable.
    conf MUST be porovided in 'reconfigure' case.
    """
    if step_id == 'user':
        base = vol.Schema({
            vol.Required( CONF_URL ): str,
        })
        collapsed = True
        default_polling = DEF_POLLING_INTERVAL
    else:
        base = vol.Schema({})
        collapsed = False
        default_polling = conf.get( JPI_CONF_DEVICE_OPTIONS, {} ).get( JPI_CONF_POLLING_INTERVAL, DEF_POLLING_INTERVAL )

    # section() is presentation only; it groups the inner fields in the UI.
    # Placing it under a key stores the inner data under that key.
    return base.extend({
        vol.Required( JPI_CONF_DEVICE_OPTIONS ): section(
            vol.Schema({
                vol.Optional( JPI_CONF_POLLING_INTERVAL, default=default_polling ): cv.positive_int
            }),
            { "collapsed": collapsed }
        )
    })

async def validate_user_input( hass: HomeAssistant, data: dict[str, Any]) -> bool:
    """
    Validate the user input at first configuration of a new entry.
    The bronze quality scale requires that the connection be tested (and validated) during user step of ConfigFlow.
    So tries to fetch here the device informations.
    """
    _LOGGER.debug( f"validate_input() data:{data}" )
    errors: dict[str, str] = {}

    url = data.get( CONF_URL )
    if not url or not bool( validators.url( url )):
        errors["base"] = "invalid_url"

    if not errors:
        conf = JPIDeviceConfig( data )
        info = JPIDeviceInfo()
        ok = await info.fetch_device_info( hass, conf )
        if not ok:
            errors["base"] = "device_info"

    return errors

class JpiConfigFlow( ConfigFlow, domain=DOMAIN ):
    """Handle a config flow for JPI.
    user_input:
        url: <url>
        device_options:
            polling_interval: <interval>
    """

    VERSION = 1

    async def async_step_user( self, user_input: dict[str, Any] | None = None ) -> ConfigFlowResult:
        """Handle the initial step."""
        errors: dict[str, str] = {}
        step_id = "user"
        schema = get_schema( step_id )

        if user_input is not None:
            errors = await validate_user_input( self.hass, user_input )
            if errors:
                return self.async_show_form( step_id=step_id, data_schema=schema, errors=errors )
            # Success path.
            conf = JPIDeviceConfig( user_input )
            # Make sure we do not have already configured this entity.
            await self.async_set_unique_id( conf.id())
            self._abort_if_unique_id_configured()
            # And create the entry.
            return self.async_create_entry( title=conf.name(), data=user_input )

        if user_input is None:
            return self.async_show_form( step_id=step_id, data_schema=schema, errors=errors )

    async def async_step_reconfigure( self, user_input: dict[str, Any] | None = None ) -> ConfigFlowResult:
        """Handle the reconfigure step."""
        errors: dict[str, str] = {}
        entry = self._get_reconfigure_entry()
        if user_input is not None:
            # TODO: maybe could we just update the poll interval directly into the coordinator instead of reinstanciating all the stuff..
            _LOGGER.debug( f"async_step_reconfigure() user_input:{user_input}" )
            return self.async_update_reload_and_abort( entry, data_updates=user_input )

        step_id = "reconfigure"
        conf = JPIDeviceConfig( entry )
        schema = get_schema( step_id, conf )
        return self.async_show_form( step_id=step_id, data_schema=schema, errors=errors, description_placeholders={ CONF_URL: conf.url()})
