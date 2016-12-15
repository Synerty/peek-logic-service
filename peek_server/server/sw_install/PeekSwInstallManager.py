from peek_platform.sw_install.PeekSwInstallManagerABC import PeekSwInstallManagerABC
from peek_server import storage
from peek_server.plugin.ServerPluginLoader import serverPluginLoader

__author__ = 'synerty'


class PeekSwInstallManager(PeekSwInstallManagerABC):

    def _stopCode(self):
        serverPluginLoader.unloadAllPlugins()

    def _upgradeCode(self):
        # Ensure the migration succeeds before restarting.
        from peek_server.storage import dbConn
        dbConn.closeAllSessions()
        dbConn.migratre()

    def _startCode(self):
        serverPluginLoader.loadAllPlugins()


peekSwInstallManager = PeekSwInstallManager()
