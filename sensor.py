from __future__ import annotations

from datetime import datetime, timedelta, timezone

from homeassistant.components.sensor import SensorEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity import EntityCategory

from .const import DOMAIN


async def async_setup_entry(
    hass: HomeAssistant, entry: ConfigEntry, async_add_entities
) -> None:
    """Set up dummy forecast sensor."""
    async_add_entities(
        [OpenMeteoPVForecastSensor(entry.entry_id)], update_before_add=True
    )


class OpenMeteoPVForecastSensor(SensorEntity):
    """Dummy sensor showing 48-hour dummy forecast values."""

    _attr_has_entity_name = True
    _attr_name = "Open-Meteo PV Forecast"
    _attr_unique_id = "open_meteo_pv_forecast_main"
    _attr_native_unit_of_measurement = "kW"
    _attr_entity_category = EntityCategory.DIAGNOSTIC
    _attr_state_class = "measurement"

    def __init__(self, entry_id: str) -> None:
        self._attr_extra_state_attributes = {}
        self._entry_id = entry_id

    def update(self) -> None:
        now = datetime.now(timezone.utc)
        self._attr_native_value = 0.0

        forecast = {}
        for i in range(48):
            dt = now + timedelta(hours=i)
            hour = dt.hour
            # Simple bell curve simulation
            value = max(0, 10 * (1 - ((hour - 12) / 6) ** 2))
            forecast[dt.isoformat()] = round(value, 2)

        self._attr_extra_state_attributes = forecast
