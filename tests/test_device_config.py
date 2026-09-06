"""Test JPI device configuration."""

from homeassistant.components.jpi.const import (
    JPI_CONF_DEVICE_OPTIONS,
    JPI_CONF_POLLING_INTERVAL,
)
from homeassistant.components.jpi.device_config import JPIDeviceConfig

from tests.common import MockConfigEntry

from .const import POLLING_INTERVAL, URL


def test_device_config_from_dict() -> None:
    """Test configuration constructed from config-flow data."""
    data = {
        "url": URL,
        JPI_CONF_DEVICE_OPTIONS: {
            JPI_CONF_POLLING_INTERVAL: POLLING_INTERVAL,
        },
    }

    config = JPIDeviceConfig(data)

    assert config.url() == URL
    assert config.name() == "PHONE"
    assert config.id() == "PHONE"
    assert (
        config.get(JPI_CONF_DEVICE_OPTIONS, {})[JPI_CONF_POLLING_INTERVAL]
        == POLLING_INTERVAL
    )


def test_device_config_from_entry(mock_config_entry: MockConfigEntry) -> None:
    """Test configuration constructed from a config entry."""
    config = JPIDeviceConfig(mock_config_entry)

    assert config.url() == URL
    assert config.name() == "PHONE"
    assert config.id() == "PHONE"
