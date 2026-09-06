"""Test JPI integration initialization and migration."""

from unittest.mock import AsyncMock, patch

from homeassistant.components.jpi import async_migrate_entry
from homeassistant.components.jpi.const import DOMAIN, JPI_CONF_LEGACY_IDENTIFIER
from homeassistant.config_entries import ConfigEntryState
from homeassistant.const import STATE_UNAVAILABLE
from homeassistant.core import HomeAssistant

from tests.common import MockConfigEntry


async def test_migrate_legacy_entry(
    hass: HomeAssistant,
    mock_config_entry: MockConfigEntry,
) -> None:
    """Test migration preserves the legacy identifier and UI title."""
    original_title = mock_config_entry.title
    original_unique_id = mock_config_entry.unique_id
    mock_config_entry.add_to_hass(hass)

    assert mock_config_entry.version == 1
    assert await async_migrate_entry(hass, mock_config_entry)

    assert mock_config_entry.version == 2
    assert mock_config_entry.data[JPI_CONF_LEGACY_IDENTIFIER] == "PHONE"
    assert mock_config_entry.title == original_title
    assert mock_config_entry.unique_id == original_unique_id


async def test_setup_entry(
    hass: HomeAssistant,
    mock_jpi: AsyncMock,
    init_integration: MockConfigEntry,
) -> None:
    """Test successful config-entry setup."""
    entry = init_integration

    assert entry.state is ConfigEntryState.LOADED
    assert entry.runtime_data is not None
    assert hass.data[DOMAIN]["entries"][entry.entry_id] is entry
    mock_jpi.battInfo.assert_awaited_once()
    mock_jpi.getDeviceName.assert_awaited_once()


async def test_setup_entry_failure(
    hass: HomeAssistant,
    mock_jpi: AsyncMock,
    mock_config_entry: MockConfigEntry,
) -> None:
    """Test an initial update failure schedules a setup retry."""
    mock_jpi.battInfo.side_effect = OSError("device unavailable")
    mock_config_entry.add_to_hass(hass)

    with patch(
        "homeassistant.components.jpi.jpiInit",
        return_value=mock_jpi,
    ):
        await hass.config_entries.async_setup(mock_config_entry.entry_id)

    assert mock_config_entry.state is ConfigEntryState.SETUP_RETRY


async def test_availability(
    hass: HomeAssistant,
    mock_jpi: AsyncMock,
    init_integration: MockConfigEntry,
) -> None:
    """Test an update failure marks the battery sensor unavailable."""
    state = hass.states.get("sensor.phone_battery")
    assert state is not None
    assert state.state != STATE_UNAVAILABLE

    mock_jpi.battInfo.side_effect = OSError("device unavailable")
    await init_integration.runtime_data.async_refresh()
    await hass.async_block_till_done()

    state = hass.states.get("sensor.phone_battery")
    assert state is not None
    assert state.state == STATE_UNAVAILABLE


async def test_unload_entry(
    hass: HomeAssistant,
    init_integration: MockConfigEntry,
) -> None:
    """Test unloading a config entry cleans up its runtime state."""
    entry = init_integration

    assert await hass.config_entries.async_unload(entry.entry_id)
    await hass.async_block_till_done()

    assert entry.state is ConfigEntryState.NOT_LOADED
    assert not hasattr(entry, "runtime_data")
    assert entry.entry_id not in hass.data[DOMAIN]["entries"]
