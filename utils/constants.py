# -----------------------------
# Configuration and constants
# -----------------------------
from utils.settings_manager import SettingsManager

# Load all settings from config.json
_config = SettingsManager.load_settings()


HMI_COLORS = _config.get("HMI_COLORS", {})
ICONS = _config.get("ICONS", {})
CONSTANTS = _config.get("CONSTANTS", {})

# Fallback  if file is empty or missing keys
if not CONSTANTS:
    print("Warning: CONSTANTS not loaded from config.json. Using minimal defaults.")
    CONSTANTS = {
        "UPDATE_INTERVAL_MS": 1000,
        "DEFAULT_SCREEN_SIZE": (480, 300),
        "MOTION_HISTORY_LENGTH": 50,
        "LOGS_HISTORY_LENGTH": 10,
        "DEFAULT_SERIAL_PORT": "/dev/ttyAMA0",
        "DEFAULT_BAUDRATE": 9600,
        "DEVICE_VERSION": {"control_station": "Raspberypi 1b+ v1.2"},
        "MESSAGE_TYPES": {
            "MOTION": "MOTION",
            "LOGS": "LOGS",
            "PERFORMANCE_STATUS": "PERFORMANCE_STATUS",
        },
        "USE_MOCK_DATA": False,
    }
