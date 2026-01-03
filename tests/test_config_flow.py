"""Tests for the Consumable Tracker config flow."""

import pytest
from homeassistant import config_entries
from homeassistant.core import HomeAssistant
from homeassistant.data_entry_flow import FlowResultType
from pytest_homeassistant_custom_component.common import MockConfigEntry

from custom_components.consumable_tracker.const import (
    CONF_CONSUMABLE_NAME,
    CONF_CONSUMABLES,
    CONF_DEVICE_NAME,
    CONF_LIFETIME_DAYS,
    CONF_WARNING_DAYS,
    DOMAIN,
)


@pytest.fixture
async def config_entry(hass: HomeAssistant) -> MockConfigEntry:
    """Create a config entry for testing options flow."""
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
                },
            ],
        },
        unique_id="Test Device",
    )
    entry.add_to_hass(hass)
    return entry


async def test_user_flow_creates_entry(hass: HomeAssistant) -> None:
    """Test the full user config flow."""
    result = await hass.config_entries.flow.async_init(
        DOMAIN, context={"source": config_entries.SOURCE_USER}
    )

    assert result["type"] is FlowResultType.FORM
    assert result["step_id"] == "user"

    result = await hass.config_entries.flow.async_configure(
        result["flow_id"],
        {CONF_DEVICE_NAME: "Test Device"},
    )

    assert result["type"] is FlowResultType.FORM
    assert result["step_id"] == "add_consumable"

    result = await hass.config_entries.flow.async_configure(
        result["flow_id"],
        {
            CONF_CONSUMABLE_NAME: "Test Filter",
            CONF_LIFETIME_DAYS: 90,
            CONF_WARNING_DAYS: 15,
            "add_another": False,
        },
    )

    assert result["type"] is FlowResultType.CREATE_ENTRY
    assert result["title"] == "Test Device"
    assert result["data"][CONF_DEVICE_NAME] == "Test Device"
    assert len(result["data"]["consumables"]) == 1
    assert result["data"]["consumables"][0][CONF_CONSUMABLE_NAME] == "Test Filter"


async def test_user_flow_add_multiple_consumables(hass: HomeAssistant) -> None:
    """Test adding multiple consumables in config flow."""
    result = await hass.config_entries.flow.async_init(
        DOMAIN, context={"source": config_entries.SOURCE_USER}
    )

    result = await hass.config_entries.flow.async_configure(
        result["flow_id"],
        {CONF_DEVICE_NAME: "Multi Device"},
    )

    result = await hass.config_entries.flow.async_configure(
        result["flow_id"],
        {
            CONF_CONSUMABLE_NAME: "Filter 1",
            CONF_LIFETIME_DAYS: 30,
            CONF_WARNING_DAYS: 7,
            "add_another": True,
        },
    )

    assert result["type"] is FlowResultType.FORM
    assert result["step_id"] == "add_consumable"

    result = await hass.config_entries.flow.async_configure(
        result["flow_id"],
        {
            CONF_CONSUMABLE_NAME: "Filter 2",
            CONF_LIFETIME_DAYS: 60,
            CONF_WARNING_DAYS: 10,
            "add_another": False,
        },
    )

    assert result["type"] is FlowResultType.CREATE_ENTRY
    assert len(result["data"]["consumables"]) == 2
    assert result["data"]["consumables"][0][CONF_CONSUMABLE_NAME] == "Filter 1"
    assert result["data"]["consumables"][1][CONF_CONSUMABLE_NAME] == "Filter 2"


async def test_options_flow_init(
    hass: HomeAssistant, config_entry: config_entries.ConfigEntry
) -> None:
    """Test the options flow init step."""
    result = await hass.config_entries.options.async_init(config_entry.entry_id)

    assert result["type"] is FlowResultType.FORM
    assert result["step_id"] == "init"


async def test_options_flow_add_consumable(
    hass: HomeAssistant, config_entry: config_entries.ConfigEntry
) -> None:
    """Test adding a consumable via options flow."""
    result = await hass.config_entries.options.async_init(config_entry.entry_id)

    result = await hass.config_entries.options.async_configure(
        result["flow_id"],
        {"action": "add"},
    )

    assert result["type"] is FlowResultType.FORM
    assert result["step_id"] == "add_consumable"

    result = await hass.config_entries.options.async_configure(
        result["flow_id"],
        {
            CONF_CONSUMABLE_NAME: "New Filter",
            CONF_LIFETIME_DAYS: 60,
            CONF_WARNING_DAYS: 10,
        },
    )

    assert result["type"] is FlowResultType.FORM
    assert result["step_id"] == "init"

    result = await hass.config_entries.options.async_configure(
        result["flow_id"],
        {"action": "done"},
    )

    assert result["type"] is FlowResultType.CREATE_ENTRY
    assert len(config_entry.data[CONF_CONSUMABLES]) == 2


async def test_options_flow_edit_consumable(
    hass: HomeAssistant, config_entry: config_entries.ConfigEntry
) -> None:
    """Test editing a consumable via options flow."""
    result = await hass.config_entries.options.async_init(config_entry.entry_id)

    result = await hass.config_entries.options.async_configure(
        result["flow_id"],
        {"action": "edit"},
    )

    assert result["type"] is FlowResultType.FORM
    assert result["step_id"] == "select_consumable"

    result = await hass.config_entries.options.async_configure(
        result["flow_id"],
        {"consumable": "0"},
    )

    assert result["type"] is FlowResultType.FORM
    assert result["step_id"] == "edit_consumable"

    result = await hass.config_entries.options.async_configure(
        result["flow_id"],
        {
            CONF_CONSUMABLE_NAME: "Updated Filter",
            CONF_LIFETIME_DAYS: 120,
            CONF_WARNING_DAYS: 20,
        },
    )

    assert result["type"] is FlowResultType.FORM
    assert result["step_id"] == "init"

    result = await hass.config_entries.options.async_configure(
        result["flow_id"],
        {"action": "done"},
    )

    assert result["type"] is FlowResultType.CREATE_ENTRY
    assert (
        config_entry.data[CONF_CONSUMABLES][0][CONF_CONSUMABLE_NAME] == "Updated Filter"
    )
    assert config_entry.data[CONF_CONSUMABLES][0][CONF_LIFETIME_DAYS] == 120


async def test_options_flow_delete_consumable(
    hass: HomeAssistant, config_entry: config_entries.ConfigEntry
) -> None:
    """Test deleting a consumable via options flow."""
    result = await hass.config_entries.options.async_init(config_entry.entry_id)

    result = await hass.config_entries.options.async_configure(
        result["flow_id"],
        {"action": "delete"},
    )

    assert result["type"] is FlowResultType.FORM
    assert result["step_id"] == "delete_consumable"

    result = await hass.config_entries.options.async_configure(
        result["flow_id"],
        {"consumable": "0"},
    )

    assert result["type"] is FlowResultType.FORM
    assert result["step_id"] == "init"

    result = await hass.config_entries.options.async_configure(
        result["flow_id"],
        {"action": "done"},
    )

    assert result["type"] is FlowResultType.CREATE_ENTRY
    assert len(config_entry.data[CONF_CONSUMABLES]) == 0
