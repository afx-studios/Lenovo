import time
from pynput import mouse, keyboard
import win32gui
import win32con
import ctypes
from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume
from ctypes import cast, POINTER

# Setup for volume control
devices = AudioUtilities.GetSpeakers()
interface = devices.Activate(IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
volume = cast(interface, POINTER(IAudioEndpointVolume))

VOLUME_STEP = 0.05  # 5% volume step
BRIGHTNESS_STEP = 10  # 10% brightness step

def adjust_volume(change):
    current_volume = volume.GetMasterVolumeLevelScalar()
    volume.SetMasterVolumeLevelScalar(min(1.0, max(0.0, current_volume + change)), None)

def set_brightness(value):
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

def on_press(key):
    print(f"Key pressed: {key}")

def on_click(x, y, button, pressed):
    if pressed:
        print(f"Mouse Button {button} pressed at position ({x}, {y})")

def on_scroll(x, y, dx, dy):
    if dy < 0:
        print("Dial turned left (increase brightness)")
        set_brightness(0)  # Decrease might be 0, confirm this
    elif dy > 0:
        print("Dial turned right (decrease brightness)")
        set_brightness(1)  # Increase might be 1, confirm this
    elif dx < 0:
        print("Dial turned left (decrease volume)")
        adjust_volume(-VOLUME_STEP)
    elif dx > 0:
        print("Dial turned right (increase volume)")
        adjust_volume(VOLUME_STEP)

if __name__ == "__main__":
    try:
        # Start the keyboard listener
        k_listener = keyboard.Listener(on_press=on_press)
        k_listener.start()

        # Start the mouse listener for scroll events
        m_listener = mouse.Listener(on_click=on_click, on_scroll=on_scroll)
        m_listener.start()

        print("Listening for HID inputs. Press Ctrl+C to exit.")

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
