"""Config flow for Open-Meteo PV Forecast integration."""

from __future__ import annotations

from typing import Any

import voluptuous as vol
from homeassistant import config_entries
from homeassistant.core import callback
from homeassistant.helpers import selector

from .const import DOMAIN

'''
def inverter_schema(existing_names: set[str] | None = None) -> vol.Schema:
    """Return the schema for adding or editing an inverter."""
    return vol.Schema(
        {
            vol.Required(
                "name", description={"translation_key": "name"}
            ): selector.TextSelector(selector.TextSelectorConfig(type="text")),
            vol.Required(
                "size_w", description={"translation_key": "size_w"}
            ): selector.NumberSelector(
                selector.NumberSelectorConfig(min=1, step=100, unit_of_measurement="W")
            ),
            vol.Optional(
                "max_ac_w", description={"translation_key": "max_ac_w"}
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
'''


def inverter_schema(existing_names: set[str] | None = None) -> vol.Schema:
    """TEMP: Use only basic types for testing."""
    return vol.Schema(
        {
            vol.Required("name"): str,
            vol.Required("size_w"): int,
            vol.Optional("max_ac_w"): int,
            vol.Optional("inverter_eff", default=0.98): float,
        }
    )


def string_schema() -> vol.Schema:
    """Return the schema for adding a PV string."""
    return vol.Schema(
        {
            vol.Required(
                "azimuth", description={"translation_key": "azimuth"}
            ): selector.NumberSelector(
                selector.NumberSelectorConfig(
                    min=-179, max=180, step=1, unit_of_measurement="°"
                )
            ),
            vol.Required(
                "tilt", description={"translation_key": "tilt"}, default=30
            ): selector.NumberSelector(
                selector.NumberSelectorConfig(
                    min=0, max=90, step=1, unit_of_measurement="°"
                )
            ),
            vol.Required(
                "power_w", description={"translation_key": "power_w"}
            ): selector.NumberSelector(
                selector.NumberSelectorConfig(min=1, step=100, unit_of_measurement="Wp")
            ),
            vol.Optional(
                "albedo", description={"translation_key": "albedo"}, default=0.2
            ): selector.NumberSelector(
                selector.NumberSelectorConfig(min=0, max=1, step=0.01, mode="box")
            ),
            vol.Optional(
                "cell_coeff",
                description={"translation_key": "cell_coeff"},
                default=0.0328,
            ): selector.NumberSelector(
                selector.NumberSelectorConfig(min=0, step=0.001, mode="box")
            ),
        }
    )


class OpenMeteoPVForecastConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle the initial config flow for the Open-Meteo PV Forecast integration."""

    VERSION = 1

    def __init__(self) -> None:
        """Initialize the config flow."""
        self._inverters: list[dict[str, Any]] = []
        self._strings: list[dict[str, Any]] = []

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> config_entries.ConfigFlowResult:
        """Initial step: add the first inverter."""
        existing_names = {inv["name"] for inv in self._inverters}

        if user_input is not None:
            if user_input["name"] in existing_names:
                return self.async_show_form(
                    step_id="user",
                    data_schema=inverter_schema(existing_names),
                    errors={"name": "name_exists"},
                )
            self._inverters.append(user_input)
            return self.async_show_form(
                step_id="inverters_menu",
                data_schema=vol.Schema(
                    {
                        vol.Required("menu_option"): vol.In(["add_another", "done"]),
                    }
                ),
            )

        return self.async_show_form(
            step_id="user",
            data_schema=inverter_schema(existing_names),
        )

    async def async_step_inverters_add(
        self, user_input: dict[str, Any] | None = None
    ) -> config_entries.ConfigFlowResult:
        """Add a new inverter."""
        existing_names = {inv["name"] for inv in self._inverters}

        if user_input is not None:
            if user_input["name"] in existing_names:
                return self.async_show_form(
                    step_id="inverters_add",
                    data_schema=inverter_schema(existing_names),
                    errors={"name": "name_exists"},
                )
            self._inverters.append(user_input)
            return self.async_show_form(
                step_id="inverters_menu",
                data_schema=vol.Schema(
                    {
                        vol.Required("menu_option"): vol.In(["add_another", "done"]),
                    }
                ),
            )

        return self.async_show_form(
            step_id="inverters_add",
            data_schema=inverter_schema(existing_names),
        )

    async def async_step_inverters_menu(
        self, user_input: dict[str, Any]
    ) -> config_entries.ConfigFlowResult:
        """Handle user choice after adding an inverter."""
        if user_input["menu_option"] == "add_another":
            return await self.async_step_inverters_add()
        return await self.async_step_strings_add()

    async def async_step_strings_add(
        self, user_input: dict[str, Any] | None = None
    ) -> config_entries.ConfigFlowResult:
        """Add a PV string."""
        if user_input is not None:
            self._strings.append(user_input)
            return self.async_show_form(
                step_id="strings_menu",
                data_schema=vol.Schema(
                    {
                        vol.Required("menu_option"): vol.In(["add_another", "done"]),
                    }
                ),
            )

        return self.async_show_form(
            step_id="strings_add",
            data_schema=string_schema(),
        )

    async def async_step_strings_menu(
        self, user_input: dict[str, Any]
    ) -> config_entries.ConfigFlowResult:
        """Handle user choice after adding a PV string."""
        if user_input["menu_option"] == "add_another":
            return await self.async_step_strings_add()

        return self.async_create_entry(
            title="Open-Meteo PV Forecast",
            data={
                "inverters": self._inverters,
                "strings": self._strings,
            },
        )

    @staticmethod
    @callback
    def async_get_options_flow(
        config_entry: config_entries.ConfigEntry,
    ) -> config_entries.OptionsFlow:
        """Return the options flow handler."""
        from .options_flow import OpenMeteoPVForecastOptionsFlowHandler

        return OpenMeteoPVForecastOptionsFlowHandler(config_entry)
