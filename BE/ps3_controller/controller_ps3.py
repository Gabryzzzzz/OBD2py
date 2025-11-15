from inputs import get_gamepad
import time
import sys

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
        with open(LOG_FILE, "a") as log_file:
            log_file.write(f"--- New Session Started at {time.ctime()} ---\n")
            log_file.flush()
            while True:
                # Get all available events from the gamepad
                try:
                    events = get_gamepad()
                except Exception:
                    message = "Gamepad not found. Please connect a gamepad.\n"
                    print(message.strip())
                    log_file.write(message)
                    log_file.flush()
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
                                message = f"{event.code}\n"
                                print(message.strip())
                                log_file.write(message)
                                log_file.flush()

                        # TRIGGERS: Check for transition from 0 to a pressed state
                        if event.code in ('ABS_Z', 'ABS_RZ'): # Corresponds to LT/L2 and RT/R2
                            if event.state > 0 and prev_state == 0:
                                message = f"{event.code}\n"
                                print(message.strip())
                                log_file.write(message)
                                log_file.flush()

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
                            else:
                                message = f"{event.code}\n"
                                print(message.strip())
                                log_file.write(message)
                                log_file.flush()
                        button_states[event.code] = event.state
    except KeyboardInterrupt:
        print("\nExiting program.")

if __name__ == "__main__":
    main()