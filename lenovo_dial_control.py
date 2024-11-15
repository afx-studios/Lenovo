import time
from pynput import mouse, keyboard
import win32gui
import win32con
import ctypes
from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume
from comtypes import CLSCTX_ALL
from ctypes import cast, POINTER

# Setup for volume control
devices = AudioUtilities.GetSpeakers()
interface = devices.Activate(IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
volume = cast(interface, POINTER(IAudioEndpointVolume))

# Constants for adjustments
VOLUME_STEP = 0.05  # 5% volume step
BRIGHTNESS_STEP = 10  # 10% brightness step

# Global variable to track current control mode
current_mode = "volume"  # Start with volume control

def adjust_volume(change):
    """Adjusts the system volume by the specified change."""
    try:
        current_volume = volume.GetMasterVolumeLevelScalar()
        volume.SetMasterVolumeLevelScalar(min(1.0, max(0.0, current_volume + change)), None)
        print(f"Volume {'increased' if change > 0 else 'decreased'} to {int(current_volume * 100)}%")
    except Exception as e:
        print(f"Error adjusting volume: {e}")

def set_brightness(value):
    """Sets the system brightness using Windows API."""
    try:
        key = win32gui.RegOpenKeyEx(win32con.HKEY_CURRENT_USER, r"Control Panel\Desktop", 0, win32con.KEY_ALL_ACCESS)
        win32gui.RegSetValueEx(key, "PreferredUIPowerSetting", 0, win32con.REG_DWORD, value)
        win32gui.RegCloseKey(key)
        
        # Notify the system of the change
        ctypes.windll.user32.SendMessageW(
            win32con.HWND_BROADCAST, 
            win32con.WM_SETTINGCHANGE, 
            0, 
            ctypes.c_wchar_p("Environment")
        )
        print(f"Brightness {'increased' if value == 0 else 'decreased'}")
    except Exception as e:
        print(f"Error adjusting brightness: {e}")

def on_press(key):
    """Handles key press events."""
    global current_mode
    try:
        # Toggle between volume and brightness control with Ctrl key
        if key == keyboard.Key.ctrl_l:
            current_mode = "brightness" if current_mode == "volume" else "volume"
            print(f"Switched to {current_mode} control mode")
        
        # Print key info for debugging
        if hasattr(key, 'char'):
            print(f"Key pressed: {key.char}")
        else:
            print(f"Special key pressed: {key}")
    except Exception as e:
        print(f"Error handling key press: {e}")

def on_scroll(x, y, dx, dy):
    """Handles scroll events from the dial."""
    try:
        if current_mode == "volume":
            if dy < 0:
                adjust_volume(VOLUME_STEP)
            elif dy > 0:
                adjust_volume(-VOLUME_STEP)
        else:  # brightness mode
            if dy < 0:
                set_brightness(0)  # Increase brightness
            elif dy > 0:
                set_brightness(1)  # Decrease brightness
    except Exception as e:
        print(f"Error handling scroll: {e}")

if __name__ == "__main__":
    try:
        # Start keyboard listener
        keyboard_listener = keyboard.Listener(on_press=on_press)
        keyboard_listener.start()

        # Start mouse listener for scroll events
        mouse_listener = mouse.Listener(on_scroll=on_scroll)
        mouse_listener.start()

        print("Lenovo Dial Control Running...")
        print("Use the dial to adjust volume/brightness")
        print("Press left Ctrl to switch between volume and brightness control")
        print("Press Ctrl+C to exit")
        print(f"Current mode: {current_mode}")

        # Keep the script running
        while True:
            time.sleep(0.1)

    except KeyboardInterrupt:
        print("\nExiting...")
    except Exception as e:
        print(f"An error occurred: {e}")
    finally:
        keyboard_listener.stop()
        mouse_listener.stop()
        print("Listeners stopped")
