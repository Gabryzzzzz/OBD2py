import obd
import random
import config as cfg


def leggi_dati(connection, sio):
    comandi = {
        "livello_carburante": obd.commands.FUEL_LEVEL,
        "consumo_instaneo": obd.commands.FUEL_RATE,
        "pressione_carburante": obd.commands
    }

    #se non è connesso simulare i dati
    if not connection.is_connected():
        simula_dati(sio)
    else:
        dati = {nome: connection.query(comando).value for nome, comando in comandi.items()}
        sio.emit('consumi', dati)
        if cfg.SHOW_PRINTS:
            print(f"📤 Consumi: {dati}")

def simula_dati(sio):
    dati = {
        "livello_carburante": random.randint(0, 100),
        "consumo_instaneo": random.randint(0, 100),
        "pressione_carburante": random.randint(0, 100)
    }
    sio.emit('consumi', dati)
    if cfg.SHOW_PRINTS:
        print(f"📤 Consumi: {dati}")