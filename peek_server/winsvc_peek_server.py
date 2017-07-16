import platform

try:
    import win32serviceutil
    import win32service
    import win32event
    import servicemanager
    # import socket
except ImportError as e:
    if platform.system() is "Windows":
        raise

from twisted.internet import reactor

from peek_server import run_peek_server


class PeekSvc(win32serviceutil.ServiceFramework):
    _svc_name_ = "peek_server"
    _svc_display_name_ = "Peek Server"

    def __init__(self, args):
        win32serviceutil.ServiceFramework.__init__(self, args)
        self.hWaitStop = win32event.CreateEvent(None, 0, 0, None)
        # socket.setdefaulttimeout(120)

    def SvcStop(self):
        self.ReportServiceStatus(win32service.SERVICE_STOP_PENDING)
        win32event.SetEvent(self.hWaitStop)
        reactor.callLater(0, reactor.stop)

    def SvcDoRun(self):
        servicemanager.LogMsg(servicemanager.EVENTLOG_INFORMATION_TYPE,
                              servicemanager.PYS_SERVICE_STARTED,
                              (self._svc_name_, ''))
        run_peek_server.main()


if __name__ == '__main__':
    win32serviceutil.HandleCommandLine(PeekSvc)
