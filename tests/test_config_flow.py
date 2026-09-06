"""Test the JPI configuration flow."""

from unittest.mock import AsyncMock

import pytest

from homeassistant import config_entries
from homeassistant.components.jpi.const import (
    DOMAIN,
    JPI_CONF_DEVICE_OPTIONS,
    JPI_CONF_POLLING_INTERVAL,
)
from homeassistant.const import CONF_URL
from homeassistant.core import HomeAssistant
from homeassistant.data_entry_flow import FlowResultType

from tests.common import MockConfigEntry

from .const import POLLING_INTERVAL, URL

pytestmark = pytest.mark.usefixtures("mock_setup_entry")


def enable_jpi(hass: HomeAssistant, mock_jpi: AsyncMock) -> None:
    """Make the mocked library available to the config flow."""
    hass.data[DOMAIN] = {
        "entries": {},
        "jpi": mock_jpi,
    }


async def test_user_flow_success(
    hass: HomeAssistant,
    mock_jpi: AsyncMock,
    mock_setup_entry: AsyncMock,
) -> None:
    """Test successful user configuration."""
    enable_jpi(hass, mock_jpi)

    result = await hass.config_entries.flow.async_init(
        DOMAIN,
        context={"source": config_entries.SOURCE_USER},
    )

    assert result["type"] is FlowResultType.FORM
    assert not result["errors"]

    result = await hass.config_entries.flow.async_configure(
        result["flow_id"],
        {
            CONF_URL: URL,
            JPI_CONF_DEVICE_OPTIONS: {
                JPI_CONF_POLLING_INTERVAL: POLLING_INTERVAL,
            },
        },
    )
    await hass.async_block_till_done()

    assert result["type"] is FlowResultType.CREATE_ENTRY
    assert result["title"] == "PHONE"
    assert result["data"] == {
        CONF_URL: URL,
        JPI_CONF_DEVICE_OPTIONS: {
            JPI_CONF_POLLING_INTERVAL: POLLING_INTERVAL,
        },
    }
    mock_jpi.getDeviceName.assert_awaited_once_with(URL)
    mock_setup_entry.assert_awaited_once()


async def test_user_flow_invalid_url(
    hass: HomeAssistant,
    mock_jpi: AsyncMock,
) -> None:
    """Test rejection of an invalid URL."""
    enable_jpi(hass, mock_jpi)

    result = await hass.config_entries.flow.async_init(
        DOMAIN,
        context={"source": config_entries.SOURCE_USER},
    )
    result = await hass.config_entries.flow.async_configure(
        result["flow_id"],
        {
            CONF_URL: "not a URL",
            JPI_CONF_DEVICE_OPTIONS: {
                JPI_CONF_POLLING_INTERVAL: POLLING_INTERVAL,
            },
        },
    )

    assert result["type"] is FlowResultType.FORM
    assert result["errors"] == {"base": "invalid_url"}
    mock_jpi.getDeviceName.assert_not_awaited()


async def test_user_flow_device_unavailable(
    hass: HomeAssistant,
    mock_jpi: AsyncMock,
) -> None:
    """Test rejection when device information cannot be retrieved."""
    enable_jpi(hass, mock_jpi)
    mock_jpi.getDeviceName.return_value = None

    result = await hass.config_entries.flow.async_init(
        DOMAIN,
        context={"source": config_entries.SOURCE_USER},
    )
    result = await hass.config_entries.flow.async_configure(
        result["flow_id"],
        {
            CONF_URL: URL,
            JPI_CONF_DEVICE_OPTIONS: {
                JPI_CONF_POLLING_INTERVAL: POLLING_INTERVAL,
            },
        },
    )

    assert result["type"] is FlowResultType.FORM
    assert result["errors"] == {"base": "device_info"}


async def test_user_flow_aborts_duplicate(
    hass: HomeAssistant,
    mock_jpi: AsyncMock,
    mock_config_entry: MockConfigEntry,
) -> None:
    """Test rejection of a duplicate device."""
    enable_jpi(hass, mock_jpi)
    mock_config_entry.add_to_hass(hass)

    result = await hass.config_entries.flow.async_init(
        DOMAIN,
        context={"source": config_entries.SOURCE_USER},
    )
    result = await hass.config_entries.flow.async_configure(
        result["flow_id"],
        {
            CONF_URL: URL,
            JPI_CONF_DEVICE_OPTIONS: {
                JPI_CONF_POLLING_INTERVAL: POLLING_INTERVAL,
            },
        },
    )

    assert result["type"] is FlowResultType.ABORT
    assert result["reason"] == "already_configured"


async def test_reconfigure_updates_polling_interval(
    hass: HomeAssistant,
    mock_config_entry: MockConfigEntry,
) -> None:
    """Test changing the polling interval while preserving the URL."""
    mock_config_entry.add_to_hass(hass)

    result = await hass.config_entries.flow.async_init(
        DOMAIN,
        context={
            "source": config_entries.SOURCE_RECONFIGURE,
            "entry_id": mock_config_entry.entry_id,
        },
    )

    assert result["type"] is FlowResultType.FORM

    result = await hass.config_entries.flow.async_configure(
        result["flow_id"],
        {
            JPI_CONF_DEVICE_OPTIONS: {
                JPI_CONF_POLLING_INTERVAL: 60,
            },
        },
    )

    assert result["type"] is FlowResultType.ABORT
    assert result["reason"] == "reconfigure_successful"
    assert mock_config_entry.data == {
        CONF_URL: URL,
        JPI_CONF_DEVICE_OPTIONS: {
            JPI_CONF_POLLING_INTERVAL: 60,
        },
    }
