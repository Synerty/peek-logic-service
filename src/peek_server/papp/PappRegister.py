import os
import sys

from peek_server.papp.PlatformApi import PlatformApi
from rapui.vortex.Tuple import TUPLE_TYPES, removeTuplesForPackage

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

    def unloadPapp(self, pappName):
        for modName in [x for x in sys.modules.keys() if x.startswith('%s.' % pappName)]:
            del sys.modules[modName]
        del sys.modules[pappName]
        removeTuplesForPackage(pappName)

    def register(self, pappName):
        oldPapClient = PAPP_CLIENTS.get(pappName)
        if oldPapClient:
            del PAPP_CLIENTS[pappName]
            oldPapClient.stop()
            oldPapClient.unload()
            self.unloadPapp(pappName)

        platformApi = PlatformApi()

        import imp

        modPath = os.path.join(self._pappPath, pappName, pappName, "PappServerMain.py")
        PappServerMainMod = imp.load_source('%s.PappServerMain' % pappName, modPath)
        peekClient = PappServerMainMod.PappServerMain(platformApi)

        sys.path.append(os.path.join(self._pappPath, pappName))
        # pappPackage = __import__(peekAppName, fromlist=[])
        #
        # peekClient = pappPackage.makeClient(self)

        PAPP_CLIENTS[pappName] = peekClient
        peekClient.start()
        sys.path.pop()



pappRegister = PappRegister()
