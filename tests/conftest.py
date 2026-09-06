"""Common fixtures for the JPI integration tests."""

from collections.abc import Generator
from unittest.mock import AsyncMock, patch

import pytest

from homeassistant.components.jpi.const import (
    DOMAIN,
    JPI_CONF_DEVICE_OPTIONS,
    JPI_CONF_POLLING_INTERVAL,
)
from homeassistant.const import CONF_URL

from tests.common import MockConfigEntry

from .const import BATTERY_INFO, DEVICE_NAME, POLLING_INTERVAL, URL


@pytest.fixture
def mock_jpi() -> AsyncMock:
    """Return a mocked pyJPI client."""
    client = AsyncMock()
    client.getDeviceName.return_value = DEVICE_NAME
    client.battInfo.return_value = BATTERY_INFO
    return client


@pytest.fixture
def mock_setup_entry() -> Generator[AsyncMock]:
    """Prevent config-flow tests from setting up the integration."""
    with patch(
        "homeassistant.components.jpi.async_setup_entry",
        return_value=True,
    ) as setup_entry:
        yield setup_entry


@pytest.fixture
def mock_config_entry() -> MockConfigEntry:
    """Return a configured JPI entry."""
    return MockConfigEntry(
        domain=DOMAIN,
        title="PHONE",
        unique_id="PHONE",
        data={
            CONF_URL: URL,
            JPI_CONF_DEVICE_OPTIONS: {
                JPI_CONF_POLLING_INTERVAL: POLLING_INTERVAL,
            },
        },
    )
