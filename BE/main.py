import time
import obd
import eventlet
import socketio
import socket
import os
import json

from OBD_Handler import motore_prestazioni, altri_dati, consumi_carburante, temperatura_sensori, diagnostica, emissioni

from config import config as cfg
# from led_controller import TMs, aggiungi_display
import tm1637

TMs = []
def aggiungi_display(clk, dio):
    TMs.append(tm1637.TM1637(clk=clk, dio=dio))

# aggiungi_display(25, 8)
# aggiungi_display(7, 1)
# Abilita WebSocket asincroni
eventlet.monkey_patch()

# Crea il server Socket.IO
sio = socketio.Server(cors_allowed_origins="*")
app = socketio.WSGIApp(sio)

#variabili per tenere traccia degli eventlet generati per configure obd e send data
# eventlet_obd = None
# eventlet_data = None


informazioni_richieste = {
    "motore": False,
    "altri_dati": False
}


# Funzione per inviare dati periodicamente
def send_data():
    while True:
        if informazioni_richieste['motore']:
            motore_prestazioni.leggi_dati(connection, sio)
        if informazioni_richieste['altri_dati']:
            altri_dati.leggi_dati(connection, sio)
        # temperatura_sensori.leggi_dati(connection, sio)
        # diagnostica.leggi_dati(connection, sio)
        # emissioni.leggi_dati(connection, sio)
        eventlet.sleep(cfg.UPDATE_INTERVAL)


# Funzione per configurare la connessione OBD
def configure_obd():
    global connection, eventlet_data
    #print the config
    print("🔧 Configurazione OBD:")
    print(f"Show prints: {cfg.SHOW_PRINTS}")
    # eventlet.sleep(5)
    connection = None
    if cfg.TRY_ENABLED:
        for i in range(cfg.TRY_TIMES):
            connection = obd.OBD(cfg.OBD_PORT)
            if connection.is_connected():
                print("✅ Connessione OBD riuscita!")
                break
            else:
                #send a message to the client
                # sio.emit('popup_channel', {
                #     'type': 'warn',
                #     'title': 'OBD Error',
                #     'message': f"Errore di connessione all'OBD, tentativo {i+1}",
                #     'timestamp': int(time.time() * 1000)
                # })
                send_error('OBD Error', f"Errore di connessione all'OBD, tentativo {i+1}")
                print("❌ Errore di connessione all'OBD, tentativo", i+1)
                eventlet.sleep(cfg.TRY_SLEEP)
    else:
        connection = obd.OBD(cfg.OBD_PORT, fast=True)

    if connection.is_connected():
        print("✅ Connessione OBD riuscita!")
        # sio.emit('popup_channel', {
        #     'type': 'success',
        #     'title': 'OBD Success',
        #     'message': f"Connessione obd riuscita!",
        #     'timestamp': int(time.time() * 1000)
        # })
        send_success('OBD Success', 'Connessione obd riuscita!')
    else:
        print("❌ Errore di connessione all'OBD")
        # sio.emit('popup_channel', {
        #     'type': 'error',
        #     'title': 'OBD Error',
        #     'message': f"Connessione obd non riuscita, attivo la modalita' di simulazione",
        #     'timestamp': int(time.time() * 1000)
        # })
        send_error('OBD Error', 'Connessione obd non riuscita, attivo la modalita\' di simulazione')

    eventlet_data = eventlet.spawn(send_data)

def get_ip():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.settimeout(0)
    try:
        # doesn't even have to be reachable
        s.connect(('10.254.254.254', 1))
        IP = s.getsockname()[0]
    except Exception:
        IP = '127.0.0.1'
    finally:
        s.close()
    return IP

#Funzione per popup di errore per non ripeterla nel codice
def send_error(title, message):
    TMs[0].scroll, "ERROR: " + message
    sio.emit('popup_channel', {
        'type': 'error',
        'title': title,
        'message': message,
        'timestamp': int(time.time() * 1000)
    })

#anche per i popup success
def send_success(title,message):
    TMs[1].scroll, "SUCCES: " + message
    sio.emit('popup_channel', {
        'type': 'success',
        'title': title,
        'message': message,
        'timestamp': int(time.time() * 1000)
    })

#Quando ricevi richiesta da FE manda una stringa di test in un canale di test
@sio.on('test_led')
def test_led(sid, data):
    send_success('TEST LED', 'Inizio test')
    aggiungi_display(23, 24)
    TMs[0].scroll, "TEST LED"
    send_success('TEST LED', 'Fine test')



#Quando ricevi richiesta da FE manda una stringa di test in un canale di test
@sio.on('request_ip')
def request_ip(sid, data):
    #send local ip to the client
    print("📤 Invio IP locale al client...")
    ip = get_ip()
    print("📤 IP locale:", ip)
    sio.emit('local_ip', {
        'ip': ip
    })

#Quando ricevi richiesta da FE manda una stringa di test in un canale di test
@sio.on('set_config')
def request_set_config(sid, data):
    #send local ip to the client
    print("📤 Configurazione ricevuta dal client...")
    print(data) 
    with open('config.json', 'w') as f:
        f.write(data)
    eventlet.sleep(1)
    cfg.reload()
    send_success('Configurazione', 'Configurazione salvata con successo!')


#get config
@sio.on('enable_channel')
def request_enable_channel(sid, data):
    print("📤 Abilita canale...")
    print(data)
    informazioni_richieste[data['canale']] = data['abilita']


#get config
@sio.on('get_config')
def request_get_config(sid):
    print("📤 Invio configurazione al client...")
    with open('config.json', 'r') as f:
        config = f.read()
    sio.emit('config', config)

#Restart obd configuration
@sio.on('restart_obd')
def restart_obd(sid):
    global eventlet_obd, eventlet_data
    print("🔄 Ricevuto segnale di riavvio OBD...")

    # Termina i thread esistenti se attivi
    if eventlet_obd and not eventlet_obd.dead:
        eventlet_obd.kill()
        print("❌ Thread OBD terminato.")

    if eventlet_data and not eventlet_data.dead:
        eventlet_data.kill()
        print("❌ Thread invio dati terminato.")

    # Avvia nuovamente la configurazione OBD
    eventlet_obd = eventlet.spawn(configure_obd)
    send_success('OBD Restart', 'OBD riavviato con successo!')
    
#stop obd configuration
@sio.on('stop_obd')
def stop_obd(sid):
    global eventlet_obd, eventlet_data
    print("🛑 Ricevuto segnale di stop OBD...")

    # Termina i thread esistenti se attivi
    if eventlet_obd and not eventlet_obd.dead:
        eventlet_obd.kill()
        print("❌ Thread OBD terminato.")

    if eventlet_data and not eventlet_data.dead:
        eventlet_data.kill()
        print("❌ Thread invio dati terminato.")
    
    send_success('OBD Stop', 'OBD fermato con successo!')

# Avvia il server
if __name__ == '__main__':
    global eventlet_obd

    print("🚀 Server WebSocket in esecuzione su porta 5000...")
    print("🚀 Server WebSocket in esecuzione")
    print("Inizio configurazione OBD...")
    # eventlet.spawn(configure_obd) must add a way to identify and kill it
    eventlet_obd = eventlet.spawn(configure_obd)
    #get the locale ip with get_ip() and save it to a file into ../FE/src/assets/ip.txt
    ip = get_ip()
    print("📤 IP locale:", ip)
    #get the template into template/ips.ts
    template = open('template/ips.ts', 'r').read()
    #replace PLACEHOLDER with the ip
    template = template.replace('PLACEHOLDER', ip)
    with open('../FE/src/assets/ip.ts', 'w') as f:
        f.write(template)
    eventlet.wsgi.server(eventlet.listen(('0.0.0.0', 5000)), app)
