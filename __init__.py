"""Init file for Open-Meteo PV Forecast integration."""

from __future__ import annotations
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from .const import DOMAIN
from .config_flow import OpenMeteoPVForecastOptionsFlowHandler

PLATFORMS = ["sensor"]


async def async_setup(hass: HomeAssistant, config: dict) -> bool:
    """Set up via YAML (not used)."""
    return True


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up Open-Meteo PV Forecast from a config entry."""

    hass.data.setdefault(DOMAIN, {})
    hass.data[DOMAIN][entry.entry_id] = entry.data

    # Launch options flow if inverters empty
    if not entry.options.get("inverters"):
        hass.async_create_task(
            hass.config_entries.flow.async_init(
                DOMAIN,
                context={"source": "options"},
                data=entry.data,
            )
        )

    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)

    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    return True


async def async_get_options_flow(entry: ConfigEntry):
    """Return the options flow handler (for Configure button)."""
    return OpenMeteoPVForecastOptionsFlowHandler(entry)
