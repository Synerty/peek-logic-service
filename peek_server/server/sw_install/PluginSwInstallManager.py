from peek_platform.sw_install.PluginSwInstallManagerABC import PluginSwInstallManagerABC
from peek_server.plugin.ServerPluginLoader import serverPluginLoader


class PluginSwInstallManager(PluginSwInstallManagerABC):
    def notifyOfPluginVersionUpdate(self, pluginName, targetVersion):
        serverPluginLoader.loadPlugin(pluginName)
        serverPluginLoader.buildFrontend(self)


pluginSwInstallManager = PluginSwInstallManager()
