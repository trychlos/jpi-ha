"""Test the JPI battery sensor."""

from datetime import datetime
from unittest.mock import AsyncMock

from homeassistant.components.jpi.const import DOMAIN
from homeassistant.components.jpi.coordinator import JPICoordinator
from homeassistant.components.jpi.sensor import JPIBatterySensor
from homeassistant.core import HomeAssistant
from homeassistant.util import dt as dt_util

from tests.common import MockConfigEntry

from .const import BATTERY_INFO


def test_sensor_uses_coordinator_data(
    hass: HomeAssistant,
    mock_jpi: AsyncMock,
    mock_config_entry: MockConfigEntry,
) -> None:
    """Test the sensor exposes data supplied by its coordinator."""
    hass.data[DOMAIN] = {"jpi": mock_jpi}
    coordinator = JPICoordinator(hass, mock_config_entry)
    last_seen = dt_util.now()
    coordinator.data = {**BATTERY_INFO, "last_seen": last_seen}

    sensor = JPIBatterySensor(coordinator)

    assert sensor.native_value == 87
    assert sensor.extra_state_attributes == {
        "last_seen": last_seen,
        "charging": True,
        "power": False,
    }
    assert isinstance(
        sensor.extra_state_attributes["last_seen"],
        datetime,
    )
