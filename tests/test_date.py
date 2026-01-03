"""Tests for the Consumable Tracker date entity."""

from datetime import date

from homeassistant.core import HomeAssistant, State
from pytest_homeassistant_custom_component.common import (
    MockConfigEntry,
    mock_restore_cache,
)

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


def create_config_entry(hass: HomeAssistant) -> MockConfigEntry:
    """Create a config entry."""
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
    return entry


async def test_date_entity_exists(hass: HomeAssistant) -> None:
    """Test date entity is created."""
    entry = create_config_entry(hass)
    await hass.config_entries.async_setup(entry.entry_id)
    await hass.async_block_till_done()

    state = hass.states.get("date.test_device_test_filter_last_replaced")
    assert state is not None


async def test_date_entity_initial_state(hass: HomeAssistant) -> None:
    """Test date entity starts with no value."""
    entry = create_config_entry(hass)
    await hass.config_entries.async_setup(entry.entry_id)
    await hass.async_block_till_done()

    date_entity_id = "date.test_device_test_filter_last_replaced"
    entity = hass.data["entity_components"]["date"].get_entity(date_entity_id)
    assert entity is not None
    assert entity.native_value is None


async def test_date_entity_set_value(hass: HomeAssistant) -> None:
    """Test setting a date value."""
    entry = create_config_entry(hass)
    await hass.config_entries.async_setup(entry.entry_id)
    await hass.async_block_till_done()

    # Set date via service
    await hass.services.async_call(
        "date",
        "set_value",
        {
            "entity_id": "date.test_device_test_filter_last_replaced",
            "date": "2026-01-01",
        },
        blocking=True,
    )
    await hass.async_block_till_done()

    date_entity_id = "date.test_device_test_filter_last_replaced"
    entity = hass.data["entity_components"]["date"].get_entity(date_entity_id)
    assert entity is not None
    assert entity.native_value == date(2026, 1, 1)


async def test_date_entity_restores_state(hass: HomeAssistant) -> None:
    """Test date entity restores previous state."""
    mock_restore_cache(
        hass,
        [
            State(
                "date.test_device_test_filter_last_replaced",
                "2025-12-25",
            ),
        ],
    )

    entry = create_config_entry(hass)
    await hass.config_entries.async_setup(entry.entry_id)
    await hass.async_block_till_done()

    date_entity_id = "date.test_device_test_filter_last_replaced"
    entity = hass.data["entity_components"]["date"].get_entity(date_entity_id)
    assert entity is not None
    assert entity.native_value == date(2025, 12, 25)


async def test_date_entity_handles_invalid_restore_state(hass: HomeAssistant) -> None:
    """Test date entity handles invalid restored state."""
    mock_restore_cache(
        hass,
        [
            State(
                "date.test_device_test_filter_last_replaced",
                "not-a-valid-date",
            ),
        ],
    )

    entry = create_config_entry(hass)
    await hass.config_entries.async_setup(entry.entry_id)
    await hass.async_block_till_done()

    date_entity_id = "date.test_device_test_filter_last_replaced"
    entity = hass.data["entity_components"]["date"].get_entity(date_entity_id)
    assert entity is not None
    assert entity.native_value is None


async def test_date_entity_handles_unknown_restore_state(hass: HomeAssistant) -> None:
    """Test date entity handles unknown restored state."""
    mock_restore_cache(
        hass,
        [
            State(
                "date.test_device_test_filter_last_replaced",
                "unknown",
            ),
        ],
    )

    entry = create_config_entry(hass)
    await hass.config_entries.async_setup(entry.entry_id)
    await hass.async_block_till_done()

    date_entity_id = "date.test_device_test_filter_last_replaced"
    entity = hass.data["entity_components"]["date"].get_entity(date_entity_id)
    assert entity is not None
    assert entity.native_value is None
