import inputs
import time
import sys

import subprocess
from importlib import reload
# Analog stick deadzone to prevent drift
STICK_DEADZONE = 4000 
LOG_FILE = "controller_log.txt"

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
            
            # Main loop to handle connection and events
            while True: 
                try:
                    # --- Connection Attempt ---
                    # This will raise an exception if no gamepad is found,
                    # which is caught below to handle the "not found" case.
                    if not inputs.devices.gamepads:
                         # Force a check that raises an error if no gamepads are present
                        inputs.get_gamepad()
                    
                    print("✅ Gamepad connected. Monitoring for events...")

                    # --- Event Processing Loop ---
                    while True:
                        events = inputs.get_gamepad()
                        # If get_gamepad() returns an empty list after a disconnect,
                        # it means the controller is gone. We must raise an error
                        # to trigger the reconnection logic.
                        if not events:
                            raise ConnectionError("Gamepad disconnected (no events).")
                        for event in events:
                            # Update the stick state when an 'Absolute' event is received
                            if event.ev_type == 'Absolute':
                                # This block can be used for analog stick handling in the future
                                button_states[event.code] = event.state
                            # Handle button presses
                            elif event.ev_type == 'Key':
                                # Get the previous state of the button, defaulting to 0 (released)
                                prev_state = button_states.get(event.code, 0)
                                # Check if the button is being pressed now and was released before
                                if event.state == 1 and prev_state == 0:
                                    if event.code == 'BTN_START':
                                        print("Start button pressed. Exiting.")
                                        log_file.write("EXIT_BY_START_BUTTON\n")
                                        log_file.flush()
                                        sys.exit(0) # Exit the program cleanly
                                    elif event.code == 'BTN_SOUTH': # 'X' button
                                        message = "CYCLE_LED_MODE\n"
                                        print("X button pressed. Logging CYCLE_LED_MODE.")
                                        log_file.write(message)
                                        log_file.flush()
                                    elif event.code == 'BTN_WEST': # Square button
                                        message = "RETRY_OBD_CONNECTION\n"
                                        print("West button pressed. Logging RETRY_OBD_CONNECTION.")
                                        log_file.write(message)
                                        log_file.flush()
                                    elif event.code == 'BTN_TR': # R1 button
                                        message = "RESTART_SERVICE\n"
                                        print("R1 button pressed. Restarting obd2Pi service...")
                                        try:
                                            # Execute the system command directly
                                            subprocess.run(["sudo", "systemctl", "restart", "obd2Pi.service"], check=True)
                                        except (subprocess.CalledProcessError, FileNotFoundError) as e:
                                            print(f"❌ Failed to restart service: {e}")
                                        log_file.flush()
                                    elif event.code == 'BTN_TR2': # R2 button
                                        print("R2 button pressed. Stopping obd2Pi service...")
                                        try:
                                            # Execute the system command directly to stop the service
                                            subprocess.run(["sudo", "systemctl", "stop", "obd2Pi.service"], check=True)
                                        except (subprocess.CalledProcessError, FileNotFoundError) as e:
                                            print(f"❌ Failed to stop service: {e}")
                                        log_file.flush()
                                    elif event.code == 'BTN_DPAD_UP':
                                        message = "INTERVAL_UP\n"
                                        print("D-pad UP pressed. Logging INTERVAL_UP.")
                                        log_file.write(message)
                                        log_file.flush()
                                    elif event.code == 'BTN_DPAD_DOWN':
                                        message = "INTERVAL_DOWN\n"
                                        print("D-pad DOWN pressed. Logging INTERVAL_DOWN.")
                                        log_file.write(message)
                                        log_file.flush()
                                    else:
                                        message = f"{event.code}\n"
                                        print(message.strip())
                                        log_file.write(message)
                                        log_file.flush()
                                button_states[event.code] = event.state                    
                except (ConnectionError, OSError, IndexError, inputs.UnpluggedError, inputs.UnknownEventCode):
                    # This block now catches initial connection failures and subsequent disconnections.
                    message = "🎮 Gamepad not found or disconnected. Retrying in 5 seconds...\n"
                    print(message.strip())
                    
                    # Only write to log if the file is still open
                    if not log_file.closed:
                        log_file.write(message)
                        log_file.flush()

                    time.sleep(5) # Wait before retrying
                    try:
                        reload(inputs) # Fully reload the module to ensure a clean state
                    except FileNotFoundError:
                        # This can happen in a race condition if device files are gone but not yet fully deregistered.
                        print("⚠️ Race condition during device scan. Retrying...")
    except KeyboardInterrupt:
        print("\nExiting program.")

if __name__ == "__main__":
    main()