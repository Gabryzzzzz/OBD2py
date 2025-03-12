import obd
import random
import config as cfg

def leggi_dati(connection, sio):
    comandi = {
        # "Sensore O2 Banco 1 Sensore 1": obd.commands.O2_B1S1,
        # "Pressione Vapori EVAP": obd.commands.EVAP_VAPOR_PRESSURE,
        # "Temp. Catalizzatore": obd.commands.CATALYST_TEMP_B1S1
        "sensore_o2_banco_1_sensore_1": obd.commands.O2_B1S1,
        "pressione_vapori_evap": obd.commands.EVAP_VAPOR_PRESSURE,
        "temp_catalizzatore": obd.commands.CATALYST_TEMP_B1S1
    }
    #se non è connesso simulare i dati  
    if not connection.is_connected():
        simula_dati(sio)
    else:
        dati = {nome: connection.query(comando).value for nome, comando in comandi.items()}
        sio.emit('emissioni', dati)
        if cfg.SHOW_PRINTS:
            print(f"📤 Emissioni: {dati}")

def simula_dati(sio):
    dati = {
        "Sensore O2 Banco 1 Sensore 1": "N/A",
        "Pressione Vapori EVAP": "N/A",
        "Temp. Catalizzatore": "N/A"
    }
    sio.emit('emissioni', dati)
    if cfg.SHOW_PRINTS:
        print(f"📤 Emissioni", dati)
