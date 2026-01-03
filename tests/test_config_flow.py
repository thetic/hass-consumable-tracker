"""Tests for the Consumable Tracker config flow."""

from homeassistant import config_entries
from homeassistant.core import HomeAssistant
from homeassistant.data_entry_flow import FlowResultType

from custom_components.consumable_tracker.const import (
    CONF_CONSUMABLE_NAME,
    CONF_DEVICE_NAME,
    CONF_LIFETIME_DAYS,
    CONF_WARNING_DAYS,
    DOMAIN,
)


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
