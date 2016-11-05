import imp
import sys

import os

from peek_server.papp.ServerPlatformApi import ServerPlatformApi


class PappLoaderBase():
    _instance = None

    def __new__(cls, *args, **kwargs):
        assert cls._instance is None, "PappServerLoader is a singleton, don't construct it"
        cls._instance = cls()
        return cls._instance

    def __init__(self):
        self._loadedPapps = {}

    def listPapps(self):
        def pappTest(name):
            if not name.startswith("papp_"):
                return False
            return os.path.isdir(os.path.join(self._pappPath, name))

        papps = os.listdir(self._pappPath)
        papps = filter(pappTest, papps)
        return papps

    def loadAllPapps(self):
        for pappName in self.listPapps():
            self.loadPapp(pappName)

    def _unloadPappPackage(self, pappName, oldLoadedPapp):

        # Stop and remove the Papp
        del self._loadedPapps[pappName]
        oldLoadedPapp.stop()
        oldLoadedPapp.unload()
        self.unloadPapp(pappName)

        # Unload the packages
        loadedSubmodules = [modName
                            for modName in sys.modules.keys()
                            if modName.startswith('%s.' % pappName)]

        for modName in loadedSubmodules:
            del sys.modules[modName]

        del sys.modules[pappName]
