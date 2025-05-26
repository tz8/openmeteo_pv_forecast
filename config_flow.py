"""Config flow for Open-Meteo PV Forecast integration."""

from __future__ import annotations

import voluptuous as vol
from homeassistant import config_entries
from homeassistant.core import callback
from homeassistant.helpers import config_validation as cv
from homeassistant.helpers import selector

DOMAIN = "openmeteo_pv_forecast"


def inverter_schema(existing_names=None) -> vol.Schema:
    """Return the inverter input schema with translated field labels."""
    return vol.Schema(
        {
            vol.Required(
                "name",
                description={"translation_key": "name"},
            ): selector.TextSelector(selector.TextSelectorConfig(type="text")),
            vol.Required(
                "size_w", description={"translation_key": "size_w"}, default=15000
            ): selector.NumberSelector(
                selector.NumberSelectorConfig(min=1, step=100, unit_of_measurement="W")
            ),
            vol.Optional(
                "max_ac_w", description={"translation_key": "max_ac_w"}, default=10300
            ): selector.NumberSelector(
                selector.NumberSelectorConfig(min=1, step=100, unit_of_measurement="W")
            ),
            vol.Optional(
                "inverter_eff",
                description={"translation_key": "inverter_eff"},
                default=0.98,
            ): selector.NumberSelector(
                selector.NumberSelectorConfig(min=0, max=1, step=0.01, mode="box")
            ),
        }
    )


def string_schema():
    """Return schema for string configuration."""
    return vol.Schema(
        {
            vol.Required("azimuth"): selector.NumberSelector(
                selector.NumberSelectorConfig(
                    min=-179, max=180, step=1, unit_of_measurement="°"
                ),
                translation_key="azimuth",
            ),
            vol.Required("tilt", default=30): selector.NumberSelector(
                selector.NumberSelectorConfig(
                    min=0, max=90, step=1, unit_of_measurement="°"
                ),
                translation_key="tilt",
            ),
            vol.Required("power_w"): selector.NumberSelector(
                selector.NumberSelectorConfig(
                    min=1, step=100, unit_of_measurement="Wp"
                ),
                translation_key="power_w",
            ),
            vol.Optional("albedo", default=0.2): selector.NumberSelector(
                selector.NumberSelectorConfig(min=0, max=1, step=0.01, mode="box"),
                translation_key="albedo",
            ),
            vol.Optional("cell_coeff", default=0.0328): selector.NumberSelector(
                selector.NumberSelectorConfig(min=0, step=0.001, mode="box"),
                translation_key="cell_coeff",
            ),
        }
    )


class OpenMeteoPVForecastConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for Open-Meteo PV Forecast."""

    VERSION = 1

    def __init__(self) -> None:
        """Initialize the config flow."""
        self._data: dict[str, any] = {}
        self._inverters: list[dict[str, any]] = []
        self._strings: list[dict[str, any]] = []

    async def async_step_user(
        self, user_input: dict[str, any] | None = None
    ) -> config_entries.FlowResult:
        """Handle the initial step - use default HA location."""
        # Use Home Assistant's default location
        self._data["latitude"] = self.hass.config.latitude
        self._data["longitude"] = self.hass.config.longitude
        self._data["location_name"] = self.hass.config.location_name or "Home"

        return await self.async_step_inverters_add()

    async def async_step_inverters_add(
        self, user_input: dict[str, any] | None = None
    ) -> config_entries.FlowResult:
        """Handle adding an inverter."""
        if user_input is not None:
            # Check for unique name
            new_name = user_input["name"]
            if any(inv["name"] == new_name for inv in self._inverters):
                return self.async_show_form(
                    step_id="inverters_add",
                    data_schema=inverter_schema(),
                    errors={"name": "name_exists"} if duplicate else {},
                    description_placeholders={},
                )
            self._inverters.append(user_input)
            # Ask user: add another inverter or continue?
            return self.async_show_menu(
                step_id="inverters_menu",
                menu_options=["add_another", "done"],
            )

        return self.async_show_form(
            step_id="inverters_add",
            data_schema=inverter_schema(),
        )

    async def async_step_inverters_menu(
        self, user_input: dict[str, any] | None = None
    ) -> config_entries.FlowResult:
        """Handle menu after adding inverter."""
        if user_input is None:
            return self.async_show_menu(
                step_id="inverters_menu",
                menu_options=["add_another", "done"],
            )
        if user_input == {"menu_option": "add_another"}:
            return await self.async_step_inverters_add()
        elif user_input == {"menu_option": "done"}:
            return await self.async_step_strings_add()

    async def async_step_strings_add(
        self, user_input: dict[str, any] | None = None
    ) -> config_entries.FlowResult:
        """Handle adding a string."""
        if user_input is not None:
            self._strings.append(user_input)
            # Ask user: add another string or finish?
            return self.async_show_menu(
                step_id="strings_menu",
                menu_options=["add_another", "done"],
            )
        return self.async_show_form(
            step_id="strings_add",
            data_schema=string_schema(),
        )

    async def async_step_strings_menu(
        self, user_input: dict[str, any] | None = None
    ) -> config_entries.FlowResult:
        """Handle menu after adding string."""
        if user_input is None:
            return self.async_show_menu(
                step_id="strings_menu",
                menu_options=["add_another", "done"],
            )
        if user_input == {"menu_option": "add_another"}:
            return await self.async_step_strings_add()
        elif user_input == {"menu_option": "done"}:
            # Finalize config entry
            self._data["inverters"] = self._inverters
            self._data["strings"] = self._strings
            return self.async_create_entry(
                title=f"PV Forecast - {self._data['location_name']}",
                data=self._data,
            )

    @staticmethod
    @callback
    def async_get_options_flow(
        config_entry: config_entries.ConfigEntry,
    ) -> OpenMeteoPVForecastOptionsFlowHandler:
        """Get the options flow for this handler."""
        from .options_flow import OpenMeteoPVForecastOptionsFlowHandler

        return OpenMeteoPVForecastOptionsFlowHandler(config_entry)
