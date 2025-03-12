import obd
import random
import config as cfg

def leggi_dati(connection, sio):
    comandi = {
        "temp_liquido_refrigerante": obd.commands.COOLANT_TEMP,
        "temp_olio_motore": obd.commands.OIL_TEMP,
        "temp_aspirazione": obd.commands.INTAKE_TEMP,
        "temp_ambiente": obd.commands.AMBIANT_AIR_TEMP
    }

    #se non è connesso simulare i dati
    if not connection.is_connected():
        simula_dati(sio)
    else:
        dati = {nome: connection.query(comando).value for nome, comando in comandi.items()}
        sio.emit('temperature', dati)
        if cfg.SHOW_PRINTS:
            print(f"📤 Temperature: {dati}")

def simula_dati(sio):
    dati = {
        "temp_liquido_refrigerante": random.randint(0, 100),
        "temp_olio_motore": random.randint(0, 100),
        "temp_aspirazione": random.randint(0, 100),
        "temp_ambiente": random.randint(0, 100)
    }
    sio.emit('temperature', dati)
    if cfg.SHOW_PRINTS:
        print(f"📤 Temperature: {dati}")
