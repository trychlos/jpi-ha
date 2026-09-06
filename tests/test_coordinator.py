"""Test the JPI data update coordinator."""

from unittest.mock import AsyncMock

import pytest

from homeassistant.components.jpi.const import DOMAIN
from homeassistant.components.jpi.coordinator import JPICoordinator
from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import UpdateFailed
from homeassistant.util import dt as dt_util

from tests.common import MockConfigEntry

from .const import BATTERY_INFO, URL


async def test_update_data_success(
    hass: HomeAssistant,
    mock_jpi: AsyncMock,
    mock_config_entry: MockConfigEntry,
) -> None:
    """Test a successful battery update."""
    hass.data[DOMAIN] = {"jpi": mock_jpi}
    coordinator = JPICoordinator(hass, mock_config_entry)
    before_update = dt_util.now()

    data = await coordinator._async_update_data()

    after_update = dt_util.now()
    assert data["level"] == BATTERY_INFO["level"]
    assert data["charging"] is BATTERY_INFO["charging"]
    assert data["power"] is BATTERY_INFO["power"]
    assert before_update <= data["last_seen"] <= after_update
    mock_jpi.battInfo.assert_awaited_once_with(URL)


async def test_update_data_empty_response(
    hass: HomeAssistant,
    mock_jpi: AsyncMock,
    mock_config_entry: MockConfigEntry,
) -> None:
    """Test an empty response is reported as an update failure."""
    hass.data[DOMAIN] = {"jpi": mock_jpi}
    mock_jpi.battInfo.return_value = None
    coordinator = JPICoordinator(hass, mock_config_entry)

    with pytest.raises(UpdateFailed, match="Unable to fetch battery information"):
        await coordinator._async_update_data()


async def test_update_data_exception(
    hass: HomeAssistant,
    mock_jpi: AsyncMock,
    mock_config_entry: MockConfigEntry,
) -> None:
    """Test a library exception is reported as an update failure."""
    hass.data[DOMAIN] = {"jpi": mock_jpi}
    mock_jpi.battInfo.side_effect = RuntimeError("device disconnected")
    coordinator = JPICoordinator(hass, mock_config_entry)

    with pytest.raises(
        UpdateFailed,
        match="Unable to fetch battery information: device disconnected",
    ):
        await coordinator._async_update_data()
