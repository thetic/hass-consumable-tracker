"""Tests for the Consumable Tracker sensor entity."""

from datetime import date, timedelta

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


async def test_sensor_initial_state(hass: HomeAssistant) -> None:
    """Test sensor shows full lifetime when no date is set."""
    await setup_integration(hass)

    state = hass.states.get("sensor.test_device_test_filter_days_remaining")
    assert state is not None
    assert state.state == "90"


async def test_sensor_with_date_set(hass: HomeAssistant) -> None:
    """Test sensor calculates days remaining when date is set."""
    await setup_integration(hass)

    # Set the date entity to 30 days ago
    today = date.today()
    thirty_days_ago = today - timedelta(days=30)

    hass.states.async_set(
        "date.test_device_test_filter_last_replaced",
        thirty_days_ago.isoformat(),
    )
    await hass.async_block_till_done()

    # Get the sensor entity directly to check its native_value
    sensor_entity_id = "sensor.test_device_test_filter_days_remaining"
    entity = hass.data["entity_components"]["sensor"].get_entity(sensor_entity_id)
    assert entity is not None
    assert entity.native_value == 60  # 90 - 30 = 60 days remaining


@freeze_time("2026-01-15")
async def test_sensor_days_remaining_calculation(hass: HomeAssistant) -> None:
    """Test sensor correctly calculates days remaining."""
    await setup_integration(hass)

    # Set the date entity to a specific date
    hass.states.async_set(
        "date.test_device_test_filter_last_replaced",
        "2026-01-01",  # 14 days ago from frozen time
    )
    await hass.async_block_till_done()

    sensor_entity_id = "sensor.test_device_test_filter_days_remaining"
    entity = hass.data["entity_components"]["sensor"].get_entity(sensor_entity_id)
    assert entity is not None
    assert entity.native_value == 76  # 90 - 14 = 76 days remaining


@freeze_time("2026-01-15")
async def test_sensor_icon_normal(hass: HomeAssistant) -> None:
    """Test sensor shows normal icon when plenty of days remaining."""
    await setup_integration(hass)

    # Set date to recent (many days remaining)
    hass.states.async_set(
        "date.test_device_test_filter_last_replaced",
        "2026-01-10",  # 5 days ago, 85 days remaining
    )
    await hass.async_block_till_done()

    sensor_entity_id = "sensor.test_device_test_filter_days_remaining"
    entity = hass.data["entity_components"]["sensor"].get_entity(sensor_entity_id)
    assert entity is not None
    assert entity.icon == DEFAULT_ICON_NORMAL


@freeze_time("2026-01-15")
async def test_sensor_icon_warning(hass: HomeAssistant) -> None:
    """Test sensor shows warning icon when within warning threshold."""
    await setup_integration(hass)

    # Set date so we're in warning zone (15 days or less remaining)
    # 90 - 80 = 10 days remaining (within 15 day warning)
    hass.states.async_set(
        "date.test_device_test_filter_last_replaced",
        "2025-10-27",  # 80 days ago
    )
    await hass.async_block_till_done()

    sensor_entity_id = "sensor.test_device_test_filter_days_remaining"
    entity = hass.data["entity_components"]["sensor"].get_entity(sensor_entity_id)
    assert entity is not None
    assert entity.native_value == 10
    assert entity.icon == DEFAULT_ICON_WARNING


@freeze_time("2026-01-15")
async def test_sensor_icon_overdue(hass: HomeAssistant) -> None:
    """Test sensor shows overdue icon when no days remaining."""
    await setup_integration(hass)

    # Set date so consumable is overdue (more than 90 days ago)
    hass.states.async_set(
        "date.test_device_test_filter_last_replaced",
        "2025-10-01",  # 106 days ago
    )
    await hass.async_block_till_done()

    sensor_entity_id = "sensor.test_device_test_filter_days_remaining"
    entity = hass.data["entity_components"]["sensor"].get_entity(sensor_entity_id)
    assert entity is not None
    assert entity.native_value == 0
    assert entity.icon == DEFAULT_ICON_OVERDUE


@freeze_time("2026-01-15")
async def test_sensor_extra_attributes(hass: HomeAssistant) -> None:
    """Test sensor extra attributes when date is set."""
    await setup_integration(hass)

    hass.states.async_set(
        "date.test_device_test_filter_last_replaced",
        "2026-01-01",  # 14 days ago
    )
    await hass.async_block_till_done()

    sensor_entity_id = "sensor.test_device_test_filter_days_remaining"
    entity = hass.data["entity_components"]["sensor"].get_entity(sensor_entity_id)
    assert entity is not None

    attrs = entity.extra_state_attributes
    assert attrs["consumable_name"] == "Test Filter"
    assert attrs["lifetime_days"] == 90
    assert attrs["warning_days"] == 15
    assert attrs["last_changed"] == "2026-01-01"
    assert attrs["next_replacement"] == "2026-04-01"  # 90 days after 2026-01-01
    assert attrs["percentage"] == 84  # 76/90 * 100 = 84%


async def test_sensor_invalid_date_state(hass: HomeAssistant) -> None:
    """Test sensor handles invalid date state gracefully."""
    await setup_integration(hass)

    # Set an invalid date value
    hass.states.async_set(
        "date.test_device_test_filter_last_replaced",
        "not-a-date",
    )
    await hass.async_block_till_done()

    sensor_entity_id = "sensor.test_device_test_filter_days_remaining"
    entity = hass.data["entity_components"]["sensor"].get_entity(sensor_entity_id)
    assert entity is not None
    # Should fall back to full lifetime
    assert entity.native_value == 90
