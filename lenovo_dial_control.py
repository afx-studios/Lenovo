from pynput import keyboard
from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume
from ctypes import cast, POINTER
from comtypes import CLSCTX_ALL
import screen_brightness_control as sbc
import time

# Initialize volume control
devices = AudioUtilities.GetSpeakers()
interface = devices.Activate(IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
volume = cast(interface, POINTER(IAudioEndpointVolume))

# Set initial mode
mode = "volume"

# Functions to adjust volume and brightness
def adjust_volume(change):
    current_volume = volume.GetMasterVolumeLevelScalar()
    new_volume = current_volume + change
    new_volume = max(0, min(1, new_volume))
    volume.SetMasterVolumeLevelScalar(new_volume, None)
    print(f"Volume adjusted to: {new_volume:.2f}")  # Log volume change

def adjust_brightness(change):
    current_brightness = sbc.get_brightness()[0]
    new_brightness = current_brightness + change * 10
    new_brightness = max(0, min(100, new_brightness))
    sbc.set_brightness(new_brightness)
    print(f"Brightness adjusted to: {new_brightness}")  # Log brightness change

# Function to handle keyboard events
def on_press(key):
    global mode
    try:
        if key.char == '-':  # Volume down
            print("Minus key pressed")  # Log key press
            if mode == "volume":
                adjust_volume(-0.05)
        elif key.char == '=':  # Volume up
            print("Equals key pressed")  # Log key press
            if mode == "volume":
                adjust_volume(0.05)
        elif key.char == 'm':  # Switch mode
            print("M key pressed")  # Log key press
            mode = "brightness" if mode == "volume" else "volume"
            print(f"Switched to {mode} mode.")
    except AttributeError:
        if key == keyboard.Key.ctrl:  # Brightness down
            print("Control key pressed")  # Log key press
            if mode == "brightness":
                adjust_brightness(-1)
        elif key == keyboard.Key.left_windows:  # Brightness up
            print("Left Windows key pressed")  # Log key press
            if mode == "brightness":
                adjust_brightness(1)

# Set up keyboard listener
keyboard_listener = keyboard.Listener(on_press=on_press)
keyboard_listener.start()

print("Lenovo Dial Control Running...")
try:
    keyboard_listener.join()
except KeyboardInterrupt:
    print("Exiting...")
    keyboard_listener.stop()
