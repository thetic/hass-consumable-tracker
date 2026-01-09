# Consumable Tracker for Home Assistant

[![CI](https://github.com/thetic/hass-consumable-tracker/actions/workflows/ci.yml/badge.svg)](https://github.com/thetic/hass-consumable-tracker/actions/workflows/ci.yml)
[![codecov](https://codecov.io/gh/thetic/hass-consumable-tracker/graph/badge.svg)](https://codecov.io/gh/thetic/hass-consumable-tracker)
[![hacs_badge](https://img.shields.io/badge/HACS-Custom-41BDF5.svg)](https://github.com/hacs/integration)
[![License: GPL v3](https://img.shields.io/badge/License-GPLv3-blue.svg)](https://www.gnu.org/licenses/gpl-3.0)

A Home Assistant custom integration to track consumable items that need periodic replacement, such as filters, pads, cartridges, and other maintenance items.

## Features

- **Multi-consumable tracking**: Track multiple consumables per device (e.g., HVAC system with furnace filter, humidifier pad, and UV bulb)
- **Days remaining sensor**: Shows how many days until replacement is needed
- **Warning thresholds**: Configurable warning period before replacement is due
- **Dynamic icons**: Icons change based on status (normal, warning, overdue)
- **Mark as replaced button**: One-click button to reset the replacement date
- **Date entity**: View and manually edit the last replacement date
- **State persistence**: Maintains tracking data across Home Assistant restarts

## Installation

### HACS (Recommended)

1. Open HACS in Home Assistant
2. Click the three dots in the top right corner
3. Select "Custom repositories"
4. Add `https://github.com/thetic/hass-consumable-tracker` with category "Integration"
5. Click "Install"
6. Restart Home Assistant

### Manual Installation

1. Download the `consumable_tracker` folder from this repository
2. Copy it to your `config/custom_components/` directory
3. Restart Home Assistant

## Configuration

1. Go to **Settings** > **Devices & Services**
2. Click **Add Integration**
3. Search for "Consumable Tracker"
4. Enter a device name (e.g., "HVAC System")
5. Add your first consumable:
   - **Name**: e.g., "Furnace Filter"
   - **Lifetime (days)**: How long the consumable lasts (1-730 days)
   - **Warning threshold (days)**: When to start warning (0-365 days)
   - **Icons** (optional): Custom icons for normal, warning, and overdue states
6. Optionally add more consumables to the same device
7. Click **Submit**

### Managing Consumables

After setup, you can add, edit, or delete consumables:

1. Go to **Settings** > **Devices & Services**
2. Find your Consumable Tracker device
3. Click **Configure**
4. Choose to add, edit, or delete consumables

## Entities Created

For each consumable, the integration creates three entities:

| Entity Type | Purpose | Example |
|-------------|---------|---------|
| Sensor | Shows days remaining | `sensor.hvac_system_furnace_filter_days_remaining` |
| Button | Mark as replaced | `button.hvac_system_mark_furnace_filter_as_replaced` |
| Date | Last replacement date | `date.hvac_system_furnace_filter_last_replaced` |

### Sensor Attributes

The sensor includes additional attributes:
- `consumable_name`: Name of the consumable
- `lifetime_days`: Configured lifetime
- `warning_days`: Warning threshold
- `last_changed`: Date of last replacement
- `next_replacement`: Calculated next replacement date
- `percentage`: Percentage of lifetime remaining

## Example Use Cases

- **HVAC Systems**: Furnace filters, humidifier pads, air intake filters
- **Water Filtration**: Reverse osmosis filters, UV bulbs, sediment cartridges
- **Kitchen Appliances**: Refrigerator water filters, coffee maker cartridges
- **Medical Equipment**: CPAP filters, nebulizer supplies
- **Vehicles**: Cabin air filters, windshield wipers

## Blueprints

### Low/Depleted Notification

This integration includes a blueprint that creates persistent notifications when consumables need attention:

[![Open your Home Assistant instance and show the blueprint import dialog with a specific blueprint pre-filled.](https://my.home-assistant.io/badges/blueprint_import.svg)](https://my.home-assistant.io/redirect/blueprint_import/?blueprint_url=https%3A%2F%2Fgithub.com%2Fthetic%2Fhass-consumable-tracker%2Fblob%2Fmain%2Fblueprints%2Fautomation%2Fconsumable_notification.yaml)

Click the badge above to import, then create an automation from the blueprint for each consumable you want to monitor.

<details>
<summary>Manual import instructions</summary>

1. Go to **Settings** > **Automations & Scenes** > **Blueprints**
2. Click **Import Blueprint**
3. Enter: `https://github.com/thetic/hass-consumable-tracker/blob/main/blueprints/automation/consumable_notification.yaml`
4. Create an automation from the blueprint for each consumable you want to monitor

</details>

The blueprint will:
- Show a warning notification when days remaining reaches the warning threshold
- Update to an urgent notification when the consumable is fully depleted
- Automatically dismiss the notification when the consumable is replaced

## Dashboard Example

```yaml
type: entities
title: HVAC Consumables
entities:
  - entity: sensor.hvac_system_furnace_filter_days_remaining
  - entity: button.hvac_system_mark_furnace_filter_as_replaced
  - entity: sensor.hvac_system_humidifier_pad_days_remaining
  - entity: button.hvac_system_mark_humidifier_pad_as_replaced
```

## License

This project is licensed under the GNU General Public License v3.0 - see the [LICENSE](LICENSE) file for details.
