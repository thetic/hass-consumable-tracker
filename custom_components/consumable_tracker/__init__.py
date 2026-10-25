"""The Consumable Tracker integration."""

from __future__ import annotations

import logging

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers import device_registry as dr

from .const import CONF_DEVICE_ID, CONF_DEVICE_NAME, DOMAIN, MANUFACTURER, MODEL

_LOGGER = logging.getLogger(__name__)

# Sensors look up their date entities in the entity registry when they're added,
# so the date platform is set up before the platforms that depend on it.
DATE_PLATFORMS = ["date"]
DEPENDENT_PLATFORMS = ["sensor", "button"]
PLATFORMS = DATE_PLATFORMS + DEPENDENT_PLATFORMS

type ConsumableTrackerConfigEntry = ConfigEntry[dr.AnyDeviceEntry | None]


def is_consumable_tracker_device(device: dr.AnyDeviceEntry) -> bool:
    """Return whether a device was created by this integration."""
    return any(domain == DOMAIN for domain, _ in device.identifiers)


def _async_get_linked_device(
    hass: HomeAssistant, entry: ConsumableTrackerConfigEntry
) -> dr.AnyDeviceEntry | None:
    """Return the existing device the entry's entities attach to, if any."""
    if (device_id := entry.data.get(CONF_DEVICE_ID)) is None:
        return None

    device = dr.async_get(hass).async_get(device_id)
    if device is None:
        _LOGGER.warning(
            "Device %s for %s no longer exists, so its consumables are on their "
            "own device instead",
            device_id,
            entry.title,
        )
        return None
    if is_consumable_tracker_device(device):
        _LOGGER.warning(
            "%s can't attach its consumables to another Consumable Tracker device, "
            "so they are on their own device instead",
            entry.title,
        )
        return None
    return device


async def async_setup_entry(
    hass: HomeAssistant, entry: ConsumableTrackerConfigEntry
) -> bool:
    """Set up Consumable Tracker from a config entry."""
    hass.data.setdefault(DOMAIN, {})
    hass.data[DOMAIN][entry.entry_id] = entry.data

    device_registry = dr.async_get(hass)
    entry.runtime_data = _async_get_linked_device(hass, entry)

    if entry.runtime_data is None:
        # Create device
        device_registry.async_get_or_create(
            config_entry_id=entry.entry_id,
            identifiers={(DOMAIN, entry.entry_id)},
            name=entry.data[CONF_DEVICE_NAME],
            manufacturer=MANUFACTURER,
            model=MODEL,
        )

    await hass.config_entries.async_forward_entry_setups(entry, DATE_PLATFORMS)
    await hass.config_entries.async_forward_entry_setups(entry, DEPENDENT_PLATFORMS)

    if entry.runtime_data is not None:
        # The entities moved to the linked device, so remove the entry's own
        # device. This has to wait until they've moved, because removing a
        # device also removes the entities still on it.
        for device in dr.async_entries_for_config_entry(
            device_registry, entry.entry_id
        ):
            device_registry.async_remove_device(device.id)

    entry.async_on_unload(entry.add_update_listener(update_listener))

    return True


async def update_listener(
    hass: HomeAssistant, entry: ConsumableTrackerConfigEntry
) -> None:
    """Handle options update."""
    await hass.config_entries.async_reload(entry.entry_id)


async def async_unload_entry(
    hass: HomeAssistant, entry: ConsumableTrackerConfigEntry
) -> bool:
    """Unload a config entry."""
    unload_ok = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)

    if unload_ok:
        hass.data[DOMAIN].pop(entry.entry_id)

    return unload_ok
