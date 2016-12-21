from peek_platform import PeekPlatformConfig
from peek_platform.sw_install.PluginSwInstallManagerBase import PluginSwInstallManagerBase


class PluginSwInstallManager(PluginSwInstallManagerBase):
    def notifyOfPluginVersionUpdate(self, pluginName, targetVersion):
        PeekPlatformConfig.pluginLoader.loadPlugin(pluginName)
        PeekPlatformConfig.pluginLoader.buildFrontend()

