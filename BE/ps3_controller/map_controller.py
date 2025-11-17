import evdev
import time
import json
import os

TARGET_DEVICE_NAME = "PLAYSTATION"
MAP_FILE = "button_map.json"

# Define all the actions that need a button
ACTIONS_TO_MAP = [
    "CYCLE_LED_MODE",
    "RETRY_OBD_CONNECTION",
    "INTERVAL_UP",
    "INTERVAL_DOWN",
    "RESTART_SERVICE",
    "STOP_SERVICE",
    "EXIT_SCRIPT"
]

def find_controller():
    """Scans for and connects to the controller."""
    while True:
        print(f"⏳ Scanning for a device named '{TARGET_DEVICE_NAME}'...")
        devices = [evdev.InputDevice(path) for path in evdev.list_devices()]
        for device in devices:
            if TARGET_DEVICE_NAME in device.name:
                print(f"✅ Found controller: {device.path} - {device.name}")
                return device
        time.sleep(3)

def main():
    """Main function to guide the user through button mapping."""
    print("--- Controller Button Mapping Utility ---")
    device = find_controller()
    button_map = {}

    try:
        device.grab()
        print("\nStarting mapping process. Press the requested button firmly.")

        for action in ACTIONS_TO_MAP:
            print(f"\n>>> Press the button for: '{action}'...")
            
            # Wait for a button press event
            for event in device.read_loop():
                if event.type == evdev.ecodes.EV_KEY and event.value == 1: # 1 is 'press'
                    code = event.code
                    button_map[action] = code
                    print(f"    ✅ OK! '{action}' mapped to button code {code}.")
                    time.sleep(0.5) # Prevents accidental double-press
                    break # Move to the next action

        # Save the map to a file
        map_path = os.path.join(os.path.dirname(__file__), MAP_FILE)
        with open(map_path, "w") as f:
            json.dump(button_map, f, indent=4)

        print(f"\n\n🎉 Mapping complete! Configuration saved to '{MAP_FILE}'.")

    except KeyboardInterrupt:
        print("\nMapping cancelled.")
    finally:
        try:
            device.ungrab()
        except (OSError, NameError):
            pass

if __name__ == "__main__":
    main()
