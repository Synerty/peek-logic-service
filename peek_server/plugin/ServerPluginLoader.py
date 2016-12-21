import logging
from typing import Type

from peek_plugin_base.PluginCommonEntryHookABC import PluginCommonEntryHookABC
from peek_plugin_base.server.PluginServerEntryHookABC import PluginServerEntryHookABC
from peek_platform.plugin.PluginFrontendInstallerABC import PluginFrontendInstallerABC
from peek_platform.plugin.PluginLoaderABC import PluginLoaderABC
from peek_server.plugin.PeekServerPlatformHook import PeekServerPlatformHook

logger = logging.getLogger(__name__)


class ServerPluginLoader(PluginLoaderABC, PluginFrontendInstallerABC):
    _instance = None

    def __new__(cls, *args, **kwargs):
        assert cls._instance is None, "ServerPluginLoader is a singleton, don't construct it"
        cls._instance = PluginLoaderABC.__new__(cls, *args, **kwargs)
        return cls._instance

    def __init__(self, *args, **kwargs):
        PluginLoaderABC.__init__(self, *args, **kwargs)
        PluginFrontendInstallerABC.__init__(self, *args, platformService="server", **kwargs)


    @property
    def _entryHookFuncName(self) -> str:
        return "peekServerEntryHook"

    @property
    def _entryHookClassType(self):
        return PluginServerEntryHookABC

    @property
    def _platformServiceNames(self) -> [str]:
        return ["server", "storage"]

    def loadAllPlugins(self):
        PluginLoaderABC.loadAllPlugins(self)
        self.buildFrontend()

    def unloadPlugin(self, pluginName: str):
        PluginLoaderABC.unloadPlugin(self, pluginName)

        # Remove the Plugin resource tree

        from peek_server.backend.SiteRootResource import root as serverRootResource
        try:
            serverRootResource.deleteChild(pluginName.encode())
        except KeyError:
            pass

    def _loadPluginThrows(self, pluginName: str, EntryHookClass: Type[PluginCommonEntryHookABC],
                        pluginRootDir: str) -> None:
        # Everyone gets their own instance of the plugin API
        platformApi = PeekServerPlatformHook()

        pluginMain = EntryHookClass(pluginName=pluginName,
                                  pluginRootDir=pluginRootDir,
                                  platform=platformApi)

        # Load the plugin
        pluginMain.load()

        # Configure the celery app in the worker
        # This is not the worker that will be started, it allows the worker to queue tasks
        from peek_platform.CeleryApp import configureCeleryApp
        configureCeleryApp(pluginMain.celeryApp)

        # Start the Plugin
        pluginMain.start()

        # Add all the resources required to serve the backend site
        # And all the plugin custom resources it may create

        from peek_server.backend.SiteRootResource import root as serverRootResource
        serverRootResource.putChild(pluginName.encode(), platformApi.rootResource)

        self._loadedPlugins[pluginName] = pluginMain


