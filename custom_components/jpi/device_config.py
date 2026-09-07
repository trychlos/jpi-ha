"""Configuration for a JPI device."""

from collections.abc import Mapping
import logging
from typing import Any, cast
from urllib.parse import urlparse

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_URL

from .const import JPI_CONF_LEGACY_IDENTIFIER

# Define a logger.
_LOGGER = logging.getLogger(__name__)


class JPIDeviceConfig:
    """Represent configuration supplied by a config entry or config flow."""

    def __init__(self, entry: ConfigEntry | Mapping[str, Any]) -> None:
        """Initialize the device configuration."""
        _LOGGER.debug("JPIDeviceConfig::__init__()")
        self._entry: Mapping[str, Any]
        self._entry_id: str | None = None
        # if the provide entry is really a JPIConfigEntry
        if isinstance(entry, ConfigEntry):
            _LOGGER.debug("JPIConfigEntry: %s", entry.data)
            self._entry = entry.data
            self._entry_id = entry.entry_id
        # if the provided 'entry' is actually a user input from ConfigFlow
        # but the url is missing from user_input when reconfiguring
        # so only use in 'user' case on first configuration
        elif isinstance(entry, Mapping):
            for k, v in entry.items():
                _LOGGER.debug("user_input: key=%s, value=%s", k, v)
            self._entry = entry
        else:
            for k, v in entry.items():
                _LOGGER.debug("user_input: key=%s, value=%s", k, v)
            raise TypeError(f"Unsupported type: {type(entry)!r}")

    def _data(self) -> Mapping[str, Any]:
        """Get the data from the entry."""
        return self._entry

    def get(self, key: str, default: Any) -> Any:
        """Return the configuration value associated with the key."""
        return self._data().get(key, default)

    def id(self) -> str:
        """Return the stable internal identifier for this device."""
        return cast(
            str,
            self.get(JPI_CONF_LEGACY_IDENTIFIER, self._entry_id or self.name()),
        )

    def endpoint_id(self) -> str:
        """Return the normalized endpoint used for duplicate detection."""
        parsed = urlparse(self.url())
        assert parsed.hostname is not None
        host = parsed.hostname.lower().rstrip(".")
        port = parsed.port
        if port is None:
            port = 443 if parsed.scheme.lower() == "https" else 80
        if ":" in host:
            host = f"[{host}]"
        return f"{host}:{port}"

    def name(self) -> str:
        """Compute the (unique) name from the URL."""
        url = self.url()
        parsed = urlparse(url)
        assert parsed.hostname is not None
        host = parsed.hostname.split(".")[0]
        return host.upper()

    def url(self) -> str:
        """Return the URL got from the provided JPIConfigEntry."""
        return cast(str, self._data()[CONF_URL])
