import inputs
import time
import sys
import os
import subprocess
# Analog stick deadzone to prevent drift
STICK_DEADZONE = 4000 
LOG_FILE = "controller_log.txt"

def find_gamepad_device():
    """
    Waits for a gamepad device to appear in /dev/input/ and returns its path.
    This is a more robust way to handle connection delays on Linux.
    """
    print("⏳ Waiting for a gamepad device to be created by the OS...")
    while True:
        try:
            # Force a clean re-scan by creating a new DeviceManager instance.
            devices = inputs.DeviceManager()
            gamepads = devices.gamepads

            if gamepads:
                print(f"✅ Found {len(gamepads)} gamepad(s):")
                for i, gamepad in enumerate(gamepads):
                    print(f"  [{i}]: {gamepad}")
            # This will raise an IndexError if no gamepads are found by the library
            # which is a good way to check if a device is ready.
            return gamepads[0]
        except (IndexError, FileNotFoundError):
            # If not found, wait and let the loop try again.
            time.sleep(2)

def main():
    # To store the state of the buttons (0=released, 1=pressed)
    button_states = {}

    print("Controller active. Press a button or move the stick. (Ctrl+C to exit)")
    print(f"Logging button presses to {LOG_FILE}")

    try:
        # Open the log file in append mode ('a') to add to it without deleting existing content
        with open(LOG_FILE, "a", encoding="utf-8") as log_file:
            log_file.write(f"--- New Session Started at {time.ctime()} ---\n")
            log_file.flush()
            
            while True: # Main loop for the script's lifetime
                gamepad = None
                try:
                    gamepad = find_gamepad_device()
                    print(f"✅ Gamepad connected: {gamepad.name}. Monitoring for events...")
                except PermissionError:
                    print("❌ Permission Denied. Cannot read controller device file.")
                    print("   Run 'sudo usermod -a -G input $USER' and reboot your Pi.")
                    time.sleep(10) # Wait longer before retrying

                # --- Event Processing Loop ---
                try:
                    while True:
                        events = gamepad.read()
                        for event in events:
                            if event.ev_type == 'Absolute':
                                button_states[event.code] = event.state
                            elif event.ev_type == 'Key':
                                prev_state = button_states.get(event.code, 0)
                                if event.state == 1 and prev_state == 0:
                                    if event.code == 'BTN_START':
                                        print("Start button pressed. Exiting.")
                                        log_file.write("EXIT_BY_START_BUTTON\n")
                                        log_file.flush()
                                        sys.exit(0)
                                    elif event.code == 'BTN_SOUTH': # 'X' button
                                        message = "CYCLE_LED_MODE\n"
                                        print("X button pressed. Logging CYCLE_LED_MODE.")
                                        log_file.write(message)
                                    elif event.code == 'BTN_WEST': # Square button
                                        message = "RETRY_OBD_CONNECTION\n"
                                        print("West button pressed. Logging RETRY_OBD_CONNECTION.")
                                        log_file.write(message)
                                    elif event.code == 'BTN_TR': # R1 button
                                        print("R1 button pressed. Restarting obd2Pi service...")
                                        try:
                                            subprocess.run(["sudo", "systemctl", "restart", "obd2Pi.service"], check=True)
                                        except (subprocess.CalledProcessError, FileNotFoundError) as e:
                                            print(f"❌ Failed to restart service: {e}")
                                    elif event.code == 'BTN_TR2': # R2 button
                                        print("R2 button pressed. Stopping obd2Pi service...")
                                        try:
                                            subprocess.run(["sudo", "systemctl", "stop", "obd2Pi.service"], check=True)
                                        except (subprocess.CalledProcessError, FileNotFoundError) as e:
                                            print(f"❌ Failed to stop service: {e}")
                                    elif event.code == 'BTN_DPAD_UP':
                                        message = "INTERVAL_UP\n"
                                        print("D-pad UP pressed. Logging INTERVAL_UP.")
                                        log_file.write(message)
                                    elif event.code == 'BTN_DPAD_DOWN':
                                        message = "INTERVAL_DOWN\n"
                                        print("D-pad DOWN pressed. Logging INTERVAL_DOWN.")
                                        log_file.write(message)
                                    else:
                                        message = f"{event.code}\n"
                                        print(message.strip())
                                        log_file.write(message)
                                    
                                    log_file.flush()
                                button_states[event.code] = event.state
                except (OSError, inputs.UnpluggedError) as e:
                    # This block catches disconnections.
                    message = f"🎮 Gamepad disconnected ({e}). Returning to connection loop...\n"
                    print(message.strip())
                    if not log_file.closed:
                        log_file.write(message)
                        log_file.flush()
                    # The outer 'while True' loop will now take over and start searching for a gamepad again.
                    
    except KeyboardInterrupt:
        print("\nExiting program.")

if __name__ == "__main__":
    main()