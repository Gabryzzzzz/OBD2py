import pydbus
from gi.repository import GLib
import time
import sys

def get_player_proxy(bus):
    """
    Finds the first available media player provided by BlueZ over D-Bus.
    """
    try:
        # The BlueZ service name
        bus_name = 'org.bluez'
        # The path for the media player interface
        mpris_path = '/org/mpris/MediaPlayer2'

        # Get all objects managed by BlueZ
        managed_objects = bus.get(bus_name).GetManagedObjects()

        # Find the first device that exposes the media player interface
        for path, interfaces in managed_objects.items():
            if 'org.mpris.MediaPlayer2.Player' in interfaces:
                print(f"✅ Found media player at: {path}")
                # The service name for a specific player is often its device address
                player_service = f"{bus_name}.Player{path.split('/')[-1]}"
                return bus.get(bus_name, path)
    except GLib.Error as e:
        # This error happens if the service isn't running or no player is active
        if "g-dbus-error-quark" in str(e):
            return None
        raise
    return None

def on_metadata_changed(iface, changed_props, invalidated_props):
    """
    Callback function that is triggered when media metadata changes.
    """
    if 'Track' in changed_props:
        metadata = changed_props['Track']
        title = metadata.get('Title', 'No Title')
        artist = metadata.get('Artist', 'No Artist')
        print(f"\n🎵 Now Playing: {artist} - {title}")

def main():
    """
    Main function to connect to D-Bus and monitor for media player events.
    """
    loop = GLib.MainLoop()
    
    print("--- Bluetooth Media Player Monitor ---")
    
    while True:
        bus = pydbus.SystemBus() # BlueZ runs on the System bus
        player = get_player_proxy(bus)
        
        if player:
            player.onPropertiesChanged = on_metadata_changed
            print("🎧 Listening for song changes... (Press Ctrl+C to exit)")
            loop.run()
        else:
            print("⚠️ No active Bluetooth media player found. Is your phone connected for audio? Retrying in 10 seconds...")
            time.sleep(10)

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nExiting program.")
        sys.exit(0)