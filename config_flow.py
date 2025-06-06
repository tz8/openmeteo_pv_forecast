"""Config flow for Open-Meteo PV Forecast integration."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

import voluptuous as vol

from homeassistant import config_entries
from homeassistant.const import CONF_NAME, UnitOfLength
from homeassistant.core import callback
from homeassistant.data_entry_flow import FlowResult
from homeassistant.helpers import selector

from .const import (
    CONF_HORIZON,
    CONF_VERSION,
    CONF_WEATHER_MODEL,
    DEFAULT_HORIZON,
    DEFAULT_WEATHER_MODEL,
    DOMAIN,
    WEATHER_MODELS,
)

CONF_INVERTERS = "inverters"
CONF_STRINGS = "strings"
CONF_INVERTER = "inverter"
CONF_STRING_NAME = "string_name"


@dataclass
class Inverter:
    """Inverter configuration class."""

    name: str
    size_w: int
    max_ac_w: int | None = None
    inverter_eff: float = 0.98


@dataclass
class PVString:
    """PV string configuration class."""

    name: str
    inverter: str
    azimuth: int
    tilt: int
    power_w: int
    horizon: list[float]  # Add horizon field
    albedo: float = 0.2
    cell_coeff: float = 0.0328


def inverter_schema(existing_names: set[str] | None = None) -> vol.Schema:
    """Get schema for inverter configuration."""
    return vol.Schema(
        {
            vol.Required("name"): str,
            vol.Required("size_w"): selector.NumberSelector(
                selector.NumberSelectorConfig(
                    min=100,
                    step=10,
                    unit_of_measurement="W",
                    mode=selector.NumberSelectorMode.BOX,
                ),
            ),
            vol.Optional("max_ac_w"): selector.NumberSelector(
                selector.NumberSelectorConfig(
                    min=100,
                    step=10,
                    unit_of_measurement="W",
                    mode=selector.NumberSelectorMode.BOX,
                ),
            ),
            vol.Optional("inverter_eff", default=0.98): selector.NumberSelector(
                selector.NumberSelectorConfig(
                    min=0.8,
                    max=1.0,
                    step=0.01,
                    mode=selector.NumberSelectorMode.BOX,
                ),
            ),
        }
    )


def string_schema(
    inverters: list[dict[str, Any]], existing_names: set[str] | None = None
) -> vol.Schema:
    """Get schema for PV string configuration."""
    schema = {
        vol.Required(CONF_STRING_NAME): str,
        vol.Required(CONF_INVERTER): selector.SelectSelector(
            selector.SelectSelectorConfig(
                options=[inv["name"] for inv in inverters],
                mode=selector.SelectSelectorMode.DROPDOWN,
            ),
        ),
        vol.Required("azimuth", default=0): selector.NumberSelector(
            selector.NumberSelectorConfig(
                min=-179,
                max=180,
                step=1,
                unit_of_measurement="°",
                mode=selector.NumberSelectorMode.SLIDER,
            ),
        ),
        vol.Required("tilt", default=30): selector.NumberSelector(
            selector.NumberSelectorConfig(
                min=0,
                max=90,
                step=1,
                unit_of_measurement="°",
                mode=selector.NumberSelectorMode.SLIDER,
            ),
        ),
        vol.Required("power_w"): selector.NumberSelector(
            selector.NumberSelectorConfig(
                min=100,
                step=10,
                unit_of_measurement="Wp",
                mode=selector.NumberSelectorMode.BOX,
            ),
        ),
    }

    # Add horizon fields
    for i in range(12):
        schema[vol.Optional(f"horizon_{i}", default=0.0)] = selector.NumberSelector(
            selector.NumberSelectorConfig(
                min=0,
                max=90,
                step=0.5,
                unit_of_measurement="°",
                mode=selector.NumberSelectorMode.BOX,
            ),
        )

    # Existing albedo, cell_coeff fields
    schema.update(
        {
            vol.Optional("albedo", default=0.2): selector.NumberSelector(
                selector.NumberSelectorConfig(
                    min=0,
                    max=1,
                    step=0.01,
                    mode=selector.NumberSelectorMode.BOX,
                ),
            ),
            vol.Optional("cell_coeff", default=0.0328): selector.NumberSelector(
                selector.NumberSelectorConfig(
                    min=0,
                    max=0.1,
                    step=0.001,
                    mode=selector.NumberSelectorMode.BOX,
                ),
            ),
        }
    )

    return vol.Schema(schema)


def horizon_schema(current_values: list[float] | None = None) -> vol.Schema:
    """Get schema for horizon configuration."""
    if current_values is None:
        current_values = DEFAULT_HORIZON

    schema = {
        f"horizon_{i}": vol.All(
            vol.Coerce(float),
            vol.Range(min=0, max=90),
            msg="Value must be between 0 and 90 degrees",
        )
        for i in range(12)
    }

    return vol.Schema(
        {
            vol.Required(
                f"horizon_{i}", default=current_values[i]
            ): selector.NumberSelector(
                selector.NumberSelectorConfig(
                    min=0,
                    max=90,
                    step=0.5,
                    unit_of_measurement="°",
                    mode=selector.NumberSelectorMode.BOX,
                ),
            )
            for i in range(12)
        }
    )


def weather_model_schema(unit_system: str = UnitOfLength.KILOMETERS) -> vol.Schema:
    """Get schema for weather model selection."""
    return vol.Schema(
        {
            vol.Required(
                CONF_WEATHER_MODEL, default=DEFAULT_WEATHER_MODEL
            ): selector.SelectSelector(
                selector.SelectSelectorConfig(
                    options=[
                        selector.SelectOptionDict(
                            value=model.id,
                            label=f"{model.name} ({model.region}, {model.get_resolution(unit_system)})",
                        )
                        for model in WEATHER_MODELS.values()
                    ],
                    mode=selector.SelectSelectorMode.DROPDOWN,
                )
            ),
        }
    )


class OpenMeteoPVForecastConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle config flow for Open-Meteo PV Forecast."""

    VERSION = 2

    def __init__(self) -> None:
        """Initialize config flow."""
        self._weather_model: str | None = None
        self._inverters: list[dict[str, Any]] = []
        self._strings: list[dict[str, Any]] = []

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Handle the initial step."""
        if user_input is not None:
            if user_input["next_step_id"] == "finish":
                return self.async_create_entry(
                    title="Open-Meteo PV Forecast",
                    data={},
                    options={
                        CONF_WEATHER_MODEL: self._weather_model,
                        CONF_INVERTERS: self._inverters,
                        CONF_STRINGS: self._strings,
                    },
                )
            return await self.async_step(user_input["next_step_id"])

        # Build menu options based on configuration state
        menu_options = ["weather_model", "add_inverter", "add_string"]

        # Only show finish when we have all required components
        if (
            self._weather_model is not None
            and self._inverters
            and self._strings
            and any(
                s["inverter"] in [i["name"] for i in self._inverters]
                for s in self._strings
            )
        ):
            menu_options.append("finish")

        return self.async_show_menu(
            step_id="user",
            menu_options=menu_options,
        )

    async def async_step_add_inverter(
        self,
        user_input: dict[str, Any] | None = None,
    ) -> FlowResult:
        """Handle adding an inverter."""
        errors = {}

        if user_input is not None:
            name = user_input["name"]
            if any(inv["name"] == name for inv in self._inverters):
                errors["name"] = "name_exists"
            else:
                self._inverters.append(user_input)
                return await self.async_step_add_string()

        return self.async_show_form(
            step_id="add_inverter",
            data_schema=inverter_schema({inv["name"] for inv in self._inverters}),
            errors=errors,
        )

    async def async_step_add_string(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Handle adding a PV string."""
        if not self._inverters:
            return await self.async_step_add_inverter()

        if user_input is not None:
            # Extract horizon values from input
            horizon = [user_input[f"horizon_{i}"] for i in range(12)]
            string_data = {
                k: v for k, v in user_input.items() if not k.startswith("horizon_")
            }
            string_data["horizon"] = horizon
            self._strings.append(string_data)
            return await self.async_step_user()

        return self.async_show_form(
            step_id="add_string",
            data_schema=string_schema(self._inverters),
        )

    async def async_step_finish(
        self,
        user_input: dict[str, Any] | None = None,
    ) -> FlowResult:
        """Finish configuration."""
        return self.async_create_entry(
            title="Open-Meteo PV Forecast",
            data={},
            options={
                CONF_INVERTERS: self._inverters,
                CONF_STRINGS: self._strings,
            },
        )

    async def async_step_weather_model(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Handle weather model selection."""
        if user_input is not None:
            self._weather_model = user_input[CONF_WEATHER_MODEL]
            return await self.async_step_user()

        return self.async_show_form(
            step_id="weather_model",
            data_schema=weather_model_schema(self.hass.config.units.length_unit),
        )

    @staticmethod
    @callback
    def async_get_options_flow(
        config_entry: config_entries.ConfigEntry,
    ) -> OpenMeteoPVForecastOptionsFlow:
        """Get the options flow."""
        return OpenMeteoPVForecastOptionsFlow(config_entry)


class OpenMeteoPVForecastOptionsFlow(config_entries.OptionsFlow):
    """Handle options flow for Open-Meteo PV Forecast."""

    def __init__(self, config_entry: config_entries.ConfigEntry) -> None:
        """Initialize options flow."""
        self.inverters = list(config_entry.options.get(CONF_INVERTERS, []))
        self.strings = list(config_entry.options.get(CONF_STRINGS, []))
        self.weather_model = config_entry.options.get(CONF_WEATHER_MODEL)

    async def async_step_init(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Handle options flow."""
        if user_input is not None:
            if user_input["menu_option"] == "done":
                return self.async_create_entry(
                    title="",
                    data={
                        CONF_INVERTERS: self.inverters,
                        CONF_STRINGS: self.strings,
                    },
                )
            return await self.async_step(user_input["menu_option"])

        return self.async_show_menu(
            step_id="init",
            menu_options=[
                "edit_inverters",
                "edit_strings",
                "done",
            ],  # Remove edit_horizon
        )

    async def async_step_edit_inverters(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Edit inverters."""
        if user_input is not None:
            if user_input["action"] == "add":
                return await self.async_step_add_inverter()
            if user_input["action"] == "edit":
                return await self.async_step_edit_inverter(user_input["inverter"])
            if user_input["action"] == "remove":
                # Check if inverter has strings
                if any(s["inverter"] == user_input["inverter"] for s in self.strings):
                    return self.async_show_form(
                        step_id="edit_inverters",
                        data_schema=edit_inverters_schema(self.inverters),
                        errors={"base": "cannot_delete_with_strings"},
                    )
                self.inverters = [
                    inv
                    for inv in self.inverters
                    if inv["name"] != user_input["inverter"]
                ]
                return await self.async_step_init()

        return self.async_show_form(
            step_id="edit_inverters",
            data_schema=edit_inverters_schema(self.inverters),
        )

    async def async_step_edit_inverter(
        self, inverter_name: str, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Edit a specific inverter."""
        inverter = next(
            (inv for inv in self.inverters if inv["name"] == inverter_name), None
        )
        if inverter is None:
            return await self.async_step_edit_inverters()

        if user_input is not None:
            # Update inverter with new values while keeping the name
            updated_inverter = {
                "name": inverter_name,  # Keep original name
                "size_w": user_input["size_w"],
                "max_ac_w": user_input.get("max_ac_w"),  # Optional field
                "inverter_eff": user_input["inverter_eff"],
            }
            # Replace old inverter with updated one
            self.inverters = [
                updated_inverter if inv["name"] == inverter_name else inv
                for inv in self.inverters
            ]
            # Return to inverters menu
            return await self.async_step_edit_inverters()

        # Show form with current values
        return self.async_show_form(
            step_id="edit_inverter",
            data_schema=vol.Schema(
                {
                    vol.Required(
                        "size_w", default=inverter["size_w"]
                    ): selector.NumberSelector(
                        selector.NumberSelectorConfig(
                            min=100,
                            step=10,
                            unit_of_measurement="W",
                            mode=selector.NumberSelectorMode.BOX,
                        ),
                    ),
                    vol.Optional(
                        "max_ac_w", default=inverter.get("max_ac_w")
                    ): selector.NumberSelector(
                        selector.NumberSelectorConfig(
                            min=100,
                            step=10,
                            unit_of_measurement="W",
                            mode=selector.NumberSelectorMode.BOX,
                        ),
                    ),
                    vol.Required(
                        "inverter_eff", default=inverter.get("inverter_eff", 0.98)
                    ): selector.NumberSelector(
                        selector.NumberSelectorConfig(
                            min=0.8,
                            max=1.0,
                            step=0.01,
                            mode=selector.NumberSelectorMode.BOX,
                        ),
                    ),
                }
            ),
            description_placeholders={
                "name": inverter_name,
            },
        )

    async def async_step_edit_strings(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Edit PV strings."""
        if user_input is not None:
            if user_input["action"] == "add":
                return await self.async_step_add_string()
            if user_input["action"] == "edit":
                self.current_string = next(
                    (
                        s
                        for s in self.strings
                        if s[CONF_STRING_NAME] == user_input["string"]
                    ),
                    None,
                )
                return await self.async_step_edit_string()
            if user_input["action"] == "remove":
                self.strings = [
                    s
                    for s in self.strings
                    if s[CONF_STRING_NAME] != user_input["string"]
                ]
            return self.async_create_entry(
                title="",
                data={
                    CONF_INVERTERS: self.inverters,
                    CONF_STRINGS: self.strings,
                },
            )

        if not self.strings:
            return await self.async_step_add_string()

        return self.async_show_form(
            step_id="edit_strings",
            data_schema=vol.Schema(
                {
                    vol.Required("action"): vol.In(
                        {
                            "add": "Add String",
                            "edit": "Edit String",
                            "remove": "Remove String",
                            "back": "Back",
                        }
                    ),
                    vol.Optional("string"): vol.In(
                        {
                            s[
                                CONF_STRING_NAME
                            ]: f"{s[CONF_STRING_NAME]} ({s[CONF_INVERTER]} - {s['power_w']}Wp)"
                            for s in self.strings
                        }
                    ),
                }
            ),
        )

    async def async_step_edit_horizon(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Edit horizon values."""
        if user_input is not None:
            # Convert form data to horizon list
            self.horizon = [user_input[f"horizon_{i}"] for i in range(12)]
            return self.async_create_entry(
                title="",
                data={
                    CONF_INVERTERS: self.inverters,
                    CONF_STRINGS: self.strings,
                    CONF_HORIZON: self.horizon,
                },
            )

        return self.async_show_form(
            step_id="edit_horizon",
            data_schema=horizon_schema(self.horizon),
            description_placeholders={
                "ranges": "Values for each 30° segment (12-1h is first, clockwise)",
            },
        )


def edit_inverters_schema(inverters: list[dict[str, Any]]) -> vol.Schema:
    """Get schema for editing inverters."""
    if not inverters:
        return vol.Schema({})

    return vol.Schema(
        {
            vol.Required("action", default="add"): vol.In(
                {
                    "add": "Add Inverter",
                    "edit": "Edit Inverter",
                    "remove": "Remove Inverter",
                }
            ),
            vol.Optional("inverter"): vol.In(
                {inv["name"]: inv["name"] for inv in inverters}
            ),
        }
    )
