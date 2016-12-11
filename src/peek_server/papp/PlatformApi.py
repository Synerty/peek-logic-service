


class PlatformApi:
    @property
    def dbConnectString(self):
        from peek_server.PeekServerConfig import peekServerConfig
        return peekServerConfig.dbConnectString
