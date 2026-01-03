"""Config flow for Consumable Tracker integration."""

from __future__ import annotations

import voluptuous as vol
from homeassistant import config_entries
from homeassistant.core import callback

from .const import (
    CONF_CONSUMABLE_NAME,
    CONF_CONSUMABLES,
    CONF_DEVICE_NAME,
    CONF_ICON_NORMAL,
    CONF_ICON_OVERDUE,
    CONF_ICON_WARNING,
    CONF_LIFETIME_DAYS,
    CONF_WARNING_DAYS,
    DEFAULT_ICON_NORMAL,
    DEFAULT_ICON_OVERDUE,
    DEFAULT_ICON_WARNING,
    DEFAULT_LIFETIME_DAYS,
    DEFAULT_WARNING_DAYS,
    DOMAIN,
)


class ConsumableTrackerConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for Consumable Tracker."""

    VERSION = 2

    def __init__(self) -> None:
        """Initialize the config flow."""
        self.device_name: str | None = None
        self.consumables: list[dict[str, object]] = []

    async def async_step_user(self, user_input=None):
        """Handle the initial step - device name."""
        errors = {}

        if user_input is not None:
            self.device_name = user_input[CONF_DEVICE_NAME]
            return await self.async_step_add_consumable()

        data_schema = vol.Schema(
            {
                vol.Required(CONF_DEVICE_NAME): str,
            }
        )

        return self.async_show_form(
            step_id="user",
            data_schema=data_schema,
            errors=errors,
            description_placeholders={
                "example": "Example: 'HVAC System', 'Kitchen Appliances', 'Water Treatment'"
            },
        )

    async def async_step_add_consumable(self, user_input=None):
        """Handle adding a consumable."""
        errors = {}

        if user_input is not None:
            # Check if user wants to add more
            if user_input.get("add_another"):
                # Save this consumable
                consumable = {
                    CONF_CONSUMABLE_NAME: user_input[CONF_CONSUMABLE_NAME],
                    CONF_LIFETIME_DAYS: user_input[CONF_LIFETIME_DAYS],
                    CONF_WARNING_DAYS: user_input[CONF_WARNING_DAYS],
                    CONF_ICON_NORMAL: user_input.get(
                        CONF_ICON_NORMAL, DEFAULT_ICON_NORMAL
                    ),
                    CONF_ICON_WARNING: user_input.get(
                        CONF_ICON_WARNING, DEFAULT_ICON_WARNING
                    ),
                    CONF_ICON_OVERDUE: user_input.get(
                        CONF_ICON_OVERDUE, DEFAULT_ICON_OVERDUE
                    ),
                }
                self.consumables.append(consumable)
                # Show form again for next consumable
                return await self.async_step_add_consumable()
            else:
                # Save this consumable and finish
                consumable = {
                    CONF_CONSUMABLE_NAME: user_input[CONF_CONSUMABLE_NAME],
                    CONF_LIFETIME_DAYS: user_input[CONF_LIFETIME_DAYS],
                    CONF_WARNING_DAYS: user_input[CONF_WARNING_DAYS],
                    CONF_ICON_NORMAL: user_input.get(
                        CONF_ICON_NORMAL, DEFAULT_ICON_NORMAL
                    ),
                    CONF_ICON_WARNING: user_input.get(
                        CONF_ICON_WARNING, DEFAULT_ICON_WARNING
                    ),
                    CONF_ICON_OVERDUE: user_input.get(
                        CONF_ICON_OVERDUE, DEFAULT_ICON_OVERDUE
                    ),
                }
                self.consumables.append(consumable)

                # Create the entry
                assert self.device_name is not None
                await self.async_set_unique_id(self.device_name)
                self._abort_if_unique_id_configured()

                return self.async_create_entry(
                    title=self.device_name,
                    data={
                        CONF_DEVICE_NAME: self.device_name,
                        CONF_CONSUMABLES: self.consumables,
                    },
                )

        data_schema = vol.Schema(
            {
                vol.Required(CONF_CONSUMABLE_NAME): str,
                vol.Required(
                    CONF_LIFETIME_DAYS, default=DEFAULT_LIFETIME_DAYS
                ): vol.All(vol.Coerce(int), vol.Range(min=1, max=730)),
                vol.Required(CONF_WARNING_DAYS, default=DEFAULT_WARNING_DAYS): vol.All(
                    vol.Coerce(int), vol.Range(min=0, max=365)
                ),
                vol.Optional(CONF_ICON_NORMAL, default=DEFAULT_ICON_NORMAL): str,
                vol.Optional(CONF_ICON_WARNING, default=DEFAULT_ICON_WARNING): str,
                vol.Optional(CONF_ICON_OVERDUE, default=DEFAULT_ICON_OVERDUE): str,
                vol.Required("add_another", default=False): bool,
            }
        )

        consumable_count = len(self.consumables)
        description = f"Adding consumable {consumable_count + 1} to {self.device_name}"
        if consumable_count > 0:
            description += f"\n\nAlready added: {', '.join([str(c[CONF_CONSUMABLE_NAME]) for c in self.consumables])}"

        return self.async_show_form(
            step_id="add_consumable",
            data_schema=data_schema,
            errors=errors,
            description_placeholders={"description": description},
        )

    @staticmethod
    @callback
    def async_get_options_flow(config_entry):
        """Get the options flow for this handler."""
        return ConsumableTrackerOptionsFlow(config_entry)


class ConsumableTrackerOptionsFlow(config_entries.OptionsFlow):
    """Handle options flow for Consumable Tracker."""

    def __init__(self, config_entry: config_entries.ConfigEntry) -> None:
        """Initialize options flow."""
        self._config_entry = config_entry
        self.consumables: list[dict[str, object]] = list(
            config_entry.data.get(CONF_CONSUMABLES, [])
        )
        self.editing_index: int | None = None

    async def async_step_init(self, user_input=None):
        """Manage the options - choose what to do."""
        if user_input is not None:
            action = user_input.get("action")
            if action == "add":
                return await self.async_step_add_consumable()
            elif action == "edit":
                return await self.async_step_select_consumable()
            elif action == "delete":
                return await self.async_step_delete_consumable()
            elif action == "done":
                # Save and finish
                self.hass.config_entries.async_update_entry(
                    self._config_entry,
                    data={
                        CONF_DEVICE_NAME: self._config_entry.data[CONF_DEVICE_NAME],
                        CONF_CONSUMABLES: self.consumables,
                    },
                )
                return self.async_create_entry(title="", data={})

        consumable_list = "\n".join(
            [
                f"- {c[CONF_CONSUMABLE_NAME]} ({c[CONF_LIFETIME_DAYS]} days)"
                for c in self.consumables
            ]
        )

        return self.async_show_form(
            step_id="init",
            data_schema=vol.Schema(
                {
                    vol.Required("action"): vol.In(
                        {
                            "add": "Add new consumable",
                            "edit": "Edit existing consumable",
                            "delete": "Delete consumable",
                            "done": "Save and finish",
                        }
                    )
                }
            ),
            description_placeholders={
                "consumables": consumable_list
                if consumable_list
                else "No consumables yet"
            },
        )

    async def async_step_add_consumable(self, user_input=None):
        """Add a new consumable."""
        if user_input is not None:
            consumable = {
                CONF_CONSUMABLE_NAME: user_input[CONF_CONSUMABLE_NAME],
                CONF_LIFETIME_DAYS: user_input[CONF_LIFETIME_DAYS],
                CONF_WARNING_DAYS: user_input[CONF_WARNING_DAYS],
                CONF_ICON_NORMAL: user_input.get(CONF_ICON_NORMAL, DEFAULT_ICON_NORMAL),
                CONF_ICON_WARNING: user_input.get(
                    CONF_ICON_WARNING, DEFAULT_ICON_WARNING
                ),
                CONF_ICON_OVERDUE: user_input.get(
                    CONF_ICON_OVERDUE, DEFAULT_ICON_OVERDUE
                ),
            }
            self.consumables.append(consumable)
            return await self.async_step_init()

        data_schema = vol.Schema(
            {
                vol.Required(CONF_CONSUMABLE_NAME): str,
                vol.Required(
                    CONF_LIFETIME_DAYS, default=DEFAULT_LIFETIME_DAYS
                ): vol.All(vol.Coerce(int), vol.Range(min=1, max=730)),
                vol.Required(CONF_WARNING_DAYS, default=DEFAULT_WARNING_DAYS): vol.All(
                    vol.Coerce(int), vol.Range(min=0, max=365)
                ),
                vol.Optional(CONF_ICON_NORMAL, default=DEFAULT_ICON_NORMAL): str,
                vol.Optional(CONF_ICON_WARNING, default=DEFAULT_ICON_WARNING): str,
                vol.Optional(CONF_ICON_OVERDUE, default=DEFAULT_ICON_OVERDUE): str,
            }
        )

        return self.async_show_form(step_id="add_consumable", data_schema=data_schema)

    async def async_step_select_consumable(self, user_input=None):
        """Select which consumable to edit."""
        if user_input is not None:
            self.editing_index = int(user_input["consumable"])
            return await self.async_step_edit_consumable()

        choices = {
            str(i): c[CONF_CONSUMABLE_NAME] for i, c in enumerate(self.consumables)
        }

        return self.async_show_form(
            step_id="select_consumable",
            data_schema=vol.Schema({vol.Required("consumable"): vol.In(choices)}),
        )

    async def async_step_edit_consumable(self, user_input=None):
        """Edit the selected consumable."""
        assert self.editing_index is not None
        if user_input is not None:
            self.consumables[self.editing_index] = {
                CONF_CONSUMABLE_NAME: user_input[CONF_CONSUMABLE_NAME],
                CONF_LIFETIME_DAYS: user_input[CONF_LIFETIME_DAYS],
                CONF_WARNING_DAYS: user_input[CONF_WARNING_DAYS],
                CONF_ICON_NORMAL: user_input.get(CONF_ICON_NORMAL, DEFAULT_ICON_NORMAL),
                CONF_ICON_WARNING: user_input.get(
                    CONF_ICON_WARNING, DEFAULT_ICON_WARNING
                ),
                CONF_ICON_OVERDUE: user_input.get(
                    CONF_ICON_OVERDUE, DEFAULT_ICON_OVERDUE
                ),
            }
            return await self.async_step_init()

        consumable = self.consumables[self.editing_index]
        data_schema = vol.Schema(
            {
                vol.Required(
                    CONF_CONSUMABLE_NAME, default=consumable[CONF_CONSUMABLE_NAME]
                ): str,
                vol.Required(
                    CONF_LIFETIME_DAYS, default=consumable[CONF_LIFETIME_DAYS]
                ): vol.All(vol.Coerce(int), vol.Range(min=1, max=730)),
                vol.Required(
                    CONF_WARNING_DAYS, default=consumable[CONF_WARNING_DAYS]
                ): vol.All(vol.Coerce(int), vol.Range(min=0, max=365)),
                vol.Optional(
                    CONF_ICON_NORMAL,
                    default=consumable.get(CONF_ICON_NORMAL, DEFAULT_ICON_NORMAL),
                ): str,
                vol.Optional(
                    CONF_ICON_WARNING,
                    default=consumable.get(CONF_ICON_WARNING, DEFAULT_ICON_WARNING),
                ): str,
                vol.Optional(
                    CONF_ICON_OVERDUE,
                    default=consumable.get(CONF_ICON_OVERDUE, DEFAULT_ICON_OVERDUE),
                ): str,
            }
        )

        return self.async_show_form(step_id="edit_consumable", data_schema=data_schema)

    async def async_step_delete_consumable(self, user_input=None):
        """Delete a consumable."""
        if user_input is not None:
            index = int(user_input["consumable"])
            self.consumables.pop(index)
            return await self.async_step_init()

        choices = {
            str(i): c[CONF_CONSUMABLE_NAME] for i, c in enumerate(self.consumables)
        }

        return self.async_show_form(
            step_id="delete_consumable",
            data_schema=vol.Schema({vol.Required("consumable"): vol.In(choices)}),
        )
