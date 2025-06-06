"""Constants for Open-Meteo PV Forecast integration."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import timedelta
from typing import Final

from homeassistant.const import UnitOfLength
from homeassistant.util.unit_conversion import DistanceConverter

DOMAIN: Final = "openmeteo_pv_forecast"
CONF_VERSION: Final = "version"
STORAGE_VERSION: Final = 2

# Sensor types
SENSOR_TYPE_STRING_FORECAST: Final = "string_forecast"
SENSOR_TYPE_INVERTER_FORECAST: Final = "inverter_forecast"
SENSOR_TYPE_STRING_REMAINING: Final = "string_remaining"
SENSOR_TYPE_INVERTER_REMAINING: Final = "inverter_remaining"

# Horizon configuration
CONF_HORIZON: Final = "horizon"
DEFAULT_HORIZON: Final = [
    0,
    0,
    0,
    0,
    0,
    0,
    0,
    0,
    0,
    0,
    0,
    0,
]  # 12 values for 30° segments
HORIZON_MIN: Final = 0  # degrees
HORIZON_MAX: Final = 90  # degrees
HORIZON_STEP: Final = 0.5  # degrees

# Weather model configuration
CONF_WEATHER_MODEL: Final = "weather_model"
DEFAULT_WEATHER_MODEL: Final = "icon_d2_eps"


@dataclass
class WeatherModel:
    """Weather model configuration class."""

    id: str
    name: str
    region: str
    resolution_km: float
    resolution_hours: int  # 1 for hourly
    members: int
    forecast_length: str
    update_frequency: str
    min_poll_interval: int  # seconds
    next_update_interval: timedelta  # when to check next

    def get_resolution_string(self, to_unit: str) -> str:
        """Get resolution string in the desired unit."""
        if to_unit == UnitOfLength.KILOMETERS:
            return f"{self.resolution_km:.0f} km"
        # Convert to miles
        miles = DistanceConverter.convert(
            self.resolution_km, UnitOfLength.KILOMETERS, to_unit
        )
        return f"{miles:.0f} mi"

    def get_resolution(self, to_unit: str) -> str:
        """Get full resolution string including time interval."""
        dist = self.get_resolution_string(to_unit)
        return f"{dist}, hourly"  # All remaining models are hourly


WEATHER_MODELS: dict[str, WeatherModel] = {
    "icon_d2_eps": WeatherModel(
        id="icon_d2_eps",
        name="ICON-D2-EPS (DWD)",
        region="Central Europe",
        resolution_km=2,
        resolution_hours=1,
        members=20,
        forecast_length="2 days",
        update_frequency="3 hours",
        min_poll_interval=3600 * 3,  # 3 hours
        next_update_interval=timedelta(hours=3),
    ),
    "icon_eu_eps": WeatherModel(
        id="icon_eu_eps",
        name="ICON-EU-EPS (DWD)",
        region="Europe",
        resolution_km=13,
        resolution_hours=1,
        members=40,
        forecast_length="5 days",
        update_frequency="6 hours",
        min_poll_interval=3600 * 6,  # 6 hours
        next_update_interval=timedelta(hours=6),
    ),
    "icon_eps": WeatherModel(
        id="icon_eps",
        name="ICON-EPS (DWD)",
        region="Global",
        resolution_km=26,
        resolution_hours=1,
        members=40,
        forecast_length="7.5 days",
        update_frequency="12 hours",
        min_poll_interval=3600 * 12,  # 12 hours
        next_update_interval=timedelta(hours=12),
    ),
    "mogreps_uk": WeatherModel(
        id="mogreps_uk",
        name="MOGREPS-UK (UK Met Office)",
        region="UK",
        resolution_km=2,
        resolution_hours=1,
        members=3,
        forecast_length="5 days",
        update_frequency="1 hour",
        min_poll_interval=3600,  # 1 hour
        next_update_interval=timedelta(hours=1),
    ),
    "mogreps_g": WeatherModel(
        id="mogreps_g",
        name="MOGREPS-G (UK Met Office)",
        region="Global",
        resolution_km=20,
        resolution_hours=1,
        members=18,
        forecast_length="8 days",
        update_frequency="6 hours",
        min_poll_interval=3600 * 6,  # 6 hours
        next_update_interval=timedelta(hours=6),
    ),
}
