"""Integration for Open-Meteo PV Forecast."""

from __future__ import annotations

from typing import Any

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import Platform
from homeassistant.core import HomeAssistant

from .const import (
    CONF_HORIZON,
    CONF_WEATHER_MODEL,
    DEFAULT_HORIZON,
    DEFAULT_WEATHER_MODEL,
    DOMAIN,
)

PLATFORMS: list[Platform] = [Platform.SENSOR]


async def async_migrate_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Migrate old entry."""
    if entry.version == 1:
        options = {
            **entry.options,
            CONF_HORIZON: DEFAULT_HORIZON,
            CONF_WEATHER_MODEL: DEFAULT_WEATHER_MODEL,
        }

        hass.config_entries.async_update_entry(entry, options=options, version=2)

    return True


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up Open-Meteo PV Forecast from a config entry."""
    if entry.version < 2:
        if not await async_migrate_entry(hass, entry):
            return False

    hass.data.setdefault(DOMAIN, {})
    hass.data[DOMAIN][entry.entry_id] = entry.options

    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)

    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    unload_ok = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
    if unload_ok:
        hass.data[DOMAIN].pop(entry.entry_id)

    return unload_ok
