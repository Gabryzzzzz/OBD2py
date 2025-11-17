import time
import sys
import subprocess
import evdev
from evdev import ecodes

LOG_FILE = "controller_log.txt"
TARGET_DEVICE_NAME = "PLAYSTATION"

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

def main():
    """
    Main function to find the controller and process its events.
    """
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
                        print(evdev.categorize(event))

                        # We only care about key presses (event.value == 1)
                        if event.type == ecodes.EV_KEY and event.value == 1:
                            message = None
                            
                            if event.code == ecodes.BTN_START:
                                print("Start button pressed. Exiting.")
                                log_file.write("EXIT_BY_START_BUTTON\n")
                                log_file.flush()
                                sys.exit(0)
                            elif event.code == ecodes.BTN_SOUTH: # 'X' button
                                message = "CYCLE_LED_MODE"
                                print("X button pressed. Logging CYCLE_LED_MODE.")
                            elif event.code == ecodes.BTN_WEST: # Square button
                                message = "RETRY_OBD_CONNECTION"
                                print("West button pressed. Logging RETRY_OBD_CONNECTION.")
                            elif event.code == ecodes.BTN_TR: # R1 button
                                print("R1 button pressed. Restarting obd2Pi service...")
                                try:
                                    subprocess.run(["sudo", "systemctl", "restart", "obd2Pi.service"], check=True)
                                except (subprocess.CalledProcessError, FileNotFoundError) as e:
                                    print(f"❌ Failed to restart service: {e}")
                            elif event.code == ecodes.BTN_TR2: # R2 button
                                print("R2 button pressed. Stopping obd2Pi service...")
                                try:
                                    subprocess.run(["sudo", "systemctl", "stop", "obd2Pi.service"], check=True)
                                except (subprocess.CalledProcessError, FileNotFoundError) as e:
                                    print(f"❌ Failed to stop service: {e}")
                            elif event.code == ecodes.BTN_DPAD_UP:
                                message = "INTERVAL_UP"
                                print("D-pad UP pressed. Logging INTERVAL_UP.")
                            elif event.code == ecodes.BTN_DPAD_DOWN:
                                message = "INTERVAL_DOWN"
                                print("D-pad DOWN pressed. Logging INTERVAL_DOWN.")
                            
                            if message:
                                log_file.write(f"{message}\n")
                                log_file.flush()

                except (OSError, evdev.errors.EvdevError) as e:
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