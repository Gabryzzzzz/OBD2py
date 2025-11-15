from inputs import get_gamepad
from time import sleep

def controller_ps3():
    sleep(5)
    # To store the state of the buttons (0=released, 1=pressed)
    button_states = {}

    print("Controller active. Press a button or move the stick. (Ctrl+C to exit)")

    try:
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
                            print(f"Button {event.code} was pressed")
                    button_states[event.code] = event.state
    except KeyboardInterrupt:
        print("\nExiting program.")
