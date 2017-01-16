from peek_platform import PeekPlatformConfig
from peek_plugin_base.PeekPlatformFrontendHookABC import PeekPlatformFrontendHookABC
from peek_plugin_base.server.PeekServerPlatformHookABC import PeekServerPlatformHookABC


class PeekServerPlatformHook(PeekServerPlatformHookABC):
    def __init__(self):
        PeekPlatformFrontendHookABC.__init__(self)

    @property
    def dbConnectString(self) -> str:
        from peek_platform import PeekPlatformConfig
        return PeekPlatformConfig.config.dbConnectString

    def getOtherPluginApi(self, pluginName):
        serverPluginLoader = PeekPlatformConfig.pluginLoader

        otherPlugin = serverPluginLoader.pluginEntryHook(pluginName)
        if not otherPlugin:
            return None

        from peek_plugin_base.server.PluginServerEntryHookABC import \
            PluginServerEntryHookABC

        assert isinstance(otherPlugin, PluginServerEntryHookABC), (
            "Not an instance of PluginServerEntryHookABC")


        return otherPlugin.publishedServerApi
