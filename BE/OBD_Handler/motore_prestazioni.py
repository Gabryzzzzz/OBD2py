import obd
import random
import config as cfg

def leggi_dati(connection, sio):
    comandi = {
        "rpm": obd.commands.RPM,
        "velocita": obd.commands.SPEED,
        "acceleratore": obd.commands.THROTTLE_POS,
        "pressione_map": obd.commands.THROTTLE_POS, #da cambiare
        "flusso_maf": obd.commands.MAF
    }

    #se non è connesso simulare i dati
    if not connection.is_connected():
        simula_dati(sio)
    else:
        dati = {nome: connection.query(comando).value for nome, comando in comandi.items()}
        sio.emit('motore', dati)
        if cfg.SHOW_PRINTS:
            print(f"📤 Motore: {dati}")

def simula_dati(sio):
    # step_speed = 5  # Incremento per la velocità
    # step_rpm = 300  # Incremento per gli RPM
    # step_throttle = 5  # Incremento per la posizione dell'accelleratore
    dati = {
        "rpm": random.randint(800, 7200),
        "velocita": random.randint(0, 180),
        "acceleratore": random.randint(0, 100),
        "pressione_map": random.randint(0, 100),
        "flusso_maf": random.randint(0, 100)
    }
    sio.emit('motore', dati)
    if cfg.SHOW_PRINTS:
        print(f"📤 Motore: {dati}")