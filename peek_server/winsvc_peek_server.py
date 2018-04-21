import platform

import peek_server
from peek_platform.util.LogUtil import setupServiceLogOutput

try:
    import win32serviceutil
    import win32service
    import win32event
except ImportError as e:
    if platform.system() is "Windows":
        raise

from twisted.internet import reactor

from peek_server import run_peek_server


class PeekSvc(win32serviceutil.ServiceFramework):
    _svc_name_ = "peek_server"
    _svc_display_name_ = "Peek Server " + peek_server.__version__

    def __init__(self, args):
        win32serviceutil.ServiceFramework.__init__(self, args)
        self.hWaitStop = win32event.CreateEvent(None, 0, 0, None)

        reactor.addSystemEventTrigger('after', 'shutdown', self._notifyOfStop)

    def _notifyOfStop(self, _):
        self.ReportServiceStatus(win32service.SERVICE_STOPPED)

    def _notifyOfStart(self, _):
        self.ReportServiceStatus(win32service.SERVICE_RUNNING)

    def SvcStop(self):
        self.ReportServiceStatus(win32service.SERVICE_STOP_PENDING)
        win32event.SetEvent(self.hWaitStop)
        reactor.callFromThread(reactor.stop)

    def SvcDoRun(self):
        self.ReportServiceStatus(win32service.SERVICE_START_PENDING)
        d = run_peek_server.main()
        d.addBoth(self._notifyOfStart)
        reactor.run()


def main():
    setupServiceLogOutput(PeekSvc._svc_name_)
    win32serviceutil.HandleCommandLine(PeekSvc)


if __name__ == '__main__':
    main()
