"""Tests for the Consumable Tracker integration initialization."""

from homeassistant.core import HomeAssistant
from pytest_homeassistant_custom_component.common import MockConfigEntry

from custom_components.consumable_tracker.const import (
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
    DOMAIN,
)


async def setup_integration(hass: HomeAssistant) -> MockConfigEntry:
    """Set up the integration with a config entry."""
    entry = MockConfigEntry(
        version=2,
        domain=DOMAIN,
        title="Test Device",
        data={
            CONF_DEVICE_NAME: "Test Device",
            CONF_CONSUMABLES: [
                {
                    CONF_CONSUMABLE_NAME: "Test Filter",
                    CONF_LIFETIME_DAYS: 90,
                    CONF_WARNING_DAYS: 15,
                    CONF_ICON_NORMAL: DEFAULT_ICON_NORMAL,
                    CONF_ICON_WARNING: DEFAULT_ICON_WARNING,
                    CONF_ICON_OVERDUE: DEFAULT_ICON_OVERDUE,
                },
            ],
        },
        unique_id="test_device",
    )
    entry.add_to_hass(hass)
    await hass.config_entries.async_setup(entry.entry_id)
    await hass.async_block_till_done()
    return entry


async def test_unload_entry(hass: HomeAssistant) -> None:
    """Test that unloading a config entry removes entities and data."""
    entry = await setup_integration(hass)

    # Verify entities are created
    assert hass.states.get("sensor.test_device_test_filter_days_remaining") is not None
    assert hass.states.get("date.test_device_test_filter_last_replaced") is not None
    assert (
        hass.states.get("button.test_device_mark_test_filter_as_replaced") is not None
    )

    # Verify data is stored
    assert entry.entry_id in hass.data[DOMAIN]

    # Unload the entry
    assert await hass.config_entries.async_unload(entry.entry_id)
    await hass.async_block_till_done()

    # Verify entities are unavailable (unloaded)
    state = hass.states.get("sensor.test_device_test_filter_days_remaining")
    assert state is not None
    assert state.state == "unavailable"

    state = hass.states.get("date.test_device_test_filter_last_replaced")
    assert state is not None
    assert state.state == "unavailable"

    state = hass.states.get("button.test_device_mark_test_filter_as_replaced")
    assert state is not None
    assert state.state == "unavailable"

    # Verify data is cleaned up
    assert entry.entry_id not in hass.data[DOMAIN]
