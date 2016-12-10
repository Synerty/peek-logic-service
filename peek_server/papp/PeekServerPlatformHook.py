from papp_base.PeekPlatformFrontendHookABC import PeekPlatformFrontendHookABC
from papp_base.server.PeekServerPlatformHookABC import PeekServerPlatformHookABC


class PeekServerPlatformHook(PeekServerPlatformHookABC):
    def __init__(self):
        PeekPlatformFrontendHookABC.__init__(self)

    @property
    def dbConnectString(self) -> str:
        from peek_server.PeekServerConfig import peekServerConfig
        return peekServerConfig.dbConnectString

    def getOtherPappApi(self, pappName):
        return None
