import imp
import logging
import sys
from _collections import defaultdict

import os

from peek_platform.papp.PappLoaderBase import PappLoaderBase
from peek_server.papp.ServerPlatformApi import ServerPlatformApi
from peek_server.server.sw_version.PappSwVersionInfoUtil import getLatestPappVersionInfos
from rapui.site.ElementUtil import addPageElement
from rapui.site.ResourceUtil import removeResourcePaths, registeredResourcePaths, \
    addResourceCreator
from rapui.vortex.PayloadIO import PayloadIO
from rapui.vortex.Tuple import removeTuplesForTupleNames, \
    registeredTupleNames, tupleForTupleName

logger = logging.getLogger(__name__)


class PappServerLoader(PappLoaderBase):
    _instance = None

    def __new__(cls, *args, **kwargs):
        assert cls._instance is None, "PappServerLoader is a singleton, don't construct it"
        cls._instance = PappLoaderBase.__new__(cls)
        return cls._instance

    def __init__(self):
        PappLoaderBase.__init__(self)

        from peek_server.PeekServerConfig import peekServerConfig
        self._pappPath = peekServerConfig.pappSoftwarePath

        self._rapuiEndpointInstancesByPappName = defaultdict(list)
        self._rapuiResourcePathsByPappName = defaultdict(list)
        self._rapuiTupleNamesByPappName = defaultdict(list)

    def unloadPapp(self, pappName):
        oldLoadedPapp = self._loadedPapps.get(pappName)

        if not oldLoadedPapp:
            return

        # Remove the Papp resource creator
        removeResourcePaths(pappName)

        # Remove the admin page element
        from peek_server.admin.app.PeekAdmAppElement import removePappAdminPage
        removePappAdminPage(pappName)

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

        self._unloadPappPackage(pappName, oldLoadedPapp)

    def _loadPappThrows(self, pappName):
        self.unloadPapp(pappName)

        pappVersionInfo = getLatestPappVersionInfos(name=pappName)
        if not pappVersionInfo:
            logger.warning("Papp version info for %s is missing, loading skipped",
                           pappName)
            return

        pappVersionInfo = pappVersionInfo[0]

        # Make note of the initial registrations for this papp
        endpointInstancesBefore = set(PayloadIO().endpoints)
        resourcePathsBefore = set(registeredResourcePaths())
        tupleNamesBefore = set(registeredTupleNames())

        # Everyone gets their own instance of the papp API
        serverPlatformApi = ServerPlatformApi()

        srcDir = os.path.join(self._pappPath, pappVersionInfo.dirName, 'cpython')
        sys.path.append(srcDir)

        modPath = os.path.join(srcDir, pappName, "PappServerMain.py")
        if not os.path.exists(modPath) and os.path.exists(modPath + "c"):  # .pyc
            PappServerMainMod = imp.load_compiled('%s.PappServerMain' % pappName,
                                                  modPath + 'c')
        else:
            PappServerMainMod = imp.load_source('%s.PappServerMain' % pappName,
                                                modPath)

        pappMain = PappServerMainMod.PappServerMain(serverPlatformApi)

        self._loadedPapps[pappName] = pappMain

        # Configure the celery app in the worker
        # This is not the worker that will be started, it allows the worker to queue tasks

        from peek_platform.CeleryApp import configureCeleryApp
        configureCeleryApp(pappMain.celeryApp)

        pappMain.start()
        sys.path.pop()

        # Add all the resources required to serve the admin site
        # And all the papp custom resources it may create
        addResourceCreator(pappName.encode("UTF-8"))(
            serverPlatformApi._PappPlatformApiResourceBase__createPappRootResource)

        # Add the page element, for angular routing for the papp_xxx page
        from peek_server.admin.app.PeekAdmAppElement import addPappAdminPage
        addPappAdminPage(pappName)

        # Make note of the final registrations for this papp
        self._rapuiEndpointInstancesByPappName[pappName] = list(
            set(PayloadIO().endpoints) - endpointInstancesBefore)

        self._rapuiResourcePathsByPappName[pappName] = list(
            set(registeredResourcePaths()) - resourcePathsBefore)

        self._rapuiTupleNamesByPappName[pappName] = list(
            set(registeredTupleNames()) - tupleNamesBefore)

        self.sanityCheckServerPapp(pappName)

    def sanityCheckServerPapp(self, pappName):
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
            if not path.strip(b'/').startswith(pappName.encode("UTF-8")):
                raise Exception("Resource path does not start with '%s'\n%s"
                                % (pappName, path))

        # all tuple names must start with their pappName
        for tupleName in self._rapuiTupleNamesByPappName[pappName]:
            TupleCls = tupleForTupleName(tupleName)
            if not tupleName.startswith(pappName):
                raise Exception("Tuple name does not start with '%s', %s (%s)"
                                % (pappName, tupleName, TupleCls.__name__))

    def notifyOfPappVersionUpdate(self, pappName, pappVersion):
        logger.info("Received PAPP update for %s version %s", pappName, pappVersion)
        return self.loadPapp(pappName)

    def pappAdminTitleUrls(self):
        """ Papp Admin Name Urls

        @:returns a list of tuples (pappName, pappTitle, pappUrl)
        """
        data = []
        for pappName, papp in list(self._loadedPapps.items()):
            data.append((pappName, papp.title, "/%s" % pappName))

        return data


pappServerLoader = PappServerLoader()
