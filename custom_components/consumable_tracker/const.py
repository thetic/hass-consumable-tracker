"""Constants for the Consumable Tracker integration."""

DOMAIN = "consumable_tracker"

CONF_DEVICE_NAME = "device_name"
CONF_CONSUMABLES = "consumables"
CONF_CONSUMABLE_NAME = "consumable_name"
CONF_LIFETIME_DAYS = "lifetime_days"
CONF_WARNING_DAYS = "warning_days"
CONF_ICON_NORMAL = "icon_normal"
CONF_ICON_WARNING = "icon_warning"
CONF_ICON_OVERDUE = "icon_overdue"

DEFAULT_LIFETIME_DAYS = 90
DEFAULT_WARNING_DAYS = 15
DEFAULT_ICON_NORMAL = "mdi:gauge-full"
DEFAULT_ICON_WARNING = "mdi:gauge-low"
DEFAULT_ICON_OVERDUE = "mdi:gauge-empty"
