import time
import sys
import subprocess
import json
import os
import evdev
from evdev import ecodes

LOG_FILE = "controller_log.txt"
TARGET_DEVICE_NAME = "PLAYSTATION"
BUTTON_MAP_FILE = "button_map.json"

def find_controller():
    """
    Scans for and connects to a device with TARGET_DEVICE_NAME in its name.
    Returns the device object upon successful connection.
    """
    while True:
        print(f"⏳ Scanning for a device named '{TARGET_DEVICE_NAME}'...")
        devices = [evdev.InputDevice(path) for path in evdev.list_devices()]
        for device in devices:
            if TARGET_DEVICE_NAME in device.name:
                print(f"✅ Found controller: {device.path} - {device.name}")
                return device
        
        print("⚠️ Controller not found. Retrying in 5 seconds...")
        time.sleep(5)

def load_button_map():
    """Loads the button map and creates a reverse map for quick lookups."""
    map_path = os.path.join(os.path.dirname(__file__), BUTTON_MAP_FILE)
    try:
        with open(map_path, "r") as f:
            action_to_code = json.load(f)
            # Create a reverse map for efficient lookups {code: action}
            code_to_action = {v: k for k, v in action_to_code.items()}
            print("✅ Button map loaded successfully.")
            return code_to_action
    except FileNotFoundError:
        print(f"❌ ERROR: '{BUTTON_MAP_FILE}' not found.")
        print("   Please run 'map_controller.py' first to generate it.")
        sys.exit(1)
    except (json.JSONDecodeError, KeyError) as e:
        print(f"❌ ERROR: Invalid button map file. {e}")
        print("   Please run 'map_controller.py' again.")
        sys.exit(1)

def main():
    """
    Main function to find the controller and process its events.
    """
    # Load the button mapping at the start
    code_to_action_map = load_button_map()

    try:
        with open(LOG_FILE, "a", encoding="utf-8") as log_file:
            log_file.write(f"--- New EVDEV Session Started at {time.ctime()} ---\n")
            log_file.flush()

            while True: # Main loop to handle reconnection
                device = find_controller()

                try:
                    # Grab exclusive access to the device
                    device.grab()
                    print("🎮 Monitoring for events...")
                    
                    for event in device.read_loop():
                        # For development purposes, print all categorized events
                        # This will show analog stick movements, triggers, etc.
                        # try:
                        #     print(evdev.categorize(event))
                        # except KeyError:
                        #     # This happens when a button code is not recognized by the library
                        #     print(f"Unknown event: type={event.type}, code={event.code}, value={event.value}")

                        # We only care about key presses (event.value == 1)
                        if event.type == ecodes.EV_KEY and event.value == 1:
                            action = code_to_action_map.get(event.code)

                            if not action:
                                continue # Ignore unmapped buttons

                            print(f"Button press detected: '{action}' (code: {event.code})")

                            # Handle special actions that don't just log a message
                            if action == "EXIT_SCRIPT":
                                print("Exit button pressed. Exiting.")
                                sys.exit(0)
                            elif action == "RESTART_SERVICE":
                                print("R1 button pressed. Restarting obd2Pi service...")
                                try:
                                    subprocess.run(["sudo", "systemctl", "restart", "obd2Pi.service"], check=True)
                                except (subprocess.CalledProcessError, FileNotFoundError) as e:
                                    print(f"❌ Failed to restart service: {e}")
                            elif action == "STOP_SERVICE":
                                print("R2 button pressed. Stopping obd2Pi service...")
                                try:
                                    subprocess.run(["sudo", "systemctl", "stop", "obd2Pi.service"], check=True)
                                except (subprocess.CalledProcessError, FileNotFoundError) as e:
                                    print(f"❌ Failed to stop service: {e}")
                            else:
                                # For all other actions, write the action name to the log file
                                log_file.write(f"{action}\n")
                                log_file.flush()

                except (OSError, evdev.EvdevError) as e:
                    # This typically means the controller was disconnected.
                    message = f"🎮 Gamepad disconnected ({e}). Returning to scanning loop...\n"
                    print(message.strip())
                    log_file.write(message)
                    log_file.flush()
                    try:
                        device.ungrab() # Release the device if it was grabbed
                    except:
                        pass
                    # The outer loop will now take over and call find_controller() again.

    except KeyboardInterrupt:
        print("\nExiting program.")
    except PermissionError:
        print("\n❌ PERMISSION ERROR: Cannot access input devices.")
        print("   Please run this script with 'sudo' or add your user to the 'input' group:")
        print("   sudo usermod -a -G input $USER   (and then reboot)")

if __name__ == "__main__":
    main()