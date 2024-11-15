import ctypes
import time
from ctypes.wintypes import BOOL, DWORD, HANDLE

# Constants
ES_CONTINUOUS = 0x80000000
ES_SYSTEM_REQUIRED = 0x00000001
ES_DISPLAY_REQUIRED = 0x00000002

# Import for volume control
from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume
from ctypes import cast, POINTER

# Setup volume control
devices = AudioUtilities.GetSpeakers()
interface = devices.Activate(IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
volume = cast(interface, POINTER(IAudioEndpointVolume))

VOLUME_STEP = 0.05  # 5% volume step

# Brightness control using SetThreadExecutionState
def set_brightness(state):
    kernel32 = ctypes.windll.kernel32
    kernel32.SetThreadExecutionState.argtypes =[DWORD]
    kernel32.SetThreadExecutionState.restype = DWORD
    return kernel32.SetThreadExecutionState(state)

# Functions to adjust volume and brightness
def increase_volume():
    current_volume = volume.GetMasterVolumeLevelScalar()
    volume.SetMasterVolumeLevelScalar(min(1.0, current_volume + VOLUME_STEP), None)
    print("Volume increased")

def decrease_volume():
    current_volume = volume.GetMasterVolumeLevelScalar()
    volume.SetMasterVolumeLevelScalar(max(0.0, current_volume - VOLUME_STEP), None)
    print("Volume decreased")

def increase_brightness():
    current_state = set_brightness(ES_CONTINUOUS | ES_DISPLAY_REQUIRED)
    if current_state == (ES_CONTINUOUS | ES_DISPLAY_REQUIRED):
        print("Brightness increased")
    else:
        print("Failed to increase brightness")

def decrease_brightness():
    current_state = set_brightness(ES_CONTINUOUS)  # Turn off display required state
    if current_state == ES_CONTINUOUS:
        print("Brightness decreased")
    else:
        print("Failed to decrease brightness")

# Main loop for testing (replace with your HID event logic)
while True:
    command = input("Enter 'u' to increase, 'd' to decrease, 'b' for brightness, 'q' to quit: ")
    if command == 'u':
        increase_volume()
    elif command == 'd':
        decrease_volume()
    elif command == 'b':
        increase_brightness()
    elif command == 'q':
        print("Exiting...")
        break
    elif command == 'l':
        decrease_brightness()
    time.sleep(0.1)
