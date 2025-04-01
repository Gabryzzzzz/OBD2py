# OBD_PORT = "COM11"  # Modifica con la tua connessione OBD (WiFi)
# UPDATE_INTERVAL = 0.1  # Secondi tra ogni aggiornamento dati
# SHOW_PRINTS = True  # Mostra i print di debug
# TRY_TIMES = 5  # Tentativi di connessione OBD
# TRY_SLEEP = 3  # Secondi tra ogni tentativo di connessione
# TRY_ENABLED = False  # Abilita i tentativi di connessione

import json

#make a class to store the config
class Config:
    def __init__(self, config):
        self.OBD_PORT = config['OBD_PORT']
        self.UPDATE_INTERVAL = config['UPDATE_INTERVAL']
        self.SHOW_PRINTS = config['SHOW_PRINTS']
        self.TRY_TIMES = config['TRY_TIMES']
        self.TRY_SLEEP = config['TRY_SLEEP']
        self.TRY_ENABLED = config['TRY_ENABLED']
    #reload configuration with json
    def reload(self):
        with open('config.json') as f:
            config = json.load(f)
            self.OBD_PORT = config['OBD_PORT']
            self.UPDATE_INTERVAL = config['UPDATE_INTERVAL']
            self.SHOW_PRINTS = config['SHOW_PRINTS']
            self.TRY_TIMES = config['TRY_TIMES']
            self.TRY_SLEEP = config['TRY_SLEEP']
            self.TRY_ENABLED = config['TRY_ENABLED']
    

#take the config from the json
with open('config.json') as f:
    #adapt with the class
    config = json.load(f)
    config = Config(config)


