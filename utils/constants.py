# -----------------------------
# Configuration and constants
# -----------------------------
from utils.settings_manager import SettingsManager
from pathlib import Path
import random

# Default Configuration
DEFAULT_CONFIG = {
    "HMI_COLORS": {
        "BACKGROUND": "#2C3E50",
        "FOREGROUND": "#ECF0F1",
        "ACCENT": "#E74C3C",
        "PRIMARY": "#2ECC71",
        "DANGER": "#C0392B",
        "INFO": "#3498DB",
        "TEXT_BRIGHT": "#FFFFFF",
        "TEXT_DIM": "#BDC3C7",
    },
    "ICONS": {"logo": "assets/graph.png"},
    "CONSTANTS": {
        "UPDATE_INTERVAL_MS": 1000,
        "IS_FULLSCREEN": False,
        "MOTION_HISTORY_LENGTH": 50,
        "DEFAULT_SERIAL_PORT": "/dev/ttyAMA0",
        "DEFAULT_BAUDRATE": 9600,
        "LOGS_HISTORY_LENGTH": 10,
        "DEFAULT_SCREEN_SIZE": [480, 300],
        "DEVICE_VERSION": {"control_station": "Raspberypi 1b+ v1.2"},
        "MESSAGE_TYPES": {
            "MOTION": "MOTION",
            "LOGS": "LOGS",
            "PERFORMANCE_STATUS": "PERFORMANCE_STATUS",
        },
        "transmitter_status": {
            "cpu": 0.0,
            "ram": 0.0,
            "disk": 0.0,
            "net_up": 0.0,
            "net_down": 0.0,
            "version": "Raspberypi 1b+ v1.2",
        },
        # "LOG_DIR": Path.cwd(),
        "LOG_DIR": "hello",
        "USE_MOCK_DATA": False,
    },
}

# Load all settings from config.json
_config = SettingsManager.load_settings()

# Fallback to DEFAULT_CONFIG if file is empty or missing
if not _config:
    _config = DEFAULT_CONFIG

HMI_COLORS = _config.get("HMI_COLORS", DEFAULT_CONFIG["HMI_COLORS"])
ICONS = _config.get("ICONS", DEFAULT_CONFIG["ICONS"])
CONSTANTS = _config.get("CONSTANTS", DEFAULT_CONFIG["CONSTANTS"])
