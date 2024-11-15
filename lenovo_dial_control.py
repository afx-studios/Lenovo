import win32serviceutil
import win32service
import win32event
import servicemanager

class LenovoDialService(win32serviceutil.ServiceFramework):
    _svc_name_ = "LenovoDialControl"
    _svc_display_name_ = "Lenovo Dial Control Service"
    _svc_description_ = "Service to manage Lenovo Dial for system brightness and volume."

    def __init__(self, args):
        win32serviceutil.ServiceFramework.__init__(self, args)
        self.hWaitStop = win32event.CreateEvent(None, 0, 0, None)

    def SvcStop(self):
        self.ReportServiceStatus(win32service.SERVICE_STOP_PENDING)
        win32event.SetEvent(self.hWaitStop)

    def SvcDoRun(self):
        servicemanager.LogMsg(servicemanager.EVENTLOG_INFORMATION_TYPE,
                              servicemanager.PYS_SERVICE_STARTED,
                              (self._svc_name_, ""))
        self.run()

    def run(self):
        # Insert your existing Lenovo Dial logic here
        import lenovo_dial_control  # Your script logic

if __name__ == '__main__':
    win32serviceutil.HandleCommandLine(LenovoDialService)
