import json
import os

SETTINGS_FILE = "config.json"


class SettingsManager:
    @staticmethod
    def load_settings():
        if not os.path.exists(SETTINGS_FILE):
            return {}
        try:
            with open(SETTINGS_FILE, "r") as f:
                return json.load(f)
        except (json.JSONDecodeError, OSError):
            print(f"Error loading {SETTINGS_FILE}")
            return {}

    @staticmethod
    def save_settings(settings):
        try:
            with open(SETTINGS_FILE, "w") as f:
                json.dump(settings, f, indent=4)
            return True
        except OSError as e:
            print(f"Error saving {SETTINGS_FILE}: {e}")
            return False
