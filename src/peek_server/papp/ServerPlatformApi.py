from papp_base.server.ServerPlatformApiBase import ServerPlatformApiBase
from peek_platform.papp.PappPlatformApiResourceBase import PappPlatformApiResourceBase


class ServerPlatformApi(ServerPlatformApiBase, PappPlatformApiResourceBase):
    def __init__(self):
        PappPlatformApiResourceBase.__init__(self)

    @property
    def dbConnectString(self) -> str:
        from peek_server.PeekServerConfig import peekServerConfig
        return peekServerConfig.dbConnectString
