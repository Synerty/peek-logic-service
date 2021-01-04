import logging

import win32service
import win32serviceutil
from twisted.internet import reactor

import peek_logic_service
from peek_platform.sw_install.PeekSwInstallManagerABC import IS_WIN_SVC

logger = logging.getLogger(__name__)


class PeekSvc(win32serviceutil.ServiceFramework):
    _svc_name_ = "peek-logic-service"
    _svc_display_name_ = "Peek Server " + peek_logic_service.__version__
    _exe_args_ = IS_WIN_SVC
    _svc_deps_ = ["RpcSs", "postgresql-x64-10", "Redis", "RabbitMQ"]

    def __init__(self, args):
        win32serviceutil.ServiceFramework.__init__(self, args)

        reactor.addSystemEventTrigger("after", "shutdown", self._notifyOfStop)

    def _notifyOfStop(self):
        self.ReportServiceStatus(win32service.SERVICE_STOPPED)

    def _notifyOfStart(self):
        self.ReportServiceStatus(win32service.SERVICE_RUNNING)

    def SvcStop(self):
        self.ReportServiceStatus(win32service.SERVICE_STOP_PENDING)
        reactor.callFromThread(reactor.stop)

    def SvcDoRun(self):
        self.ReportServiceStatus(win32service.SERVICE_START_PENDING)
        try:

            reactor.callLater(1, self._notifyOfStart)

            from peek_logic_service import run_peek_logic_service

            run_peek_logic_service.main()

        except Exception as e:
            logger.exception(e)
            raise


def main():
    win32serviceutil.HandleCommandLine(PeekSvc)


if __name__ == "__main__":
    main()
