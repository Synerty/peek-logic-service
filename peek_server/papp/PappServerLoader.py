import logging
from typing import Type

from papp_base.PappCommonEntryHookABC import PappCommonEntryHookABC
from papp_base.server.PappServerEntryHookABC import PappServerEntryHookABC
from peek_platform.papp.PappFrontendInstallerABC import PappFrontendInstallerABC
from peek_platform.papp.PappLoaderABC import PappLoaderABC
from peek_server.papp.ServerPlatformApi import ServerPlatformApi

logger = logging.getLogger(__name__)


class PappServerLoader(PappLoaderABC, PappFrontendInstallerABC):
    _instance = None

    def __new__(cls, *args, **kwargs):
        assert cls._instance is None, "PappServerLoader is a singleton, don't construct it"
        cls._instance = PappLoaderABC.__new__(cls, *args, **kwargs)
        return cls._instance

    def __init__(self, *args, **kwargs):
        PappLoaderABC.__init__(self, *args, **kwargs)
        PappFrontendInstallerABC.__init__(self, *args, platformService="server", **kwargs)

    def loadAllPapps(self):
        PappLoaderABC.loadAllPapps(self)
        self.buildFrontend()

    @property
    def _entryHookFuncName(self) -> str:
        return "peekServerEntryHook"

    @property
    def _entryHookClassType(self):
        return PappServerEntryHookABC

    @property
    def _platformServiceNames(self) -> [str]:
        return ["server", "storage"]

    def _loadPappThrows(self, pappName: str, EntryHookClass: Type[PappCommonEntryHookABC],
                        pappRootDir: str) -> None:
        # Everyone gets their own instance of the papp API
        serverPlatformApi = ServerPlatformApi()

        pappMain = EntryHookClass(pappName=pappName,
                                  pappRootDir=pappRootDir,
                                  platform=serverPlatformApi)

        # Load the papp
        pappMain.load()

        # Configure the celery app in the worker
        # This is not the worker that will be started, it allows the worker to queue tasks
        from peek_platform.CeleryApp import configureCeleryApp
        configureCeleryApp(pappMain.celeryApp)

        # Start the Papp
        pappMain.start()

        # Add all the resources required to serve the backend site
        # And all the papp custom resources it may create
        from peek_server.backend.SiteRootResource import root as serverRootResource
        serverRootResource.putChild(pappName.encode(), serverPlatformApi.rootResource)

        self._loadedPapps[pappName] = pappMain

    def pappAdminTitleUrls(self):
        """ Papp Admin Name Urls

        @:returns a list of tuples (pappName, pappTitle, pappUrl)
        """
        data = []
        for pappName, papp in list(self._loadedPapps.items()):
            data.append((pappName, papp.title, "/%s" % pappName))

        return data


pappServerLoader = PappServerLoader()
