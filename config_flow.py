"""Config flow for the JPI integration."""

import logging
from typing import Any, override

import validators
import voluptuous as vol

from homeassistant.config_entries import ConfigFlow, ConfigFlowResult
from homeassistant.const import CONF_URL
from homeassistant.core import HomeAssistant
from homeassistant.data_entry_flow import section
from homeassistant.helpers import config_validation as cv

from .const import (
    DEF_POLLING_INTERVAL,
    DOMAIN,
    JPI_CONF_DEVICE_OPTIONS,
    JPI_CONF_POLLING_INTERVAL,
)
from .device_config import JPIDeviceConfig
from .device_info import JPIDeviceInfo

# Define a logger.
_LOGGER = logging.getLogger(__name__)


def get_schema(step_id: str, conf: JPIDeviceConfig | None = None) -> vol.Schema:
    """Compute the schema for the given step."""
    if step_id == "user":
        base = vol.Schema(
            {
                vol.Required(CONF_URL): str,
            }
        )
        collapsed = True
        default_polling = DEF_POLLING_INTERVAL
    else:
        assert conf is not None
        base = vol.Schema({})
        collapsed = False
        default_polling = conf.get(JPI_CONF_DEVICE_OPTIONS, {}).get(
            JPI_CONF_POLLING_INTERVAL, DEF_POLLING_INTERVAL
        )

    # section() is presentation only; it groups the inner fields in the UI.
    # Placing it under a key stores the inner data under that key.
    return base.extend(
        {
            vol.Required(JPI_CONF_DEVICE_OPTIONS): section(
                vol.Schema(
                    {
                        vol.Optional(
                            JPI_CONF_POLLING_INTERVAL, default=default_polling
                        ): cv.positive_int
                    }
                ),
                {"collapsed": collapsed},
            )
        }
    )


async def validate_user_input(
    hass: HomeAssistant, data: dict[str, Any]
) -> dict[str, str]:
    """Validate user input when configuring a new entry."""
    _LOGGER.debug("validate_input() data: %s", data)
    errors: dict[str, str] = {}

    url = data.get(CONF_URL)
    if not url or not bool(validators.url(url)):
        errors["base"] = "invalid_url"

    if not errors:
        conf = JPIDeviceConfig(data)
        info = JPIDeviceInfo()
        ok = await info.fetch_device_info(hass, conf)
        if not ok:
            errors["base"] = "device_info"

    return errors


class JpiConfigFlow(ConfigFlow, domain=DOMAIN):
    """Handle a config flow for JPI."""

    VERSION = 2

    @override
    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        """Handle the initial step."""
        errors: dict[str, str] = {}
        step_id = "user"
        schema = get_schema(step_id)

        if user_input is not None:
            errors = await validate_user_input(self.hass, user_input)
            if errors:
                return self.async_show_form(
                    step_id=step_id, data_schema=schema, errors=errors
                )
            # Success path.
            conf = JPIDeviceConfig(user_input)
            endpoint_id = conf.endpoint_id()

            # Legacy entries have hostname-based unique IDs, so compare their
            # configured endpoints explicitly as well.
            if any(
                JPIDeviceConfig(entry).endpoint_id() == endpoint_id
                for entry in self.hass.config_entries.async_entries(DOMAIN)
            ):
                return self.async_abort(reason="already_configured")

            await self.async_set_unique_id(endpoint_id)
            self._abort_if_unique_id_configured()
            # And create the entry.
            return self.async_create_entry(title=conf.name(), data=user_input)

        return self.async_show_form(step_id=step_id, data_schema=schema, errors=errors)

    async def async_step_reconfigure(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        """Handle the reconfigure step."""
        errors: dict[str, str] = {}
        entry = self._get_reconfigure_entry()
        if user_input is not None:
            _LOGGER.debug("async_step_reconfigure() user_input: %s", user_input)
            return self.async_update_and_abort(entry, data_updates=user_input)

        step_id = "reconfigure"
        conf = JPIDeviceConfig(entry)
        schema = get_schema(step_id, conf)
        return self.async_show_form(
            step_id=step_id,
            data_schema=schema,
            errors=errors,
            description_placeholders={CONF_URL: conf.url()},
        )
