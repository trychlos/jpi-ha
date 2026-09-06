"""Test JPI device information retrieval."""

from unittest.mock import AsyncMock

from pyjpi import JPIConnectionError

from homeassistant.components.jpi.const import DOMAIN
from homeassistant.components.jpi.device_config import JPIDeviceConfig
from homeassistant.components.jpi.device_info import JPIDeviceInfo
from homeassistant.core import HomeAssistant

from .const import URL


async def test_fetch_device_info_success(
    hass: HomeAssistant,
    mock_jpi: AsyncMock,
) -> None:
    """Test parsing manufacturer and model from the device response."""
    hass.data[DOMAIN] = {"jpi": mock_jpi}
    info = JPIDeviceInfo()

    result = await info.fetch_device_info(
        hass,
        JPIDeviceConfig({"url": URL}),
    )

    assert result is True
    assert info.manufacturer() == "Samsung"
    assert info.model() == "SM-J320FN"
    mock_jpi.getDeviceName.assert_awaited_once_with(URL)


async def test_fetch_device_info_unavailable(
    hass: HomeAssistant,
    mock_jpi: AsyncMock,
) -> None:
    """Test an empty response from the device."""
    hass.data[DOMAIN] = {"jpi": mock_jpi}
    mock_jpi.getDeviceName.return_value = None
    info = JPIDeviceInfo()

    result = await info.fetch_device_info(
        hass,
        JPIDeviceConfig({"url": URL}),
    )

    assert result is False
    assert info.manufacturer() is None
    assert info.model() is None


async def test_fetch_device_info_connection_error(
    hass: HomeAssistant,
    mock_jpi: AsyncMock,
) -> None:
    """Test a pyJPI connection error is handled."""
    hass.data[DOMAIN] = {"jpi": mock_jpi}
    mock_jpi.getDeviceName.side_effect = JPIConnectionError
    info = JPIDeviceInfo()

    result = await info.fetch_device_info(
        hass,
        JPIDeviceConfig({"url": URL}),
    )

    assert result is False
    assert info.manufacturer() is None
    assert info.model() is None


async def test_fetch_device_info_invalid_name(
    hass: HomeAssistant,
    mock_jpi: AsyncMock,
) -> None:
    """Test a device name without a manufacturer/model separator."""
    hass.data[DOMAIN] = {"jpi": mock_jpi}
    mock_jpi.getDeviceName.return_value = "Unknown"
    info = JPIDeviceInfo()

    result = await info.fetch_device_info(
        hass,
        JPIDeviceConfig({"url": URL}),
    )

    assert result is False
    assert info.manufacturer() is None
    assert info.model() is None
