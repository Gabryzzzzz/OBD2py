import time
import obd
import eventlet
import socketio
import socket
from config import config as cfg
from OBD_Handler import motore_prestazioni, altri_dati, consumi_carburante, temperatura_sensori, diagnostica, emissioni
from gyroscope import gyroscope
from led import led
from inputs import get_gamepad
import os



# TMs = []
# def aggiungi_display(clk, dio):
#     TMs.append(tm1637.TM1637(clk=clk, dio=dio))

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

# connection = None

informazioni_richieste = {
    "motore": True,
    "altri_dati": False
}

def send_gyroscope_data():
    while True:
        time.sleep(0.01)
        acc, gyr, temp = gyroscope.get_info()
        sio.emit('posizione', [ acc, gyr, temp ])
            

# Funzione per inviare dati periodicamente
def send_data():
    eventlet.spawn(send_gyroscope_data)
    while True:
        if informazioni_richieste['motore']:
            motore_prestazioni.leggi_dati(connection, sio, cfg, led)
            # acc, gyr, temp = gyroscope.get_info()
            # sio.emit('posizione', [ acc, gyr, temp ])
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
    # TMs[0].scroll, "ERROR: " + message
    sio.emit('popup_channel', {
        'type': 'error',
        'title': title,
        'message': message,
        'timestamp': int(time.time() * 1000)
    })

#anche per i popup success
def send_success(title,message):
    # TMs[1].scroll, "SUCCES: " + message
    sio.emit('popup_channel', {
        'type': 'success',
        'title': title,
        'message': message,
        'timestamp': int(time.time() * 1000)
    })

data_requested_led = "acc"
setup_executed = False
def setup_display():
    if not setup_executed:
        # time.sleep(1)
        led.setup_led_display()
        # eventlet.spawn(gyroscope.start_gyro)
        # eventlet.spawn(send_pos_info)
        while True:
            acc, gyr, temp = gyroscope.get_info()
            if data_requested_led == "acc":
                x1, x2 = dividi_numero(acc[0])
                y1, y2 = dividi_numero(acc[1])
                z1, z2 = dividi_numero(acc[2])
                eventlet.spawn(led.TMs[0].numbers, int(x1), int(x2))
                eventlet.spawn(led.TMs[1].numbers, int(y1), int(y2))
                eventlet.spawn(led.TMs[2].numbers, int(z1), int(z2))
            if data_requested_led == "gyr":
                x1, x2 = dividi_numero(gyr[0])
                y1, y2 = dividi_numero(gyr[1])
                z1, z2 = dividi_numero(gyr[2])
                eventlet.spawn(led.TMs[0].numbers, int(x1), int(x2))
                eventlet.spawn(led.TMs[1].numbers, int(y1), int(y2))
                eventlet.spawn(led.TMs[2].numbers, int(z1), int(z2))
            if data_requested_led == "temp":
                # eventlet.spawn(led.TMs[1].temperature, int(temp))
                pass
            time.sleep(0.3)






def dividi_numero(valore_float):
    # 1. Converti il float in una stringa
    stringa_completa = str(valore_float)

    # 2. Gestisci i numeri negativi
    segno = ""
    if stringa_completa.startswith('-'):
        segno = "-"
        # Rimuovi il segno per le operazioni successive
        stringa_completa = stringa_completa[1:]

    # 3. Trova la posizione del punto decimale
    parti = stringa_completa.split('.')
    if len(parti) > 1:

        # 4. Estrai la parte intera (a sinistra del punto)
        parte_intera_str = parti[0]

        # 5. Estrai la parte decimale (a destra del punto)
        parte_decimale_str = parti[1]

        # 6. Formatta la parte intera
        # Se la parte intera è lunga 1, aggiungi uno 0 davanti (es. 1 -> 01)
        if len(parte_intera_str) < 2:
            parte_intera_formattata = f"{segno}0{parte_intera_str}"
        else:
            parte_intera_formattata = f"{segno}{parte_intera_str}"

        # 7. Formatta la parte decimale
        # Assicurati che sia lunga 2, aggiungendo uno 0 se necessario
        parte_decimale_formattata = parte_decimale_str[:2].ljust(2, '0')

        # 8. Restituisci le due parti come tuple
        return parte_intera_formattata, parte_decimale_formattata
    else:
        return "00", "00"

#Quando ricevi richiesta da FE manda una stringa di test in un canale di test
@sio.on('test_led')
def test_led(sid, data):
    send_success('TEST LED', 'Inizio test')
    # os.system("python /home/gabryzzzzz/Documents/led.py")
    # eventlet.spawn(setup_hardware)
    global data_requested_led
    data_requested_led = data
    eventlet.spawn(setup_display)
    time.sleep(2)
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

    if data.LED_CONFIG is not cfg.LED_CONFIG:
        setup_display()

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



def controller_ps3():
    time.sleep(5)
    # global data_requested_led
    # To store the state of the buttons (0=released, 1=pressed)
    button_states = {}
    print("Controller active. Press a button or move the stick. (Ctrl+C to exit)")
    while True:
        # Get all available events from the gamepad
        try:
            events = get_gamepad()
        except Exception:
            print("Gamepad not found. Please connect a gamepad.")
            break

        for event in events:
            # Update the stick state when an 'Absolute' event is received
            if event.ev_type == 'Absolute':
                if event.code == 'ABS_X':
                    left_stick_x = event.state
                elif event.code == 'ABS_Y':
                    left_stick_y = event.state

                # Get previous state for D-pad and Triggers
                prev_state = button_states.get(event.code, 0)

                # D-PAD: Check for transition from 0 (released) to not 0 (pressed)
                if event.code in ('ABS_HAT0X', 'ABS_HAT0Y'):
                    if event.state != 0 and prev_state == 0:
                        print(f"D-Pad {event.code} pressed with value: {event.state}")

                # TRIGGERS: Check for transition from 0 to a pressed state
                if event.code in ('ABS_Z', 'ABS_RZ'): # Corresponds to LT/L2 and RT/R2
                    if event.state > 0 and prev_state == 0:
                        print(f"Trigger {event.code} was pressed")

                button_states[event.code] = event.state
            # Handle button presses
            elif event.ev_type == 'Key':
                # Get the previous state of the button, defaulting to 0 (released)
                prev_state = button_states.get(event.code, 0)
                # Check if the button is being pressed now and was released before
                if event.state == 1 and prev_state == 0:
                    if event.code == 'BTN_START':
                        print("Start button pressed")
                    elif event.code == 'BTN_SELECT':
                        print("Select button pressed")
                    else:
                        if event.code == 'BTN_SOUTH':
                            print("X button pressed, cycling LED config")
                            # if data_requested_led == "acc":
                            #     data_requested_led = "gyr"
                            # elif data_requested_led == "gyr":
                            #     data_requested_led = "temp"
                            # elif data_requested_led == "temp":
                            #     data_requested_led = "acc"
                            # send_success('LED Config', f'LED display now showing: {data_requested_led}')

                        print(f"Button {event.code} was pressed")
                button_states[event.code] = event.state

def launch_ps3():
    eventlet.spawn(controller_ps3)



# Avvia il server
if __name__ == '__main__':
    global eventlet_obd

    eventlet.spawn(gyroscope.start_gyro)
    time.sleep(2)
    eventlet.spawn(setup_display)
    print("🎮 Avvio controller PS3")
    launch_ps3()
    print("🚀 Server WebSocket in esecuzione su porta 5000...")
    print("🚀 Server WebSocket in esecuzione")
    print("Inizio configurazione OBD...")
    # eventlet.spawn(configure_obd) must add a way to identify and kill it
    eventlet_obd = eventlet.spawn(configure_obd)

    data_requested_led = cfg.LED_CONFIG

    # eventlet.spawn(setup_display) 
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
