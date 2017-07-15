import logging
from typing import Type, Tuple

import os
from peek_platform.frontend.WebBuilder import WebBuilder
from peek_platform.plugin.PluginLoaderABC import PluginLoaderABC
from peek_plugin_base.PluginCommonEntryHookABC import PluginCommonEntryHookABC
from peek_plugin_base.server.PluginServerEntryHookABC import PluginServerEntryHookABC
from peek_plugin_base.server.PluginServerStorageEntryHookABC import \
    PluginServerStorageEntryHookABC
from peek_plugin_base.server.PluginServerWorkerEntryHookABC import \
    PluginServerWorkerEntryHookABC
from peek_server.plugin.PeekServerPlatformHook import PeekServerPlatformHook
# from peek_platform.plugin.PluginFrontendInstallerABC import PluginFrontendInstallerABC
from twisted.internet.defer import inlineCallbacks

logger = logging.getLogger(__name__)


class ServerPluginLoader(PluginLoaderABC):
    _instance = None

    def __new__(cls, *args, **kwargs):
        assert cls._instance is None, "ServerPluginLoader is a singleton, don't construct it"
        cls._instance = PluginLoaderABC.__new__(cls, *args, **kwargs)
        return cls._instance

    def __init__(self, *args, **kwargs):
        PluginLoaderABC.__init__(self, *args, **kwargs)

    @property
    def _entryHookFuncName(self) -> str:
        return "peekServerEntryHook"

    @property
    def _entryHookClassType(self):
        return PluginServerEntryHookABC

    @property
    def _platformServiceNames(self) -> [str]:
        return ["server", "storage"]

    @inlineCallbacks
    def loadOptionalPlugins(self):
        yield PluginLoaderABC.loadOptionalPlugins(self)

        import peek_admin
        frontendProjectDir = os.path.dirname(peek_admin.__file__)

        from peek_platform import PeekPlatformConfig

        webBuilder = WebBuilder(frontendProjectDir,
                                "peek-admin",
                                PeekPlatformConfig.config,
                                self._loadedPlugins.values())
        webBuilder.build()

    def unloadPlugin(self, pluginName: str):
        PluginLoaderABC.unloadPlugin(self, pluginName)

        # Remove the Plugin resource tree

        from peek_server.backend.SiteRootResource import root as serverRootResource
        try:
            serverRootResource.deleteChild(pluginName.encode())
        except KeyError:
            pass

    @inlineCallbacks
    def _loadPluginThrows(self, pluginName: str,
                          EntryHookClass: Type[PluginCommonEntryHookABC],
                          pluginRootDir: str,
                          requiresService: Tuple[str, ...]) -> PluginCommonEntryHookABC:
        # Everyone gets their own instance of the plugin API
        platformApi = PeekServerPlatformHook(pluginName)

        pluginMain = EntryHookClass(pluginName=pluginName,
                                    pluginRootDir=pluginRootDir,
                                    platform=platformApi)

        # Load the plugin
        yield pluginMain.load()

        if isinstance(pluginMain, PluginServerWorkerEntryHookABC):
            # Configure the celery app in the worker
            # This is not the worker that will be started, it allows the worker to queue tasks
            from peek_platform.ConfigCeleryApp import configureCeleryApp
            from peek_platform import PeekPlatformConfig
            configureCeleryApp(pluginMain.celeryApp, PeekPlatformConfig.config)

        # Check the implementation
        elif "worker" in requiresService:
            raise Exception("Plugin %s requires 'worker' service."
                            " It must now inherit PluginServerWorkerEntryHookABC"
                            " in its PluginServerEntryHook implementation")

        if isinstance(pluginMain, PluginServerStorageEntryHookABC):

            metadata = pluginMain.dbMetadata
            schemaName = (
                pluginName
                    .replace("peek_plugin_", "pl_")
                    .replace("peek_core_", "core_")
            )
            if metadata.schema != schemaName:
                raise Exception("Peek plugin %s db schema name is %s, should be %s"
                                % (pluginName, metadata.schema, schemaName))

            # Create/Migrate the database schema
            pluginMain._migrateStorageSchema(pluginMain.dbMetadata)

        # Check the implementation
        elif "storage" in requiresService:
            raise Exception("Plugin %s requires 'storage' service."
                            " It must now inherit PluginServerStorageEntryHookMixin"
                            " in its PluginServerEntryHook implementation")

        # Add all the resources required to serve the backend site
        # And all the plugin custom resources it may create

        from peek_server.backend.SiteRootResource import root as adminSiteRoot
        adminSiteRoot.putChild(pluginName.encode(), platformApi.rootAdminResource)

        from peek_server.server.PeekServerPlatformRootResource import root as platformRoot
        platformRoot.putChild(pluginName.encode(), platformApi.rootServerResource)

        self._loadedPlugins[pluginName] = pluginMain
