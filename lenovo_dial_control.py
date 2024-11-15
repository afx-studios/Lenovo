import win32serviceutil
import win32service
import win32event
import servicemanager
import time
from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume
from ctypes import cast, POINTER
import screen_brightness_control as sbc
from pynput import mouse, keyboard


class LenovoDialService(win32serviceutil.ServiceFramework):
    _svc_name_ = "LenovoDialControl"
    _svc_display_name_ = "Lenovo Dial Control Service"
    _svc_description_ = "Service to manage Lenovo Dial for system brightness and volume."

    def __init__(self, args):
        win32serviceutil.ServiceFramework.__init__(self, args)
        self.hWaitStop = win32event.CreateEvent(None, 0, 0, None)
        self.running = True

    def SvcStop(self):
        self.ReportServiceStatus(win32service.SERVICE_STOP_PENDING)
        win32event.SetEvent(self.hWaitStop)
        self.running = False

    def SvcDoRun(self):
        servicemanager.LogMsg(servicemanager.EVENTLOG_INFORMATION_TYPE,
                              servicemanager.PYS_SERVICE_STARTED,
                              (self._svc_name_, ""))
        self.run()

    def run(self):
        # Initialize volume control
        devices = AudioUtilities.GetSpeakers()
        interface = devices.Activate(IAudioEndpointVolume._iid_, None, None)
        volume = cast(interface, POINTER(IAudioEndpointVolume))
        mode = "volume"  # Default mode

        def adjust_volume(change):
            current_volume = volume.GetMasterVolumeLevelScalar()
            volume.SetMasterVolumeLevelScalar(max(0, min(1, current_volume + change)), None)

        def adjust_brightness(change):
            current_brightness = sbc.get_brightness()[0]
            sbc.set_brightness(max(0, min(100, current_brightness + change * 10)))

        def on_scroll(x, y, dx, dy):
            if mode == "volume":
                adjust_volume(dy * 0.05)  # Adjust volume based on scroll direction
            elif mode == "brightness":
                adjust_brightness(dy)  # Adjust brightness based on scroll direction

        def on_press(key):
            nonlocal mode
            try:
                if key.char == 'm':  # Toggle mode with 'm' key
                    mode = "brightness" if mode == "volume" else "volume"
                    print(f"Switched to {mode} mode.")
            except AttributeError:
                pass  # Ignore non-character keys

        # Set up input listeners
        mouse_listener = mouse.Listener(on_scroll=on_scroll)
        keyboard_listener = keyboard.Listener(on_press=on_press)
        mouse_listener.start()
        keyboard_listener.start()

        try:
            while self.running:
                time.sleep(0.1)
        except Exception as e:
            servicemanager.LogErrorMsg(str(e))
        finally:
            mouse_listener.stop()
            keyboard_listener.stop()


if __name__ == '__main__':
    win32serviceutil.HandleCommandLine(LenovoDialService)
