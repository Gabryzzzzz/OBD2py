# OBD_PORT = "COM11"  # Modifica con la tua connessione OBD (WiFi)
# UPDATE_INTERVAL = 0.1  # Secondi tra ogni aggiornamento dati
# SHOW_PRINTS = True  # Mostra i print di debug
# TRY_TIMES = 5  # Tentativi di connessione OBD
# TRY_SLEEP = 3  # Secondi tra ogni tentativo di connessione
# TRY_ENABLED = False  # Abilita i tentativi di connessione

import json
import os

CONFIG_FILE = 'config.json'

# Define the default configuration settings
DEFAULT_CONFIG = {
    "OBD_PORT": "/dev/ttyUSB0",
    "UPDATE_INTERVAL": 0.5,
    "SHOW_PRINTS": False,
    "TRY_TIMES": 4,
    "TRY_SLEEP": 4,
    "TRY_ENABLED": False,
    "LED_CONFIG": "motore"
}

#make a class to store the config
class Config:
    def __init__(self, config_data):
        # Use .get() for safer access, falling back to defaults if a key is missing
        self.OBD_PORT = config_data.get('OBD_PORT', DEFAULT_CONFIG['OBD_PORT'])
        self.UPDATE_INTERVAL = config_data.get('UPDATE_INTERVAL', DEFAULT_CONFIG['UPDATE_INTERVAL'])
        self.SHOW_PRINTS = config_data.get('SHOW_PRINTS', DEFAULT_CONFIG['SHOW_PRINTS'])
        self.TRY_TIMES = config_data.get('TRY_TIMES', DEFAULT_CONFIG['TRY_TIMES'])
        self.TRY_SLEEP = config_data.get('TRY_SLEEP', DEFAULT_CONFIG['TRY_SLEEP'])
        self.TRY_ENABLED = config_data.get('TRY_ENABLED', DEFAULT_CONFIG['TRY_ENABLED'])
        self.LED_CONFIG = config_data.get('LED_CONFIG', DEFAULT_CONFIG['LED_CONFIG'])

    #reload configuration with json
    def reload(self):
        """Reloads the configuration from the JSON file."""
        loaded_config = _load_or_create_config()
        self.__init__(loaded_config)

def _load_or_create_config():
    """Loads config from file, or creates it with defaults if it's missing or empty."""
    if not os.path.exists(CONFIG_FILE) or os.path.getsize(CONFIG_FILE) == 0:
        print(f"⚠️ '{CONFIG_FILE}' not found or is empty. Creating with default values.")
        with open(CONFIG_FILE, 'w') as f:
            json.dump(DEFAULT_CONFIG, f, indent=4)
        return DEFAULT_CONFIG
    
    try:
        with open(CONFIG_FILE, 'r') as f:
            return json.load(f)
    except json.JSONDecodeError:
        print(f"❌ Error decoding '{CONFIG_FILE}'. Recreating with default values.")
        with open(CONFIG_FILE, 'w') as f:
            json.dump(DEFAULT_CONFIG, f, indent=4)
        return DEFAULT_CONFIG

config = Config(_load_or_create_config())
