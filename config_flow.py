import voluptuous as vol
from homeassistant import config_entries
from homeassistant.core import callback
from homeassistant.helpers import config_validation as cv

DOMAIN = "openmeteo_pv_forecast"


def inverter_schema(existing_names=None):
    existing_names = existing_names or set()
    return vol.Schema(
        {
            vol.Required("name"): str,
            vol.Required("size_w"): vol.All(vol.Coerce(int), vol.Range(min=1)),
            vol.Optional("max_ac_w"): vol.All(vol.Coerce(int), vol.Range(min=1)),
            vol.Optional("inverter_eff", default=0.98): vol.All(
                vol.Coerce(float), vol.Range(min=0, max=1)
            ),
        }
    )


def string_schema():
    return vol.Schema(
        {
            vol.Required("azimuth"): vol.All(
                vol.Coerce(int), vol.Range(min=-179, max=180)
            ),
            vol.Required("tilt", default=30): vol.All(
                vol.Coerce(int), vol.Range(min=0, max=90)
            ),
            vol.Required("power_w"): vol.All(vol.Coerce(int), vol.Range(min=1)),
            vol.Optional("albedo", default=0.2): vol.Coerce(float),
            vol.Optional("cell_coeff", default=0.0328): vol.Coerce(float),
        }
    )


class OpenMeteoPVForecastConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    VERSION = 1

    def __init__(self):
        self._data = {}
        self._inverters = []
        self._strings = []

    async def async_step_user(self, user_input=None):
        """First step: ask for home."""
        if user_input is None:
            return self.async_show_form(
                step_id="user",
                data_schema=vol.Schema({vol.Required("home"): str}),
            )
        self._data["home"] = user_input["home"]
        return await self.async_step_inverters_add()

    async def async_step_inverters_add(self, user_input=None):
        """Step to add an inverter."""
        if user_input is not None:
            # Check for unique name
            new_name = user_input["name"]
            if any(inv["name"] == new_name for inv in self._inverters):
                return self.async_show_form(
                    step_id="inverters_add",
                    data_schema=inverter_schema(),
                    errors={"name": "name_exists"},
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

    async def async_step_inverters_menu(self, user_input=None):
        """Menu after adding inverter: add more or go to strings."""
        if user_input is None:
            return self.async_show_menu(
                step_id="inverters_menu",
                menu_options=["add_another", "done"],
            )
        if user_input == {"menu_option": "add_another"}:
            return await self.async_step_inverters_add()
        elif user_input == {"menu_option": "done"}:
            return await self.async_step_strings_add()

    async def async_step_strings_add(self, user_input=None):
        """Step to add a string."""
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

    async def async_step_strings_menu(self, user_input=None):
        """Menu after adding string: add more or finish."""
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
                title="Open-Meteo PV Forecast", data=self._data
            )

    @staticmethod
    @callback
    def async_get_options_flow(config_entry):
        from .options_flow import OpenMeteoPVForecastOptionsFlowHandler

        return OpenMeteoPVForecastOptionsFlowHandler(config_entry)
