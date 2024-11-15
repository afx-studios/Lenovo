from pynput import mouse, keyboard
from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume
from ctypes import cast, POINTER
import screen_brightness_control as sbc
import time

# Initialize volume control
devices = AudioUtilities.GetSpeakers()
interface = devices.Activate(IAudioEndpointVolume._iid_, None, None)
volume = cast(interface, POINTER(IAudioEndpointVolume))

# Set initial mode
mode = "volume"  # Default mode

# Functions to adjust volume and brightness
def adjust_volume(change):
    current_volume = volume.GetMasterVolumeLevelScalar()
    volume.SetMasterVolumeLevelScalar(max(0, min(1, current_volume + change)), None)

def adjust_brightness(change):
    current_brightness = sbc.get_brightness()[0]
    sbc.set_brightness(max(0, min(100, current_brightness + change * 10)))

# Function to handle mouse scroll events (for Lenovo Dial rotation)
def on_scroll(x, y, dx, dy):
    if mode == "volume":
        adjust_volume(dy * 0.05)  # Adjust volume based on scroll direction
    elif mode == "brightness":
        adjust_brightness(dy)  # Adjust brightness based on scroll direction

# Function to handle keyboard events (for Lenovo Dial button)
def on_press(key):
    global mode
    try:
        if key.char == 'm':  # Toggle mode with 'm' key (replace with actual button event)
            mode = "brightness" if mode == "volume" else "volume"
            print(f"Switched to {mode} mode.")
    except AttributeError:
        pass  # Ignore non-character keys

# Set up event listeners
mouse_listener = mouse.Listener(on_scroll=on_scroll)
keyboard_listener = keyboard.Listener(on_press=on_press)
mouse_listener.start()
keyboard_listener.start()

# Keep the script running
print("Lenovo Dial Control Running...")
try:
    while True:
        time.sleep(0.1)
except KeyboardInterrupt:
    print("Exiting...")
    mouse_listener.stop()
    keyboard_listener.stop()
