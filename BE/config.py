import json
import os

class Config:
    def __init__(self):
        self.reload()

    def reload(self):
        """Loads or reloads the configuration from config.json."""
        try:
            with open('config.json', 'r') as f:
                config_data = json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            # Default values if file doesn't exist or is invalid
            config_data = {
                "UPDATE_INTERVAL": 0.1,
                "SHOW_PRINTS": True,
                "LED_CONFIG": "acc"
            }
        
        self.UPDATE_INTERVAL = config_data.get("UPDATE_INTERVAL", 0.1)
        self.SHOW_PRINTS = config_data.get("SHOW_PRINTS", True)
        self.LED_CONFIG = config_data.get("LED_CONFIG", "acc")
        
        # Check if running on Raspberry Pi
        self.IS_RASPBERRY_PI = False
        if os.name == 'posix':
            try:
                with open('/proc/cpuinfo', 'r') as f:
                    if 'Raspberry Pi' in f.read():
                        self.IS_RASPBERRY_PI = True
            except FileNotFoundError:
                pass

# Singleton instance
config = Config()