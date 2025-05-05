import obd
import random
from config import config as cfg

import time

km_percorsi = 0
last_time = time.time()

def aggiorna_distanza(connection):
    global km_percorsi, last_time

    current_time = time.time()
    delta_t = current_time - last_time  # secondi
    last_time = current_time

    if not connection.is_connected():
        speed = random.randint(0, 180)  # float
        # distanza = velocità (km/h) * tempo (h)
        distanza = speed * (delta_t / 3600.0)
        km_percorsi += distanza
        if cfg.SHOW_PRINTS:
            print(f"🏁 Totale: {km_percorsi:.2f} km")
        return
    else:
        response = connection.query(obd.commands.SPEED)

    if not response.is_null():
        speed = response.value.to("km/h").magnitude  # float
        # distanza = velocità (km/h) * tempo (h)
        distanza = speed * (delta_t / 3600.0)
        km_percorsi += distanza
        if cfg.SHOW_PRINTS:
            print(f"🏁 Totale: {km_percorsi:.2f} km")
    else:
        print("❌ Nessun dato sulla velocità")

    return km_percorsi

def leggi_dati(connection, sio):
    #se non è connesso simulare i dati
    aggiorna_distanza(connection)
    dati = {
        "km_percorsi": km_percorsi
    }
    sio.emit('altri_dati', dati)
    
    if cfg.SHOW_PRINTS:
        print(f"📤 Consumi: {dati}")
