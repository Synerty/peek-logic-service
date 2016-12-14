from peek_platform.sw_install.PeekSwInstallManagerBase import PeekSwInstallManagerBase
from peek_server import storage
from peek_server.plugin.PluginServerLoader import pluginServerLoader

__author__ = 'synerty'


class PeekSwInstallManager(PeekSwInstallManagerBase):

    def _stopCode(self):
        pluginServerLoader.unloadAllPlugins()

    def _upgradeCode(self):
        # Ensure the migration succeeds before restarting.
        from peek_server.storage import dbConn
        dbConn.closeAllSessions()
        dbConn.migratre()

    def _startCode(self):
        pluginServerLoader.loadAllPlugins()


peekSwInstallManager = PeekSwInstallManager()
