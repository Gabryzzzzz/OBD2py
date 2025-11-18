import time
import obd
import eventlet
import socketio
import socket
from config import config as cfg
from OBD_Handler import motore_prestazioni, altri_dati, consumi_carburante, temperatura_sensori, diagnostica, emissioni
from gyroscope import gyroscope
from led import led
import os
import threading
import subprocess
import json
import unicodedata

CONTROLLER_LOG_PATH = "ps3_controller/controller_log.txt"

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
eventlet_obd = None
eventlet_data = None

# connection = None

informazioni_richieste = {
    "motore": True,
    "altri_dati": False
}

def send_gyroscope_data():
    while True:
        eventlet.sleep(0.01)
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
    global connection, eventlet_data, eventlet_obd
    print("🔧 Configurazione OBD:")

    # Determine possible ports based on the operating system
    possible_ports = []
    if os.name == 'posix': # For Linux, macOS, etc.
        print("🐧 Rilevato sistema operativo POSIX (Linux/macOS). Scansione porte /dev/tty...")
        possible_ports.extend([f"/dev/ttyUSB{i}" for i in range(4)])
        possible_ports.extend([f"/dev/ttyACM{i}" for i in range(4)])
    elif os.name == 'nt': # For Windows
        print("💻 Rilevato sistema operativo Windows. Scansione porte COM...")
        possible_ports.extend([f"COM{i}" for i in range(1, 9)])

    connection = None

    for port in possible_ports:
        print(f"🔄 Tentativo di connessione sulla porta: {port}")
        try:
            connection = obd.OBD(port, fast=False, timeout=30)
        except Exception as e:
            print(f"⚠️  Errore durante l'inizializzazione di python-obd su {port}: {e}")
            continue # Try the next port

        if connection.is_connected():
            print(f"✅ Connessione OBD riuscita sulla porta {port}!")
            break # Exit the loop on successful connection
        else:
            print(f"❌ Connessione fallita sulla porta {port}")
            connection.close() # Close the failed connection before trying the next
            connection = None

    if connection: # Check if the connection object exists, not if it's connected (it will be if it exists)
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
    eventlet_obd = None # Clear the spawner task as it has completed

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

def sanitize_for_display(text):
    """Removes characters not suitable for the 7-segment display."""
    # Normalize to remove accents (e.g., 'à' -> 'a')
    nfkd_form = unicodedata.normalize('NFKD', text)
    text_without_accents = "".join([c for c in nfkd_form if not unicodedata.combining(c)])
    # Filter for allowed characters (alphanumeric, space, hyphen)
    return "".join(c for c in text_without_accents.upper() if c.isalnum() or c in " -")

#Funzione per popup di errore per non ripeterla nel codice
def send_error(title, message):
    sanitized_message = sanitize_for_display("ERROR " + message)
    
    # Adjust scroll speed based on message length.
    # A lower delay means faster scrolling.
    # The base delay is 250ms. We reduce it for longer messages.
    # This assumes the scroll() method accepts a 'delay' keyword argument in milliseconds.
    delay = max(100, 250 - len(sanitized_message) * 5) # Ensure delay is at least 100ms

    led.TMs[1].write([0, 0, 0, 0])
    led.TMs[2].write([0, 0, 0, 0])
    led.TMs[0].scroll(sanitized_message, delay=delay)

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

#Funzione per popup di info per non ripeterla nel codice
def send_info(title, message):
    sio.emit('popup_channel', {
        'type': 'info',
        'title': title,
        'message': message,
        'timestamp': int(time.time() * 1000)
    })

def update_config_file(config_data):
    """Writes the given data object to the config.json file and reloads the config."""
    try:
        with open('config.json', 'w') as f:
            json.dump(config_data, f, indent=4)
        cfg.reload()
        send_success('Configurazione', 'Configurazione salvata con successo!')
        print("💾 Configurazione salvata.")
    except Exception as e:
        print(f"❌ Errore durante il salvataggio della configurazione: {e}")
        send_error("Config Error", "Impossibile salvare la configurazione.")


data_requested_led = "acc"
setup_executed = False
def setup_display():
    if not setup_executed:
        # time.sleep(1)
        led.setup_led_display()
        # eventlet.spawn(gyroscope.start_gyro)
        # eventlet.spawn(send_pos_info)
        while True:
            # Get the raw data directly from the gyroscope module's global variables
            acc = gyroscope.accelerazione
            gyr = gyroscope.giroscopio
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
            time.sleep(0.1)






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
    config_object = json.loads(data)
    update_config_file(config_object) # This function is defined above


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

def monitor_controller_log():
    """
    Monitors the controller log file for new commands, sends them via WebSocket,
    and removes the processed line from the file.
    """
    global data_requested_led
    print("🎮 Avvio monitoraggio log controller...")
    while True:
        try:
            # Open the file for reading and writing
            with open(CONTROLLER_LOG_PATH, "r+") as f:
                lines = f.readlines()
                if lines:
                    # Get the first command and remove it from the list
                    command = lines.pop(0).strip()
                    
                    # Ignore session start messages
                    if command and not command.startswith("---"):
                        if command == 'CYCLE_LED_MODE':
                            # Cycle through the LED display modes
                            if data_requested_led == "acc":
                                data_requested_led = "gyr"
                            elif data_requested_led == "gyr":
                                data_requested_led = "motore"
                            else: # Covers 'temp' and any other state
                                data_requested_led = "acc"
                            
                            message = f"Modalità display LED cambiata in: {data_requested_led.upper()}"
                            print(f"🎮 {message}")
                            send_success('Controller', message)
                            # Get current config, edit, and save
                            with open('config.json', 'r') as f_config:
                                current_config = json.load(f_config)
                            current_config['LED_CONFIG'] = data_requested_led
                            update_config_file(current_config)
                        elif command == 'RETRY_OBD_CONNECTION':
                            print("🎮 Comando ricevuto: Riprova connessione OBD.")
                            send_info("Controller", "Riprova connessione OBD...")
                            led.TMs[0].scroll("OBD-RETRY") # Display message on LEDs
                            restart_obd(None) # Call the existing restart function
                        elif command in ('INTERVAL_UP', 'INTERVAL_DOWN'):
                            with open('config.json', 'r') as f_config:
                                current_config = json.load(f_config)
                            
                            current_interval = current_config.get('UPDATE_INTERVAL', 0.1)
                            
                            if command == 'INTERVAL_UP':
                                # Decrease interval for faster updates, with a minimum of 0.05s
                                new_interval = max(0.1, current_interval - 0.1)
                                action_text = "aumentata"
                            else: # INTERVAL_DOWN
                                # Increase interval for slower updates
                                new_interval = current_interval + 0.1
                                action_text = "diminuita"
                            
                            current_config['UPDATE_INTERVAL'] = round(new_interval, 2)
                            update_config_file(current_config)
                            
                            message = f"Frequenza di aggiornamento {action_text} a {current_config['UPDATE_INTERVAL']}s"
                            print(f"🎮 {message}")
                            send_success('Controller', message)
                        else:
                            print(f"🎮 Comando ricevuto dal controller: {command}")
                            send_info("🎮 Comando ricevuto dal controller", f"{command}")

                    # Go back to the start of the file and overwrite it with the remaining lines
                    f.seek(0)
                    f.truncate()
                    f.writelines(lines)
        except FileNotFoundError:
            pass # File might not exist yet, just wait
        eventlet.sleep(0.1) # Check the file every 100ms

# Avvia il server
if __name__ == '__main__':
    # global eventlet_obd # This is not needed here as it's already global
    data_requested_led = cfg.LED_CONFIG
    
    eventlet.spawn(gyroscope.start_gyro)
    time.sleep(2)
    eventlet.spawn(setup_display)

    #--- Start sixad driver for PS3 controller if not running ---
    print("🎮 Checking for sixad driver...")
    check_sixad = subprocess.run(["pgrep", "sixad"], capture_output=True, text=True)
    if check_sixad.returncode != 0:
        print("⚠️ sixad driver not running. Attempting to start it...")
        send_info("Avvio Servizi", "🎮 Avvio sixad driver...")
        try:
            # Using Popen to run in the background and not block
            subprocess.Popen(["sudo", "sixad", "--start"])
            print("✅ sixad driver started. Please connect your controller by pressing the PS button.")
            send_success("Avvio Servizi", "Driver sixad avviato. Connetti il controller.")
            time.sleep(2) # Give it a moment to initialize
        except (subprocess.CalledProcessError, FileNotFoundError) as e:
            print(f"❌ Failed to start sixad driver: {e}")
            send_error("Driver Error", "Impossibile avviare sixad.")
    else:
        pid = check_sixad.stdout.strip()
        print(f"✅ sixad driver is already running (PID: {pid}).")
    
    # Check if the controller process is already running to kill it before restarting
    check_process = subprocess.run(["pgrep", "-f", "controller_evdev.py"], capture_output=True, text=True)
    if check_process.returncode == 0:
        pid = check_process.stdout.strip()
        send_info("Avvio Servizi", f"🎮 Trovato controller PS3 in esecuzione (PID: {pid}). Lo chiudo.")
        print(f"🎮 Trovato controller PS3 in esecuzione (PID: {pid}). Lo chiudo.")
        subprocess.run(["kill", pid])
        time.sleep(0.5) # Give a moment for the process to terminate

    # Launch the new controller process
    send_info("Avvio Servizi", "🎮 Avvio nuovo controller PS3 (EVDEV)...")
    subprocess.Popen(["python3", "controller_evdev.py"], cwd="ps3_controller")
    
    # Start the background task to monitor the controller's log file
    eventlet.spawn(monitor_controller_log)

    print("🚀 Server WebSocket in esecuzione su porta 5000...")
    print("🚀 Server WebSocket in esecuzione")
    print("Inizio configurazione OBD...")
    # eventlet.spawn(configure_obd) must add a way to identify and kill it
    eventlet_obd = eventlet.spawn(configure_obd)


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
