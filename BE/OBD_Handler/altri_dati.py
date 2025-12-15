import obd
import random
from config import config as cfg

import time

# --- Global variables for tracking state ---
km_percorsi = 0
last_time = time.time()
last_db_log_time = 0

DB_LOG_INTERVAL = 10 # Log to database every 10 seconds

def aggiorna_distanza(connection):
    global km_percorsi, last_time

    current_time = time.time()
    delta_t = current_time - last_time  # secondi
    last_time = current_time

    if not connection or not connection.is_connected():
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

def leggi_dati(connection, sio, db_handler):
    global last_db_log_time

    # Update distance traveled based on current speed
    aggiorna_distanza(connection)

    # Emit data to frontend on every call
    dati = {
        "km_percorsi": km_percorsi
    }
    sio.emit('altri_dati', dati)
    
    # --- Timed Database Logging ---
    current_time = time.time()
    if current_time - last_db_log_time > DB_LOG_INTERVAL:
        is_simulated = not connection or not connection.is_connected()
        db_data = {
            "km_percorsi": round(km_percorsi, 4),
            "simulated": is_simulated
        }
        db_handler.insert_altri_dati_data(db_data)
        last_db_log_time = current_time # Reset the timer

    if cfg.SHOW_PRINTS:
        print(f"📤 Consumi: {dati}")
