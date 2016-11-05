import imp
import sys
from _collections import defaultdict

import os

from peek_server.papp.ServerPlatformApi import ServerPlatformApi
from rapui.site.ResourceUtil import removeResourcePaths, registeredResourcePaths
from rapui.vortex.PayloadIO import PayloadIO
from rapui.vortex.Tuple import removeTuplesForTupleNames, \
    registeredTupleNames, tupleForTupleName


class PappLoader():
    _instance = None

    def __new__(cls, *args, **kwargs):
        assert cls._instance is None, "PappLoader is a singleton, don't construct it"
        cls._instance = cls()
        return cls._instance

    def __init__(self):
        from peek_server.PeekServerConfig import peekServerConfig
        self._pappPath = peekServerConfig.pappSoftwarePath

        self._loadedPapps = {}

        self._rapuiEndpointInstancesByPappName = defaultdict(list)
        self._rapuiResourcePathsByPappName = defaultdict(list)
        self._rapuiTupleNamesByPappName = defaultdict(list)

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

    def unloadPapp(self, pappName):
        oldPapClient = self._loadedPapps.get(pappName)

        if not oldPapClient:
            return

        # Remove the registered endpoints
        for endpoint in self._rapuiEndpointInstancesByPappName[pappName]:
            PayloadIO().remove(endpoint)
        del self._rapuiEndpointInstancesByPappName[pappName]

        # Remove the registered paths
        removeResourcePaths(self._rapuiResourcePathsByPappName[pappName])
        del self._rapuiResourcePathsByPappName[pappName]

        # Remove the registered tuples
        removeTuplesForTupleNames(self._rapuiTupleNamesByPappName[pappName])
        del self._rapuiTupleNamesByPappName[pappName]

        # Stop and remove the Papp
        del self._loadedPapps[pappName]
        oldPapClient.stop()
        oldPapClient.unload()
        self.unloadPapp(pappName)

        # Unload the packages
        loadedSubmodules = [modName
                            for modName in sys.modules.keys()
                            if modName.startswith('%s.' % pappName)]

        for modName in loadedSubmodules:
            del sys.modules[modName]

        del sys.modules[pappName]

    def loadPapp(self, pappName):
        self.unloadPapp(pappName)

        # Make note of the initial registrations for this papp
        endpointInstancesBefore = set(PayloadIO().endpoints)
        resourcePathsBefore = set(registeredResourcePaths())
        tupleNamesBefore = set(registeredTupleNames())

        print tupleNamesBefore

        # Everyone gets their own instance of the platform API
        serverPlatformApi = ServerPlatformApi()

        modPath = os.path.join(self._pappPath, pappName, pappName, "PappServerMain.py")
        PappServerMainMod = imp.load_source('%s.PappServerMain' % pappName, modPath)
        peekClient = PappServerMainMod.PappServerMain(serverPlatformApi)

        sys.path.append(os.path.join(self._pappPath, pappName))
        # pappPackage = __import__(peekAppName, fromlist=[])
        #
        # peekClient = pappPackage.makeClient(self)

        self._loadedPapps[pappName] = peekClient
        peekClient.start()
        sys.path.pop()

        # Make note of the final registrations for this papp
        self._rapuiEndpointInstancesByPappName[pappName] = list(
            set(PayloadIO().endpoints) - endpointInstancesBefore)

        self._rapuiResourcePathsByPappName[pappName] = list(
            set(registeredResourcePaths()) - resourcePathsBefore)

        self._rapuiTupleNamesByPappName[pappName] = list(
            set(registeredTupleNames()) - tupleNamesBefore)

        self.sanityCheckPapp(pappName)

    def sanityCheckPapp(self, pappName):
        ''' Sanity Check Papp

        This method ensures that all the things registed for this papp are
        prefixed by it's pappName, EG papp_noop
        '''

        # All endpoint filters must have the 'papp' : 'papp_name' in them
        for endpoint in self._rapuiEndpointInstancesByPappName[pappName]:
            filt = endpoint.filt
            if 'papp' not in filt and filt['papp'] != pappName:
                raise Exception("Payload endpoint does not contan 'papp':'%s'\n%s"
                                % (pappName, filt))

        # all resource paths must start with their pappName
        for path in self._rapuiResourcePathsByPappName[pappName]:
            if not path.strip('/').startswith(pappName):
                raise Exception("Resource path does not start with '%s'\n%s"
                                % (pappName, path))

        # all tuple names must start with their pappName
        for tupleName in self._rapuiTupleNamesByPappName[pappName]:
            TupleCls = tupleForTupleName(tupleName)
            if not tupleName.startswith(pappName):
                raise Exception("Tuple name does not start with '%s', %s (%s)"
                                % (pappName, tupleName, TupleCls.__name__))


pappLoader = PappLoader()
