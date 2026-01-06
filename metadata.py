PROJECT_METADATA = {
    "Name": "Human Movement Measurement HMI",
    "Version": "1.0.0",
    "Authors": ["Oswald Syndric", "Anh Tuan", "Ego Victor"],
    "Description": "A multi-page Tkinter GUI for monitoring a Raspberry Pi/ZigBee-based motion detection system. Designed for industrial-grade HMI.",
    "Hardware": [
        "2x Raspberypi 1b+",
        "2x zigbee xbee 3 module",
        "1x pir motion sensor",
    ],
    "Communication": "ZigBee Wireless Serial",
    "License": "MIT",
    "GitHub URL": "https://github.com/syoswaldcedric/motion-sensor.git",
    "Issues": "https://github.com/syoswaldcedric/motion-sensor/issues",
    "Docs": "https://github.com/syoswaldcedric/motion-sensor/blob/main/README.md",
    "Last Updated": "December 14, 2025",
}

# Define a theme for the HMI look
HMI_COLORS = {
    "BACKGROUND": "#2C3E50",  # Dark Blue/Grey (Industrial Look)
    "FOREGROUND": "#ECF0F1",  # Light Grey/White
    "ACCENT": "#E74C3C",  # Red (for alerts/power off)
    "PRIMARY": "#2ECC71",  # Green (for power on/status OK)
    "DANGER": "#C0392B",  # Darker Red
    "INFO": "#3498DB",  # Blue
    "TEXT_BRIGHT": "#FFFFFF",  # Pure White
    "TEXT_DIM": "#BDC3C7",  # Subtle Grey
}


ICONS = {"logo": "assets/graph.png"}


# -----------------------------
# Configuration and constants
# -----------------------------
CONSTANTS = {
    "UPDATE_INTERVAL_MS": 1000,  # 1 second GUI update
    "MOTION_HISTORY_LENGTH": 50,
    "DEFAULT_SERIAL_PORT": "/dev/serial0",
    "DEFAULT_BAUDRATE": 115200,
    # "DEFAULT_SCREEN_SIZE": (800, 600),
    # default screen size for LCD 3.5"
    "DEFAULT_SCREEN_SIZE": (480, 320),
}
