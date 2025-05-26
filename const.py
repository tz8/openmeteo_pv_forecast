"""Constants for the Open-Meteo integration."""

from __future__ import annotations

from datetime import timedelta
import logging
from typing import Final

from homeassistant.components.weather import (
    ATTR_CONDITION_CLOUDY,
    ATTR_CONDITION_FOG,
    ATTR_CONDITION_LIGHTNING,
    ATTR_CONDITION_PARTLYCLOUDY,
    ATTR_CONDITION_POURING,
    ATTR_CONDITION_RAINY,
    ATTR_CONDITION_SNOWY,
    ATTR_CONDITION_SUNNY,
)

DOMAIN: Final = "openmeteo_pv_forecast"

LOGGER = logging.getLogger(__package__)
SCAN_INTERVAL = timedelta(minutes=30)
