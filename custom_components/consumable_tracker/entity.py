"""Base entity for Consumable Tracker."""

from __future__ import annotations

from typing import TYPE_CHECKING

from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.entity import Entity

from .const import CONF_DEVICE_NAME, DOMAIN, MANUFACTURER, MODEL

if TYPE_CHECKING:
    from . import ConsumableTrackerConfigEntry


class ConsumableTrackerEntity(Entity):
    """An entity for one consumable of a Consumable Tracker entry."""

    _attr_has_entity_name = True

    def __init__(
        self,
        entry: ConsumableTrackerConfigEntry,
        consumable: dict,
        index: int,
    ) -> None:
        """Initialize the entity and attach it to its device."""
        self._entry = entry
        self._consumable = consumable
        self._index = index
        if entry.runtime_data is not None:
            # Link to the existing device without adding this config entry to it
            self.device_entry = entry.runtime_data
        else:
            self._attr_device_info = DeviceInfo(
                identifiers={(DOMAIN, entry.entry_id)},
                name=entry.data[CONF_DEVICE_NAME],
                manufacturer=MANUFACTURER,
                model=MODEL,
            )
