from twisted.cred.error import LoginFailed
from twisted.internet.defer import Deferred, inlineCallbacks
from txhttputil.site.AuthCredentials import AuthCredentials


class AdminAuthChecker(AuthCredentials):

    @inlineCallbacks
    def check(self, username, password) -> Deferred:

        from peek_platform import PeekPlatformConfig
        from peek_server.plugin.PeekServerPlatformHook import PeekServerPlatformHook

        coreUserAuthAdmin = PeekServerPlatformHook(PeekPlatformConfig.pluginLoader) \
            .getOtherPluginApi("peek_core_user") \
            .adminAuth

        if username == PeekPlatformConfig.config.adminUser:
            if password != PeekPlatformConfig.config.adminPass:
                raise LoginFailed("Password incorrect for Admin recovery user")
            return

        yield coreUserAuthAdmin.check(username, password)
