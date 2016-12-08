from papp_base.PeekPlatformFrontendABC import PeekPlatformFrontendABC
from papp_base.server.PeekServerPlatformABC import PeekServerPlatformABC


class ServerPlatformApi(PeekServerPlatformABC, PeekPlatformFrontendABC):
    def __init__(self):
        PeekPlatformFrontendABC.__init__(self)

    @property
    def dbConnectString(self) -> str:
        from peek_server.PeekServerConfig import peekServerConfig
        return peekServerConfig.dbConnectString

