import time
from pynput import mouse, keyboard
import win32gui
import win32con
import ctypes
from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume
from ctypes import cast, POINTER

# Define CLSCTX_ALL since it might not be available directly from pycaw
CLSCTX_ALL = 0x23  # This is the combined value for all contexts (CLSCTX_SERVER | CLSCTX_INPROC_HANDLER)

# Setup for volume control
devices = AudioUtilities.GetSpeakers()
interface = devices.Activate(IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
volume = cast(interface, POINTER(IAudioEndpointVolume))

VOLUME_STEP = 0.05  # 5% volume step
BRIGHTNESS_STEP = 10  # This might need adjustment based on your system's behavior

def adjust_volume(change):
    """Adjusts the system volume by the specified change."""
    current_volume = volume.GetMasterVolumeLevelScalar()
    volume.SetMasterVolumeLevelScalar(min(1.0, max(0.0, current_volume + change)), None)

def set_brightness(value):
    """Sets the system brightness using registry settings. 
    Note: This might require admin privileges and might not work on all systems."""
    try:
        key = win32gui.RegOpenKeyEx(win32con.HKEY_CURRENT_USER, r"Control Panel\Desktop", 0, win32con.KEY_ALL_ACCESS)
        win32gui.RegSetValueEx(key, "PreferredUIPowerSetting", 0, win32con.REG_DWORD, value)
        win32gui.RegCloseKey(key)
        
        ctypes.windll.user32.SendMessageW(
            win32con.HWND_BROADCAST, 
            win32con.WM_SETTINGCHANGE, 
            0, 
            ctypes.c_wchar_p("Environment")
        )
    except Exception as e:
        print(f"Error adjusting brightness: {e}")

# Global variable to toggle between brightness and volume control
current_mode = "brightness"

def on_press(key):
    """Prints the key that was pressed."""
    print(f"Key pressed: {key}")

    # Toggle between brightness and volume mode with Ctrl key
    if key == keyboard.Key.ctrl_l:
        global current_mode
        current_mode = "volume" if current_mode == "brightness" else "brightness"
        print(f"Switched to {current_mode} control")

def on_click(x, y, button, pressed):
    """Prints mouse click events."""
    if pressed:
        print(f"Mouse Button {button} pressed at position ({x}, {y})")

def on_scroll(x, y, dx, dy):
    """Handles scroll events from the dial."""
    if current_mode == "brightness":
        if dy < 0:
            print("Brightness increased")
            set_brightness(0)  # For increase, might need to be 1 depending on your system
        elif dy > 0:
            print("Brightness decreased")
            set_brightness(1)  # For decrease, might need to be 0 depending on your system
    elif current_mode == "volume":
        if dy < 0:
            print("Volume increased")
            adjust_volume(VOLUME_STEP)
        elif dy > 0:
            print("Volume decreased")
            adjust_volume(-VOLUME_STEP)

if __name__ == "__main__":
    try:
        # Start the keyboard listener
        k_listener = keyboard.Listener(on_press=on_press)
        k_listener.start()

        # Start the mouse listener for scroll events
        m_listener = mouse.Listener(on_click=on_click, on_scroll=on_scroll)
        m_listener.start()

        print("Listening for HID inputs. Press Ctrl+C to exit.")
        print(f"Current mode: {current_mode}")

        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("Script was interrupted by user.")
    except Exception as e:
        print(f"An error occurred: {e}")
    finally:
        k_listener.stop()
        m_listener.stop()
        print("Listeners stopped")
