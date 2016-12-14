from peek_platform.sw_install.PluginSwInstallManagerBase import PluginSwInstallManagerBase
from peek_server.plugin.PluginServerLoader import pluginServerLoader


class PluginSwInstallManager(PluginSwInstallManagerBase):
    def notifyOfPluginVersionUpdate(self, pluginName, targetVersion):
        pluginServerLoader.loadPlugin(pluginName)
        pluginServerLoader.buildFrontend(self)


pluginSwInstallManager = PluginSwInstallManager()
