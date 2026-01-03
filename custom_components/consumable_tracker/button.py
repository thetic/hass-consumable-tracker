"""Button platform for Consumable Tracker."""

from __future__ import annotations

from datetime import date

from homeassistant.components.button import ButtonEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import CONF_CONSUMABLE_NAME, CONF_CONSUMABLES, CONF_DEVICE_NAME, DOMAIN


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up the button platform."""
    consumables = entry.data.get(CONF_CONSUMABLES, [])
    entities = []

    for index, consumable in enumerate(consumables):
        entities.append(ConsumableReplacedButton(entry, consumable, index))

    async_add_entities(entities)


class ConsumableReplacedButton(ButtonEntity):
    """Button to mark consumable as replaced."""

    _attr_icon = "mdi:restore"
    _attr_has_entity_name = True

    def __init__(self, entry: ConfigEntry, consumable: dict, index: int) -> None:
        """Initialize the button."""
        self._entry = entry
        self._consumable = consumable
        self._index = index
        self._attr_unique_id = f"{entry.entry_id}_consumable_{index}_replaced"
        self._attr_device_info = {
            "identifiers": {(DOMAIN, entry.entry_id)},
            "name": entry.data[CONF_DEVICE_NAME],
            "manufacturer": "Consumable Tracker",
            "model": "Multi-Consumable Device",
        }
        self._attr_name = f"Mark {consumable[CONF_CONSUMABLE_NAME]} as replaced"

    async def async_press(self) -> None:
        """Handle the button press."""
        # Find the corresponding date entity and set it to today
        date_id = f"{self._entry.entry_id}_consumable_{self._index}_last_replaced"

        # Get all date entities
        entity_component = self.hass.data.get("entity_components", {}).get("date")
        if entity_component:
            for entity in entity_component.entities:
                if hasattr(entity, "unique_id") and entity.unique_id == date_id:
                    await entity.async_set_value(date.today())
                    break
