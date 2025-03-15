import obd
import eventlet
import socketio

from OBD_Handler import motore_prestazioni, consumi_carburante, temperatura_sensori, diagnostica, emissioni

from config import OBD_PORT, UPDATE_INTERVAL

# Abilita WebSocket asincroni
eventlet.monkey_patch()

# Crea il server Socket.IO
sio = socketio.Server(cors_allowed_origins="*")
app = socketio.WSGIApp(sio)

# Connessione OBD
# connection = obd.OBD(OBD_PORT)
connection = obd.OBD("COM11", baudrate=38400, fast=True)

if connection.is_connected():
    print("✅ Connessione OBD riuscita!")
else:
    print("❌ Errore di connessione all'OBD")

# Funzione per inviare dati periodicamente
def send_data():
    while True:
        motore_prestazioni.leggi_dati(connection, sio)
        # data_consumi = consumi_carburante.leggi_dati(connection, sio)
        # temperatura_sensori.leggi_dati(connection, sio)
        # diagnostica.leggi_dati(connection, sio)
        # emissioni.leggi_dati(connection, sio)
        eventlet.sleep(UPDATE_INTERVAL)

# Avvia il thread per inviare dati periodicamente
eventlet.spawn(send_data)

# Avvia il server
if __name__ == '__main__':
    print("🚀 Server WebSocket in esecuzione su porta 5000...")
    eventlet.wsgi.server(eventlet.listen(('0.0.0.0', 5000)), app)
