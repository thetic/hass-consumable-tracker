"""Tests for the Consumable Tracker button entity."""

from datetime import date

from freezegun import freeze_time
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


async def test_button_exists(hass: HomeAssistant) -> None:
    """Test button entity is created."""
    await setup_integration(hass)

    state = hass.states.get("button.test_device_mark_test_filter_as_replaced")
    assert state is not None


@freeze_time("2026-01-15")
async def test_button_press_sets_date_to_today(hass: HomeAssistant) -> None:
    """Test pressing button sets date entity to today."""
    await setup_integration(hass)

    # Get the date entity before pressing
    date_entity_id = "date.test_device_test_filter_last_replaced"
    date_entity = hass.data["entity_components"]["date"].get_entity(date_entity_id)
    assert date_entity is not None
    assert date_entity.native_value is None

    # Press the button
    await hass.services.async_call(
        "button",
        "press",
        {"entity_id": "button.test_device_mark_test_filter_as_replaced"},
        blocking=True,
    )
    await hass.async_block_till_done()

    # Check date was set to today
    assert date_entity.native_value == date(2026, 1, 15)


@freeze_time("2026-01-15")
async def test_button_press_updates_sensor(hass: HomeAssistant) -> None:
    """Test pressing button updates the sensor value."""
    await setup_integration(hass)

    # Get sensor - should show full lifetime initially
    sensor_entity_id = "sensor.test_device_test_filter_days_remaining"
    sensor_entity = hass.data["entity_components"]["sensor"].get_entity(
        sensor_entity_id
    )
    assert sensor_entity is not None
    assert sensor_entity.native_value == 90

    # Press the button
    await hass.services.async_call(
        "button",
        "press",
        {"entity_id": "button.test_device_mark_test_filter_as_replaced"},
        blocking=True,
    )
    await hass.async_block_till_done()

    # Sensor should now show 90 days (just replaced today)
    assert sensor_entity.native_value == 90
