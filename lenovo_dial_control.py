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

# Global variables
current_mode = "volume"  # Start with volume control
current_brightness = 50  # Track brightness level (0-100)

def adjust_volume(change):
    """Adjusts the system volume by the specified change."""
    try:
        current_volume = volume.GetMasterVolumeLevelScalar()
        new_volume = min(1.0, max(0.0, current_volume + change))
        volume.SetMasterVolumeLevelScalar(new_volume, None)
        print(f"Volume: {'▂' * int(new_volume * 20)} {int(new_volume * 100)}%")
    except Exception as e:
        print(f"Error adjusting volume: {e}")

def set_brightness(value):
    """Sets the system brightness using Windows API."""
    try:
        global current_brightness
        key = win32gui.RegOpenKeyEx(win32con.HKEY_CURRENT_USER, r"Control Panel\Desktop", 0, win32con.KEY_ALL_ACCESS)
        win32gui.RegSetValueEx(key, "PreferredUIPowerSetting", 0, win32con.REG_DWORD, value)
        win32gui.RegCloseKey(key)
        
        # Update brightness tracking
        if value == 0:  # Increase
            current_brightness = min(100, current_brightness + BRIGHTNESS_STEP)
        else:  # Decrease
            current_brightness = max(0, current_brightness - BRIGHTNESS_STEP)
            
        # Visual feedback
        print(f"Brightness: {'▂' * int(current_brightness/5)} {current_brightness}%")
        
        # Notify system of change
        ctypes.windll.user32.SendMessageW(
            win32con.HWND_BROADCAST, 
            win32con.WM_SETTINGCHANGE, 
            0, 
            ctypes.c_wchar_p("Environment")
        )
    except Exception as e:
        print(f"Error adjusting brightness: {e}")

def on_press(key):
    """Handles key press events."""
    global current_mode
    try:
        # Toggle between volume and brightness control with Ctrl key
        if key == keyboard.Key.ctrl_l:
            current_mode = "brightness" if current_mode == "volume" else "volume"
            print(f"\nSwitched to {current_mode.upper()} control mode")
            # Show current level after mode switch
            if current_mode == "volume":
                current_volume = volume.GetMasterVolumeLevelScalar()
                print(f"Volume: {'▂' * int(current_volume * 20)} {int(current_volume * 100)}%")
            else:
                print(f"Brightness: {'▂' * int(current_brightness/5)} {current_brightness}%")
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
        # Clear console and show welcome message
        print("\033[H\033[J")  # Clear screen
        print("=== Lenovo Dial Control ===")
        print("Use the dial to adjust volume/brightness")
        print("Press left Ctrl to switch between modes")
        print("Press Ctrl+C to exit")
        print(f"Current mode: {current_mode.upper()}")
        
        # Show initial volume level
        current_vol = volume.GetMasterVolumeLevelScalar()
        print(f"Volume: {'▂' * int(current_vol * 20)} {int(current_vol * 100)}%")
        
        # Start listeners
        keyboard_listener = keyboard.Listener(on_press=on_press)
        keyboard_listener.start()
        
        mouse_listener = mouse.Listener(on_scroll=on_scroll)
        mouse_listener.start()

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
