from pynput import mouse, keyboard
from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume
from ctypes import cast, POINTER
from comtypes import CLSCTX_ALL  # Import CLSCTX_ALL
import screen_brightness_control as sbc
import time

# Initialize volume control
devices = AudioUtilities.GetSpeakers()
interface = devices.Activate(
    IAudioEndpointVolume._iid_, CLSCTX_ALL, None
)  # Use CLSCTX_ALL
volume = cast(interface, POINTER(IAudioEndpointVolume))

# Set initial mode
mode = "volume"

# Functions to adjust volume and brightness


def adjust_volume(change):
    current_volume = volume.GetMasterVolumeLevelScalar()
    new_volume = current_volume + change
    new_volume = max(0, min(1, new_volume))  # Ensure volume is within bounds
    volume.SetMasterVolumeLevelScalar(new_volume, None)


def adjust_brightness(change):
    current_brightness = sbc.get_brightness()[0]
    new_brightness = current_brightness + change * 10
    new_brightness = max(0, min(100, new_brightness))  # Ensure brightness is within bounds
    sbc.set_brightness(new_brightness)


# Function to handle mouse scroll events
def on_scroll(x, y, dx, dy):
    if mode == "volume":
        adjust_volume(dy * 0.05)
    elif mode == "brightness":
        adjust_brightness(dy)


# Function to handle keyboard events
def on_press(key):
    global mode
    try:
        if key.char == "m":
            mode = "brightness" if mode == "volume" else "volume"
            print(f"Switched to {mode} mode.")
    except AttributeError:
        pass


# Set up event listeners
mouse_listener = mouse.Listener(on_scroll=on_scroll)
keyboard_listener = keyboard.Listener(on_press=on_press)
mouse_listener.start()
keyboard_listener.start()

print("Lenovo Dial Control Running...")
try:
    while True:
        time.sleep(0.1)
except KeyboardInterrupt:
    print("Exiting...")
    mouse_listener.stop()
    keyboard_listener.stop()
