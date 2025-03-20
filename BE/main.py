import time
import obd
import eventlet
import socketio

from OBD_Handler import motore_prestazioni, consumi_carburante, temperatura_sensori, diagnostica, emissioni

from config import OBD_PORT, TRY_ENABLED, TRY_SLEEP, TRY_TIMES, UPDATE_INTERVAL

# Abilita WebSocket asincroni
eventlet.monkey_patch()

# Crea il server Socket.IO
sio = socketio.Server(cors_allowed_origins="*")
app = socketio.WSGIApp(sio)

# Funzione per inviare dati periodicamente
def send_data():
    while True:
        motore_prestazioni.leggi_dati(connection, sio)
        # temperatura_sensori.leggi_dati(connection, sio)
        # diagnostica.leggi_dati(connection, sio)
        # emissioni.leggi_dati(connection, sio)
        eventlet.sleep(UPDATE_INTERVAL)


# Funzione per configurare la connessione OBD
def configure_obd():
    global connection
    eventlet.sleep(5)
    connection = None
    if TRY_ENABLED:
        for i in range(TRY_TIMES):
            connection = obd.OBD(OBD_PORT, fast=True)
            if connection.is_connected():
                print("✅ Connessione OBD riuscita!")
                break
            else:
                #send a message to the client
                sio.emit('obd_error', {
                    'type': 'warn',
                    'title': 'OBD Error',
                    'message': f"Errore di connessione all'OBD, tentativo {i+1}",
                    'timestamp': int(time.time() * 1000)
                })
                print("❌ Errore di connessione all'OBD, tentativo", i+1)
                eventlet.sleep(TRY_SLEEP)
    else:
        connection = obd.OBD(OBD_PORT, fast=True)

    if connection.is_connected():
        print("✅ Connessione OBD riuscita!")
        sio.emit('obd_error', {
            'type': 'success',
            'title': 'OBD Success',
            'message': f"Connessione obd riuscita!",
            'timestamp': int(time.time() * 1000)
        })
    else:
        print("❌ Errore di connessione all'OBD")
        sio.emit('obd_error', {
            'type': 'error',
            'title': 'OBD Error',
            'message': f"Connessione obd non riuscita, attivo la modalita' di simulazione",
            'timestamp': int(time.time() * 1000)
        })
    
    eventlet.spawn(send_data)
    
# Avvia il server
if __name__ == '__main__':
    print("🚀 Server WebSocket in esecuzione su porta 5000...")
    print("🚀 Server WebSocket in esecuzione")
    print("Inizio configurazione OBD...")
    eventlet.spawn(configure_obd)
    eventlet.wsgi.server(eventlet.listen(('0.0.0.0', 5000)), app)
