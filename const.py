"""Constants for the JPI integration."""

from __future__ import annotations

from typing import Final

from homeassistant.const import Platform

DOMAIN: Final = "jpi"

JPI_CONF_DEVICE_OPTIONS = "device_options"
JPI_CONF_BATTERY_OPTIONS = "battery_options"
JPI_CONF_HIGH_THRESHOLD = "high_threshold"
JPI_CONF_LOW_THRESHOLD = "low_threshold"
JPI_CONF_POLLING_INTERVAL = "polling_interval"

DEF_HIGH_THRESHOLD: Final = 95
DEF_LOW_THRESHOLD: Final = 15
DEF_POLLING_INTERVAL: Final = 300 # 5 min
DEF_PORT: Final = 8080

PLATFORMS: list[Platform] = [Platform.SENSOR]
