import obd
import random
from config import config as cfg
import json

def leggi_dati(connection, sio, cfg, led, db_handler):
    comandi = {
        "rpm": obd.commands.RPM,
        "velocita": obd.commands.SPEED,
        "acceleratore": obd.commands.THROTTLE_POS,
        "pressione_map": obd.commands.THROTTLE_POS, #da cambiare
        "flusso_maf": obd.commands.THROTTLE_POS
    }

    #se non è connesso simulare i dati
    if not connection or not connection.is_connected():
        simula_dati(sio, cfg, led, db_handler)
    else:
        #leggi e formatta i vari dati per avere interi
        dati = {}
        if cfg.IS_RASPBERRY_PI and cfg.LED_CONFIG == "motore":
            led.TMs[0].temperature(int(connection.query(obd.commands.COOLANT_TEMP).value.magnitude))
            led.TMs[1].number(int(connection.query(obd.commands.SPEED).value.magnitude))
            led.TMs[2].number(int(connection.query(obd.commands.THROTTLE_POS).value.magnitude))
        for nome, comando in comandi.items():
            try:
                risposta = connection.query(comando)
                dati[nome] = int(risposta.value.magnitude)
            except Exception as e:
                dati[nome] = 0
        
        dati['simulated'] = False
        sio.emit('motore', dati)
        db_handler.insert_data('motore_prestazioni', json.dumps(dati))

        if cfg.SHOW_PRINTS:
            print(f"📤 Motore: {dati}")

def simula_dati(sio, cfg, led, db_handler):
    # step_speed = 5  # Incremento per la velocità
    # step_rpm = 300  # Incremento per gli RPM
    # step_throttle = 5  # Incremento per la posizione dell'accelleratore
    dati = {
        "rpm": random.randint(800, 7200),
        "velocita": random.randint(0, 180),
        "acceleratore": random.randint(14, 75),
        "pressione_map": random.randint(0, 100),
        "flusso_maf": random.randint(0, 100)
    }
    dati['simulated'] = True

    if cfg.IS_RASPBERRY_PI and cfg.LED_CONFIG == "motore":
        led.TMs[0].temperature(int(random.randint(0, 99)))
        led.TMs[1].number(int(dati["velocita"]))
        led.TMs[2].number(int(dati["rpm"]))

    sio.emit('motore', dati)
    db_handler.insert_data('motore_prestazioni', json.dumps(dati))

    if cfg.SHOW_PRINTS:
        print(f"📤 Motore: {dati}")