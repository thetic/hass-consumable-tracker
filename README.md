# Consumable Tracker for Home Assistant

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

## Automation Examples

### Notify when filter needs replacement

```yaml
automation:
  - alias: "Furnace filter warning"
    trigger:
      - platform: numeric_state
        entity_id: sensor.hvac_system_furnace_filter_days_remaining
        below: 15
    action:
      - service: notify.mobile_app
        data:
          title: "Filter Replacement Needed"
          message: "Furnace filter has {{ states('sensor.hvac_system_furnace_filter_days_remaining') }} days remaining"
```

### Dashboard card example

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
