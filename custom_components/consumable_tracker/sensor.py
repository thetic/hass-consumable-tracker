"""Sensor platform for Consumable Tracker."""

from __future__ import annotations

from datetime import date, datetime, timedelta

from homeassistant.components.sensor import SensorEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import Event, HomeAssistant, callback
from homeassistant.helpers import entity_registry as er
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.event import (
    EventStateChangedData,
    async_track_state_change_event,
)

from .const import (
    CONF_CONSUMABLE_NAME,
    CONF_CONSUMABLES,
    CONF_DEVICE_NAME,
    CONF_ICON_NORMAL,
    CONF_ICON_OVERDUE,
    CONF_ICON_WARNING,
    CONF_LIFETIME_DAYS,
    CONF_WARNING_DAYS,
    DOMAIN,
    MANUFACTURER,
    MODEL,
)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up the sensor platform."""
    consumables = entry.data.get(CONF_CONSUMABLES, [])
    entities = []

    for index, consumable in enumerate(consumables):
        entities.append(ConsumableTrackerSensor(entry, consumable, index))

    async_add_entities(entities)


class ConsumableTrackerSensor(SensorEntity):
    """Representation of a Consumable Tracker sensor."""

    _attr_native_unit_of_measurement = "days"
    _attr_has_entity_name = True

    def __init__(self, entry: ConfigEntry, consumable: dict, index: int) -> None:
        """Initialize the sensor."""
        self._entry = entry
        self._consumable = consumable
        self._index = index
        self._attr_unique_id = f"{entry.entry_id}_consumable_{index}"
        self._attr_device_info = {
            "identifiers": {(DOMAIN, entry.entry_id)},
            "name": entry.data[CONF_DEVICE_NAME],
            "manufacturer": MANUFACTURER,
            "model": MODEL,
        }
        self._attr_name = f"{consumable[CONF_CONSUMABLE_NAME]} days remaining"
        self._date_unique_id = f"{entry.entry_id}_consumable_{index}_last_replaced"
        self._datetime_entity_id: str | None = None
        self._unsub_state_change = None

    def _get_date_entity_id(self) -> str | None:
        """Get the date entity ID from the registry, caching the result."""
        if self._datetime_entity_id is None:
            entity_registry = er.async_get(self.hass)
            self._datetime_entity_id = entity_registry.async_get_entity_id(
                "date", DOMAIN, self._date_unique_id
            )
        return self._datetime_entity_id

    async def async_added_to_hass(self) -> None:
        """Set up entity ID for date entity and subscribe to state changes."""
        await super().async_added_to_hass()

        # Subscribe to state changes from the date entity (deferred lookup)
        @callback
        def async_subscribe_to_date_entity(_: object = None) -> None:
            """Subscribe to date entity once it's available."""
            date_entity_id = self._get_date_entity_id()
            if date_entity_id and not self._unsub_state_change:
                self._unsub_state_change = async_track_state_change_event(
                    self.hass, [date_entity_id], self._handle_date_state_change
                )

        # Try to subscribe now, or schedule for later
        async_subscribe_to_date_entity()

    async def async_will_remove_from_hass(self) -> None:
        """Unsubscribe from state changes when entity is removed."""
        if self._unsub_state_change:
            self._unsub_state_change()
            self._unsub_state_change = None

    @callback
    def _handle_date_state_change(self, event: Event[EventStateChangedData]) -> None:
        """Handle state changes from the date entity."""
        self.async_write_ha_state()

    def _get_last_replaced_date(self) -> date | None:
        """Get the last replaced date from the date entity."""
        date_entity_id = self._get_date_entity_id()
        if not date_entity_id:
            return None

        state = self.hass.states.get(date_entity_id)
        if state and state.state not in ["unknown", "unavailable"]:
            try:
                return date.fromisoformat(state.state)
            except (ValueError, TypeError):
                pass
        return None

    @property
    def native_value(self) -> int:
        """Return the state of the sensor."""
        # Get current consumable config
        consumables = self._entry.data.get(CONF_CONSUMABLES, [])
        if self._index >= len(consumables):
            return 0
        consumable = consumables[self._index]

        last_changed = self._get_last_replaced_date()
        if last_changed is None:
            return consumable[CONF_LIFETIME_DAYS]

        lifetime = consumable[CONF_LIFETIME_DAYS]
        days_since = (datetime.now().date() - last_changed).days
        days_remaining = max(lifetime - days_since, 0)
        return days_remaining

    @property
    def icon(self) -> str:
        """Return the icon based on days remaining."""
        consumables = self._entry.data.get(CONF_CONSUMABLES, [])
        if self._index >= len(consumables):
            return "mdi:help"
        consumable = consumables[self._index]

        days = self.native_value
        warning = consumable[CONF_WARNING_DAYS]

        if days == 0:
            return consumable[CONF_ICON_OVERDUE]
        elif days <= warning:
            return consumable[CONF_ICON_WARNING]
        else:
            return consumable[CONF_ICON_NORMAL]

    @property
    def extra_state_attributes(self) -> dict:
        """Return additional attributes."""
        consumables = self._entry.data.get(CONF_CONSUMABLES, [])
        if self._index >= len(consumables):
            return {}
        consumable = consumables[self._index]

        attrs = {
            "consumable_name": consumable[CONF_CONSUMABLE_NAME],
            "lifetime_days": consumable[CONF_LIFETIME_DAYS],
            "warning_days": consumable[CONF_WARNING_DAYS],
        }

        last_changed = self._get_last_replaced_date()
        if last_changed:
            attrs["last_changed"] = last_changed.isoformat()
            lifetime = consumable[CONF_LIFETIME_DAYS]
            next_replacement = last_changed + timedelta(days=lifetime)
            attrs["next_replacement"] = next_replacement.isoformat()

            days = self.native_value
            percentage = int((days / lifetime) * 100) if lifetime > 0 else 0
            attrs["percentage"] = percentage

        return attrs
