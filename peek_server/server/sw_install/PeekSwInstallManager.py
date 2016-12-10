from peek_platform.sw_install.PeekSwInstallManagerBase import PeekSwInstallManagerBase
from peek_server import storage
from peek_server.papp.PappServerLoader import pappServerLoader

__author__ = 'synerty'


class PeekSwInstallManager(PeekSwInstallManagerBase):

    def _stopCode(self):
        pappServerLoader.unloadAllPapps()

    def _upgradeCode(self):
        # Ensure the migration succeeds before restarting.
        from peek_server.storage import dbConn
        dbConn.closeAllSessions()
        dbConn.migratre()

    def _startCode(self):
        pappServerLoader.loadAllPapps()


peekSwInstallManager = PeekSwInstallManager()
