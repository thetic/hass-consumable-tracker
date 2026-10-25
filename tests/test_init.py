"""Tests for the Consumable Tracker integration initialization."""

import pytest
from homeassistant.core import HomeAssistant
from homeassistant.helpers import device_registry as dr
from homeassistant.helpers import entity_registry as er
from pytest_homeassistant_custom_component.common import MockConfigEntry

from custom_components.consumable_tracker.const import (
    CONF_CONSUMABLE_NAME,
    CONF_CONSUMABLES,
    CONF_DEVICE_ID,
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


def make_entry(hass: HomeAssistant, **data: object) -> MockConfigEntry:
    """Add a config entry with one consumable and the given extra data."""
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
            **data,
        },
        unique_id="test_device",
    )
    entry.add_to_hass(hass)
    return entry


def make_other_device(hass: HomeAssistant) -> dr.DeviceEntry:
    """Create a device owned by another integration."""
    other_entry = MockConfigEntry(domain="other")
    other_entry.add_to_hass(hass)
    return dr.async_get(hass).async_get_or_create(
        config_entry_id=other_entry.entry_id,
        identifiers={("other", "purifier")},
        name="Air Purifier",
    )


def entity_device_ids(hass: HomeAssistant, entry: MockConfigEntry) -> set[str | None]:
    """Return the device IDs of the entry's entities."""
    return {
        entity.device_id
        for entity in er.async_entries_for_config_entry(
            er.async_get(hass), entry.entry_id
        )
    }


def own_device(hass: HomeAssistant, entry: MockConfigEntry) -> dr.DeviceEntry | None:
    """Return the device the integration creates for the entry, if it exists."""
    devices = dr.async_entries_for_config_entry(dr.async_get(hass), entry.entry_id)
    assert len(devices) <= 1
    return devices[0] if devices else None


async def test_attaches_to_existing_device(hass: HomeAssistant) -> None:
    """Test that entities attach to the selected device of another integration."""
    other_device = make_other_device(hass)
    entry = make_entry(hass, **{CONF_DEVICE_ID: other_device.id})

    await hass.config_entries.async_setup(entry.entry_id)
    await hass.async_block_till_done()

    assert entity_device_ids(hass, entry) == {other_device.id}
    assert own_device(hass, entry) is None
    # The other integration still owns its device
    device = dr.async_get(hass).async_get(other_device.id)
    assert device is not None
    assert device.config_entry_id == other_device.config_entry_id
    # Entity names come from the device they're attached to
    assert hass.states.get("sensor.air_purifier_test_filter_days_remaining") is not None


async def test_moves_to_existing_device(hass: HomeAssistant) -> None:
    """Test that an entry with its own device moves to a selected device."""
    other_device = make_other_device(hass)
    entry = make_entry(hass)
    await hass.config_entries.async_setup(entry.entry_id)
    await hass.async_block_till_done()

    original_device = own_device(hass, entry)
    assert original_device is not None
    assert entity_device_ids(hass, entry) == {original_device.id}

    await hass.services.async_call(
        "date",
        "set_value",
        {
            "entity_id": "date.test_device_test_filter_last_replaced",
            "date": "2026-01-01",
        },
        blocking=True,
    )

    hass.config_entries.async_update_entry(
        entry, data={**entry.data, CONF_DEVICE_ID: other_device.id}
    )
    await hass.async_block_till_done()

    assert entity_device_ids(hass, entry) == {other_device.id}
    assert own_device(hass, entry) is None
    # The entities kept their IDs and state when they moved
    state = hass.states.get("date.test_device_test_filter_last_replaced")
    assert state is not None
    assert state.state == "2026-01-01"


async def test_detaches_from_existing_device(hass: HomeAssistant) -> None:
    """Test that clearing the selected device gives entities their own device."""
    other_device = make_other_device(hass)
    entry = make_entry(hass, **{CONF_DEVICE_ID: other_device.id})
    await hass.config_entries.async_setup(entry.entry_id)
    await hass.async_block_till_done()

    hass.config_entries.async_update_entry(
        entry,
        data={k: v for k, v in entry.data.items() if k != CONF_DEVICE_ID},
    )
    await hass.async_block_till_done()

    device = own_device(hass, entry)
    assert device is not None
    assert device.name == "Test Device"
    assert entity_device_ids(hass, entry) == {device.id}


async def test_missing_device_falls_back_to_own_device(
    hass: HomeAssistant, caplog: pytest.LogCaptureFixture
) -> None:
    """Test that entities get their own device if the selected one is gone."""
    entry = make_entry(hass, **{CONF_DEVICE_ID: "missing"})

    await hass.config_entries.async_setup(entry.entry_id)
    await hass.async_block_till_done()

    device = own_device(hass, entry)
    assert device is not None
    assert entity_device_ids(hass, entry) == {device.id}
    assert "Device missing for Test Device no longer exists" in caplog.text


async def test_consumable_tracker_device_is_not_attached(
    hass: HomeAssistant, caplog: pytest.LogCaptureFixture
) -> None:
    """Test that entities don't attach to another Consumable Tracker device."""
    other_entry = MockConfigEntry(domain=DOMAIN)
    other_entry.add_to_hass(hass)
    tracker_device = dr.async_get(hass).async_get_or_create(
        config_entry_id=other_entry.entry_id,
        identifiers={(DOMAIN, other_entry.entry_id)},
        name="Other Tracker",
    )
    entry = make_entry(hass, **{CONF_DEVICE_ID: tracker_device.id})

    await hass.config_entries.async_setup(entry.entry_id)
    await hass.async_block_till_done()

    device = own_device(hass, entry)
    assert device is not None
    assert entity_device_ids(hass, entry) == {device.id}
    assert "can't attach its consumables to another Consumable Tracker" in caplog.text
