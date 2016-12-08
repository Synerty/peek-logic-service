import logging
import sys
from importlib.util import find_spec

from jsoncfg.value_mappers import require_string
from peek_platform.papp.PappLoaderABC import PappLoaderABC
from peek_server.papp.ServerPlatformApi import ServerPlatformApi

logger = logging.getLogger(__name__)


class PappServerLoader(PappLoaderABC):
    _instance = None

    def __new__(cls, *args, **kwargs):
        assert cls._instance is None, "PappServerLoader is a singleton, don't construct it"
        cls._instance = PappLoaderABC.__new__(cls, *args, **kwargs)
        return cls._instance

    def _loadPappThrows(self, pappName: str, pappPackageJson: str):
        self.unloadPapp(pappName)

        # Everyone gets their own instance of the papp API
        serverPlatformApi = ServerPlatformApi()

        # Load up the entry hook details from the papp_package.json
        entryHookPackage = pappPackageJson.config.server.entryHookPackage(require_string)
        entryHookClass = pappPackageJson.config.server.entryHookClass(require_string)

        modSpec = find_spec(entryHookPackage)
        if not modSpec:
            raise Exception("Can not load package %s for Peek App %s",
                            entryHookPackage, pappName)

        # Load the package
        Mod = modSpec.loader.load_module()

        pappMain = Mod.PappServerMain(serverPlatformApi)

        self._loadedPapps[pappName] = pappMain

        # Configure the celery app in the worker
        # This is not the worker that will be started, it allows the worker to queue tasks

        from peek_platform.CeleryApp import configureCeleryApp
        configureCeleryApp(pappMain.celeryApp)

        pappMain.start()
        sys.path.pop()

        # Add all the resources required to serve the backend site
        # And all the papp custom resources it may create
        from peek_server.backend.SiteRootResource import root as serverRootResource
        serverRootResource.putChild(pappName.encode(), serverPlatformApi.rootResource)

    def pappAdminTitleUrls(self):
        """ Papp Admin Name Urls

        @:returns a list of tuples (pappName, pappTitle, pappUrl)
        """
        data = []
        for pappName, papp in list(self._loadedPapps.items()):
            data.append((pappName, papp.title, "/%s" % pappName))

        return data


pappServerLoader = PappServerLoader()
