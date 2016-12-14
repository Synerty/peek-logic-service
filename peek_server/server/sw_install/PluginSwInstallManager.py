from peek_platform.sw_install.PluginSwInstallManagerBase import PluginSwInstallManagerBase
from peek_server.plugin.ServerPluginLoader import serverPluginLoader


class PluginSwInstallManager(PluginSwInstallManagerBase):
    def notifyOfPluginVersionUpdate(self, pluginName, targetVersion):
        serverPluginLoader.loadPlugin(pluginName)
        serverPluginLoader.buildFrontend(self)


pluginSwInstallManager = PluginSwInstallManager()
