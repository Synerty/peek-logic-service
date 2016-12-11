import os
import sys

from peek_server.papp.PlatformApi import PlatformApi

PAPP_CLIENTS = {}


class PappRegister():
    def __init__(self):
        from peek_server.PeekServerConfig import peekServerConfig
        self._pappPath = peekServerConfig.pappSoftwarePath

    def listPapps(self):
        def pappTest(name):
            if not name.startswith("papp_"):
                return False
            return os.path.isdir(os.path.join(self._pappPath, name))

        papps = os.listdir(self._pappPath)
        papps = filter(pappTest, papps)
        return papps

    def registerAll(self):
        for pappName in self.listPapps():
            self.register(pappName)

    def register(self, peekAppName):
        oldPapClient = PAPP_CLIENTS.get(peekAppName)
        if oldPapClient:
            del PAPP_CLIENTS[peekAppName]
            oldPapClient.stop()

        platformApi = PlatformApi()

        import imp

        modPath = os.path.join(self._pappPath, peekAppName, peekAppName, "PappMain.py")
        PappMainMod = imp.load_source('%s.PappMain' % peekAppName,modPath)
        peekClient = PappMainMod.PappMain(platformApi)

        sys.path.append(os.path.join(self._pappPath, peekAppName))
        # pappPackage = __import__(peekAppName, fromlist=[])
        #
        # peekClient = pappPackage.makeClient(self)

        PAPP_CLIENTS[peekAppName] = peekClient
        peekClient.start()
        sys.path.pop()


pappRegister = PappRegister()
