import inputs
import time
import sys

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
                # --- Connection Loop ---
                is_connected = False
                while not is_connected:
                    try:
                        inputs.get_gamepad() # This will raise an exception if no gamepad is found
                        is_connected = True
                        print("✅ Gamepad connected successfully.")
                    except Exception:
                        reload(inputs) # Fully reload the module to ensure a clean state
                        print("⚠️ Gamepad not found. Retrying in 5 seconds...")
                        time.sleep(5)
                
                # --- Event Processing Loop ---
                while is_connected:
                    try:
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
                                    elif event.code == 'BTN_D_UP':
                                        message = "INTERVAL_UP\n"
                                        print("D-pad UP pressed. Logging INTERVAL_UP.")
                                        log_file.write(message)
                                        log_file.flush()
                                    elif event.code == 'BTN_D_DOWN':
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
                    except (ConnectionError, OSError, IndexError, inputs.UnpluggedError):
                        # Controller disconnected
                        message = "🎮 Gamepad disconnected. Attempting to reconnect...\n"
                        print(message.strip())
                        log_file.write(message)
                        log_file.flush()
                        time.sleep(1) # Give the OS a moment to clean up stale device files
                        reload(inputs) # Fully reload the module to ensure a clean state
                        is_connected = False # This will break the event loop and go back to the connection loop
    except KeyboardInterrupt:
        print("\nExiting program.")

if __name__ == "__main__":
    main()