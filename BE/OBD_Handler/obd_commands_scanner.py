import obd
import time
import sys
import os

# --- Configuration ---
# Set to None for auto-detection (e.g., '/dev/ttyUSB0' or '/dev/rfcomm0')
OBD_PORT = None 
OUTPUT_FILE = "obd_command_scan_results.txt"
TIMEOUT_SECS = 10 # Connection timeout in seconds

# --- Function to Find All Commands ---

def get_all_known_commands():
    """
    Safely attempts to retrieve the full list of OBD commands from the library,
    handling different version structures.
    """
    try:
        # 1. Try the most common modern structure
        return obd.commands.supported.ALL_COMMANDS
    except AttributeError:
        pass
        
    try:
        # 2. Try accessing commands by mode and joining them (a common internal approach)
        # This iterates through standard modes (01, 03, 04, etc.)
        all_cmds = []
        for mode in range(1, 10):
             # Check if the mode exists in the command map
            if mode in obd.commands:
                all_cmds.extend(obd.commands[mode])
        
        # Add non-mode specific commands like GET_DTC
        if obd.commands.GET_DTC not in all_cmds:
             all_cmds.append(obd.commands.GET_DTC)
             
        if not all_cmds:
             raise AttributeError("Mode-based command list is empty.")

        return all_cmds
    except (AttributeError, TypeError) as e:
        print(f"⚠️ Warning: Could not find comprehensive command list. Error: {e}")
        # 3. Fallback to a small, guaranteed set if all else fails
        return [obd.commands.RPM, obd.commands.SPEED, obd.commands.THROTTLE_POS]


# --- Main Script ---

def scan_obd_commands():
    """Connects to the OBD adapter, queries command support, and writes results to a file."""
    
    print(f"Attempting to connect to OBD adapter (Port: {'Auto' if OBD_PORT is None else OBD_PORT})...")
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
            #if connected exit the cycle
            if connection.is_connected():
                break
        except Exception as e:
            print(f"⚠️  Errore durante l'inizializzazione di python-obd su {port}: {e}")
            continue # Try the next port

    if not connection.is_connected():
        print("\n❌ FATAL: Connection established with adapter, but communication with the Car ECU failed.")
        return

    print(f"✅ Connection successful! Protocol: {connection.protocol_name()}")
    
    # 2. Get All Commands from Library and Supported Commands from ECU
    supported_commands = connection.supported_commands
    all_commands = get_all_known_commands() # Use the robust retrieval function
        
    print(f"Found {len(supported_commands)} commands officially supported by the ECU.")
    print(f"Scanning against {len(all_commands)} library commands...")
    print(f"Writing results to {OUTPUT_FILE}...")

    # 3. Process and Log Results
    with open(OUTPUT_FILE, 'w') as f:
        f.write(f"--- OBD-II Command Scan Results ---\n")
        f.write(f"Timestamp: {time.ctime()}\n")
        f.write(f"Protocol: {connection.protocol_name()}\n")
        f.write("-" * 80 + "\n")
        f.write(f"| {'STATUS':<15} | {'COMMAND NAME':<30} | {'QUERY VALUE':<30} |\n")
        f.write("-" * 80 + "\n")

        supported_set = {cmd.name for cmd in supported_commands}
        
        for cmd in all_commands:
            status = "UNAVAILABLE"
            value_str = "N/A"
            
            if cmd.name in supported_set:
                response = connection.query(cmd)
                
                if response.is_successful():
                    status = "AVAILABLE"
                    value_str = str(response.value)
                else:
                    status = "ERROR_ON_QUERY"
                    value_str = "Error/No Data"
            
            log_line = f"| {status:<15} | {cmd.name:<30} | {value_str:<30} |\n"
            f.write(log_line)

        f.write("-" * 80 + "\n")
        f.write("Scan complete. 'AVAILABLE' means the vehicle's ECU confirmed support.\n")

    # 4. Clean up
    connection.close()
    print(f"\n✅ Scan complete. Results saved to '{os.path.abspath(OUTPUT_FILE)}'.")


if __name__ == "__main__":
    scan_obd_commands()