"""Date platform for Consumable Tracker."""

from __future__ import annotations

from datetime import date
from typing import TYPE_CHECKING

from homeassistant.components.date import DateEntity
from homeassistant.helpers.entity import EntityCategory
from homeassistant.helpers.restore_state import RestoreEntity

if TYPE_CHECKING:
    from homeassistant.core import HomeAssistant
    from homeassistant.helpers.entity_platform import AddEntitiesCallback

    from . import ConsumableTrackerConfigEntry

from .const import (
    CONF_CONSUMABLE_NAME,
    CONF_CONSUMABLES,
)
from .entity import ConsumableTrackerEntity


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConsumableTrackerConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up the date platform."""
    consumables = entry.data.get(CONF_CONSUMABLES, [])
    entities = []

    for index, consumable in enumerate(consumables):
        entities.append(ConsumableLastReplacedDate(entry, consumable, index))

    async_add_entities(entities)


class ConsumableLastReplacedDate(ConsumableTrackerEntity, RestoreEntity, DateEntity):
    """Date entity for when consumable was last replaced."""

    _attr_entity_category = EntityCategory.DIAGNOSTIC

    def __init__(
        self, entry: ConsumableTrackerConfigEntry, consumable: dict, index: int
    ) -> None:
        """Initialize the date entity."""
        super().__init__(entry, consumable, index)
        self._attr_unique_id = f"{entry.entry_id}_consumable_{index}_last_replaced"
        self._attr_name = f"{consumable[CONF_CONSUMABLE_NAME]} last replaced"
        self._attr_native_value = None

    async def async_added_to_hass(self) -> None:
        """Restore last state."""
        await super().async_added_to_hass()

        last_state = await self.async_get_last_state()
        if last_state and last_state.state not in ["unknown", "unavailable"]:
            try:
                # Parse the state as a date
                self._attr_native_value = date.fromisoformat(last_state.state)
            except (ValueError, TypeError):
                self._attr_native_value = None

    async def async_set_value(self, value: date) -> None:
        """Update the date."""
        self._attr_native_value = value
        self.async_write_ha_state()
