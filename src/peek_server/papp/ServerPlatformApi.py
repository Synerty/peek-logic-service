from peek_platform.papp.PappPlatformApiResourceBase import PappPlatformApiResourceBase
from rapui.site.RapuiStaticResources import RapuiStaticResources


class ServerPlatformApi(PappPlatformApiResourceBase):
    def __init__(self):
        PappPlatformApiResourceBase.__init__(self)

    @property
    def dbConnectString(self):
        from peek_server.PeekServerConfig import peekServerConfig
        return peekServerConfig.dbConnectString
