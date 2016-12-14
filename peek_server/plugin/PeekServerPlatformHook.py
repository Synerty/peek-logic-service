from peek_plugin_base.PeekPlatformFrontendHookABC import PeekPlatformFrontendHookABC
from peek_plugin_base.server.PeekServerPlatformHookABC import PeekServerPlatformHookABC


class PeekServerPlatformHook(PeekServerPlatformHookABC):
    def __init__(self):
        PeekPlatformFrontendHookABC.__init__(self)

    @property
    def dbConnectString(self) -> str:
        from peek_server.PeekServerConfig import peekServerConfig
        return peekServerConfig.dbConnectString

    def getOtherPluginApi(self, pluginName):
        return None
