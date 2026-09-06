"""Test JPI device configuration."""

from homeassistant.components.jpi.const import (
    DOMAIN,
    JPI_CONF_DEVICE_OPTIONS,
    JPI_CONF_LEGACY_IDENTIFIER,
    JPI_CONF_POLLING_INTERVAL,
)
from homeassistant.components.jpi.device_config import JPIDeviceConfig

from .const import POLLING_INTERVAL, URL

from tests.common import MockConfigEntry


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
    assert config.id() == mock_config_entry.entry_id


def test_existing_entry_uses_legacy_identifier(
    mock_config_entry: MockConfigEntry,
) -> None:
    """Test a migrated entry keeps its original identifier."""
    data = {
        **mock_config_entry.data,
        JPI_CONF_LEGACY_IDENTIFIER: "PHONE",
    }
    legacy_entry = MockConfigEntry(
        domain=DOMAIN,
        entry_id=mock_config_entry.entry_id,
        data=data,
    )

    assert JPIDeviceConfig(legacy_entry).id() == "PHONE"


def test_normalized_endpoint() -> None:
    """Test complete host and effective port normalization."""
    assert (
        JPIDeviceConfig({"url": "HTTP://Phone.Example.Com.:8080"}).endpoint_id()
        == "phone.example.com:8080"
    )


def test_default_endpoint_ports() -> None:
    """Test default HTTP and HTTPS ports."""
    assert (
        JPIDeviceConfig({"url": "http://phone.example.com"}).endpoint_id()
        == "phone.example.com:80"
    )
    assert (
        JPIDeviceConfig({"url": "https://phone.example.com"}).endpoint_id()
        == "phone.example.com:443"
    )


def test_ipv6_endpoint() -> None:
    """Test an IPv6 endpoint."""
    assert (
        JPIDeviceConfig({"url": "http://[2001:db8::10]:8080"}).endpoint_id()
        == "[2001:db8::10]:8080"
    )
