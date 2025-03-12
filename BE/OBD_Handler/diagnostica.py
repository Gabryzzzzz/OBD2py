import obd
import random
import config as cfg

def leggi_dati(connection, sio):
    comandi = {
        "codici_errore_dtc": obd.commands.GET_DTC,
        "stato_mil": obd.commands.GET_DTC,
        "tensione_ecu": obd.commands.CONTROL_MODULE_VOLTAGE,
        "tempo_reset_ecu": obd.commands.RUN_TIME
    }

    #se non è connesso simulare i dati
    if not connection.is_connected():
        simula_dati(sio)
    else:
        dati = {nome: connection.query(comando).value for nome, comando in comandi.items()}
        sio.emit('diagnostica', dati)
        if cfg.SHOW_PRINTS:
            print(f"📤 Diagnostica: {dati}")

def simula_dati(sio):
    dati = {
        "codici_errore_dtc": "N/A",
        "stato_mil": "N/A",
        "tensione_ecu": "N/A",
        "tempo_reset_ecu": "N/A"
    }
    sio.emit('diagnostica', dati)
    if cfg.SHOW_PRINTS:
        print(f"📤 Diagnostica: {dati}")
