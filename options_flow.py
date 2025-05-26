"""Options flow for Open-Meteo PV Forecast integration."""

from __future__ import annotations

import voluptuous as vol
from homeassistant import config_entries
from homeassistant.core import callback

from .config_flow import DOMAIN, inverter_schema, string_schema


class OpenMeteoPVForecastOptionsFlowHandler(config_entries.OptionsFlow):
    """Handle options flow for Open-Meteo PV Forecast."""

    def __init__(self, config_entry: config_entries.ConfigEntry) -> None:
        """Initialize the options flow handler."""
        self.config_entry = config_entry
        self._data = dict(config_entry.options) if config_entry.options else {}
        self._inverters = self._data.get("inverters", [])
        self._strings = self._data.get("strings", [])

    async def async_step_init(self, user_input=None):
        """Start options flow: choose what to edit."""
        if user_input is not None:
            choice = user_input["menu_option"]
            if choice == "edit_inverters":
                return await self.async_step_inverters_edit()
            if choice == "edit_strings":
                return await self.async_step_strings_edit()
            return self.async_create_entry(title="", data=self._data)

        return self.async_show_form(
            step_id="init",
            data_schema=vol.Schema(
                {
                    vol.Required("menu_option"): vol.In(
                        ["edit_inverters", "edit_strings", "done"]
                    ),
                }
            ),
        )

    async def async_step_inverters_edit(self, user_input=None):
        """Manage the list of inverters (add/edit/delete)."""
        if user_input is not None:
            selected = user_input["menu_option"]
            if selected == "add_inverter":
                return await self.async_step_inverters_add()
            if selected == "back":
                return await self.async_step_init()
            for idx, inv in enumerate(self._inverters):
                if inv["name"] == selected:
                    return await self.async_step_inverters_edit_item(idx)

        inverter_names = [inv["name"] for inv in self._inverters]
        return self.async_show_form(
            step_id="inverters_edit",
            data_schema=vol.Schema(
                {
                    vol.Required("menu_option"): vol.In(
                        inverter_names + ["add_inverter", "back"]
                    ),
                }
            ),
        )

    async def async_step_inverters_add(self, user_input=None):
        """Add a new inverter."""
        existing_names = {inv["name"] for inv in self._inverters}

        if user_input is not None:
            name = user_input["name"]
            if name in existing_names:
                return self.async_show_form(
                    step_id="inverters_add",
                    data_schema=inverter_schema(existing_names),
                    errors={"name": "name_exists"},
                )
            self._inverters.append(user_input)
            return await self.async_step_inverters_edit()

        return self.async_show_form(
            step_id="inverters_add",
            data_schema=inverter_schema(existing_names),
        )

    async def async_step_inverters_edit_item(self, idx: int, user_input=None):
        """Edit or delete an existing inverter."""
        inverter = self._inverters[idx]
        existing_names = {
            inv["name"] for i, inv in enumerate(self._inverters) if i != idx
        }

        if user_input is not None:
            if user_input.get("action") == "delete":
                self._inverters.pop(idx)
                return await self.async_step_inverters_edit()

            if user_input["name"] in existing_names:
                return self.async_show_form(
                    step_id=f"inverters_edit_item_{idx}",
                    data_schema=inverter_schema(existing_names).extend(
                        {
                            vol.Required("action", default="edit"): vol.In(
                                ["edit", "delete"]
                            ),
                        }
                    ),
                    errors={"name": "name_exists"},
                    data=user_input,
                )

            self._inverters[idx] = user_input
            return await self.async_step_inverters_edit()

        schema = inverter_schema(existing_names).extend(
            {
                vol.Required("action", default="edit"): vol.In(["edit", "delete"]),
            }
        )

        return self.async_show_form(
            step_id=f"inverters_edit_item_{idx}",
            data_schema=schema,
            data=inverter,
        )

    async def async_step_strings_edit(self, user_input=None):
        """Manage the list of PV strings (add/edit/delete)."""
        if user_input is not None:
            selected = user_input["menu_option"]
            if selected == "add_string":
                return await self.async_step_strings_add()
            if selected == "back":
                return await self.async_step_init()
            if selected.startswith("String "):
                idx = int(selected.split(" ")[1]) - 1
                return await self.async_step_strings_edit_item(idx)

        string_names = [f"String {i + 1}" for i in range(len(self._strings))]
        return self.async_show_form(
            step_id="strings_edit",
            data_schema=vol.Schema(
                {
                    vol.Required("menu_option"): vol.In(
                        string_names + ["add_string", "back"]
                    ),
                }
            ),
        )

    async def async_step_strings_add(self, user_input=None):
        """Add a new PV string."""
        if user_input is not None:
            self._strings.append(user_input)
            return await self.async_step_strings_edit()

        return self.async_show_form(
            step_id="strings_add",
            data_schema=string_schema(),
        )

    async def async_step_strings_edit_item(self, idx: int, user_input=None):
        """Edit or delete a PV string."""
        string = self._strings[idx]

        if user_input is not None:
            if user_input.get("action") == "delete":
                self._strings.pop(idx)
                return await self.async_step_strings_edit()

            self._strings[idx] = user_input
            return await self.async_step_strings_edit()

        schema = string_schema().extend(
            {
                vol.Required("action", default="edit"): vol.In(["edit", "delete"]),
            }
        )

        return self.async_show_form(
            step_id=f"strings_edit_item_{idx}",
            data_schema=schema,
            data=string,
        )
