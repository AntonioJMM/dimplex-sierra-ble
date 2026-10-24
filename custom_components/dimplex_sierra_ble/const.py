"""Constants for Dimplex Sierra BLE."""

from homeassistant.const import Platform

DOMAIN = "dimplex_sierra_ble"
PRODUCT_ID = "0fsaqmtu"
PRODUCT_NAME = "Dimplex Sierra 48"
MODEL = "SIL48"
MANUFACTURER = "Dimplex"
FD50_SERVICE_UUID = "0000fd50-0000-1000-8000-00805f9b34fb"
TUYA_MANUFACTURER_ID = 0x07D0

PLATFORMS = [
    Platform.BINARY_SENSOR,
    Platform.CLIMATE,
    Platform.NUMBER,
    Platform.SELECT,
    Platform.SENSOR,
    Platform.SWITCH,
]

DP_POWER = 101
DP_TARGET_TEMPERATURE = 102
DP_CURRENT_TEMPERATURE = 103
DP_HEATER_DISABLED = 104
DP_HEAT = 105
DP_FLAME_COLOR = 106
DP_FLAME_BRIGHTNESS = 107
DP_SOUND = 108
DP_EMBER_COLOR = 109
DP_EMBER_BRIGHTNESS = 110
DP_TIMER = 111
DP_TEMPERATURE_UNIT = 112

# The target DP uses the displayed value directly. Value 28 is the firmware's
# continuous-heat setting (shown as "ON" on the appliance).
TARGET_TEMPERATURES_C = tuple(range(18, 28))
CONTINUOUS_HEAT_VALUE = 28
