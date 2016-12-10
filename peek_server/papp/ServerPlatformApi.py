from papp_base.PeekPlatformFrontendABC import PeekPlatformFrontendABC
from papp_base.server.PeekServerPlatformABC import PeekServerPlatformABC


class ServerPlatformApi(PeekServerPlatformABC):
    def __init__(self):
        PeekPlatformFrontendABC.__init__(self)

    @property
    def dbConnectString(self) -> str:
        from peek_server.PeekServerConfig import peekServerConfig
        return peekServerConfig.dbConnectString

    def getOtherPappApi(self, pappName):
        return None
