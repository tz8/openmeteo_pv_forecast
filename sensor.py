"""Sensor platform for Open-Meteo PV Forecast integration."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import UTC, datetime, timedelta
from typing import Any

from homeassistant.components.sensor import (
    SensorDeviceClass,
    SensorEntity,
    SensorEntityDescription,
    SensorStateClass,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import UnitOfEnergy, UnitOfPower
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity import EntityCategory
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import (
    DOMAIN,
    SENSOR_TYPE_INVERTER_FORECAST,
    SENSOR_TYPE_INVERTER_REMAINING,
    SENSOR_TYPE_STRING_FORECAST,
    SENSOR_TYPE_STRING_REMAINING,
)


@dataclass(frozen=True)
class OpenMeteoPVForecastSensorEntityDescription(SensorEntityDescription):
    """Class describing OpenMeteo PV Forecast sensor entities."""

    has_entity_name: bool = True


SENSOR_DESCRIPTIONS = [
    OpenMeteoPVForecastSensorEntityDescription(
        key=SENSOR_TYPE_STRING_FORECAST,
        translation_key="string_forecast",
        device_class=SensorDeviceClass.POWER,
        state_class=SensorStateClass.MEASUREMENT,
        native_unit_of_measurement=UnitOfPower.WATT,
        entity_category=EntityCategory.DIAGNOSTIC,
    ),
    OpenMeteoPVForecastSensorEntityDescription(
        key=SENSOR_TYPE_INVERTER_FORECAST,
        translation_key="inverter_forecast",
        device_class=SensorDeviceClass.POWER,
        state_class=SensorStateClass.MEASUREMENT,
        native_unit_of_measurement=UnitOfPower.WATT,
        entity_category=EntityCategory.DIAGNOSTIC,
    ),
    OpenMeteoPVForecastSensorEntityDescription(
        key=SENSOR_TYPE_STRING_REMAINING,
        translation_key="string_remaining",
        device_class=SensorDeviceClass.ENERGY,
        state_class=SensorStateClass.TOTAL,
        native_unit_of_measurement=UnitOfEnergy.WATT_HOUR,
        entity_category=EntityCategory.DIAGNOSTIC,
    ),
    OpenMeteoPVForecastSensorEntityDescription(
        key=SENSOR_TYPE_INVERTER_REMAINING,
        translation_key="inverter_remaining",
        device_class=SensorDeviceClass.ENERGY,
        state_class=SensorStateClass.TOTAL,
        native_unit_of_measurement=UnitOfEnergy.WATT_HOUR,
        entity_category=EntityCategory.DIAGNOSTIC,
    ),
]


async def async_setup_entry(
    hass: HomeAssistant, entry: ConfigEntry, async_add_entities: AddEntitiesCallback
) -> None:
    """Set up Open-Meteo PV Forecast sensors from config entry."""
    entities = []
    for description in SENSOR_DESCRIPTIONS:
        entities.append(OpenMeteoPVForecastSensor(entry.entry_id, description))
    async_add_entities(entities, True)


class OpenMeteoPVForecastSensor(SensorEntity):
    """Sensor showing PV forecast values."""

    entity_description: OpenMeteoPVForecastSensorEntityDescription

    def __init__(
        self, entry_id: str, description: OpenMeteoPVForecastSensorEntityDescription
    ) -> None:
        """Initialize the sensor."""
        self.entity_description = description
        self._attr_unique_id = f"{entry_id}_{description.key}"
        self._attr_device_info = {
            "identifiers": {(DOMAIN, entry_id)},
            "name": "Open-Meteo PV Forecast",
            "model": "Forecast Sensor",
            "manufacturer": "Open-Meteo",
        }
        self._attr_has_entity_name = True
        self._attr_extra_state_attributes: dict[str, Any] = {}

    def update(self) -> None:
        """Update the sensor state."""
        now = datetime.now(UTC)
        self._attr_native_value = 0.0

        forecast: dict[str, float] = {}
        for i in range(48):
            dt = now + timedelta(hours=i)
            hour = dt.hour
            # Simple bell curve simulation
            value = max(0, 10 * (1 - ((hour - 12) / 6) ** 2))
            forecast[dt.isoformat()] = round(value, 2)

        self._attr_extra_state_attributes = forecast
