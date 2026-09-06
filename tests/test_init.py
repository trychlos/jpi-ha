"""Test JPI integration initialization and migration."""

from homeassistant.components.jpi import async_migrate_entry
from homeassistant.components.jpi.const import JPI_CONF_LEGACY_IDENTIFIER
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
