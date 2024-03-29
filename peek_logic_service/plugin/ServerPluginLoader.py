import logging
from typing import Type, Tuple, List

from twisted.internet.defer import inlineCallbacks

from peek_platform.plugin.PluginLoaderABC import PluginLoaderABC
from peek_plugin_base.PluginCommonEntryHookABC import PluginCommonEntryHookABC
from peek_plugin_base.server.PluginLogicEntryHookABC import PluginLogicEntryHookABC
from peek_plugin_base.server.PluginServerStorageEntryHookABC import (
    PluginServerStorageEntryHookABC,
)
from peek_plugin_base.server.PluginServerWorkerEntryHookABC import (
    PluginServerWorkerEntryHookABC,
)
from peek_logic_service.plugin.PeekServerPlatformHook import PeekServerPlatformHook
from peek_logic_service.plugin.ServerFrontendLoadersMixin import (
    ServerFrontendLoadersMixin,
)

logger = logging.getLogger(__name__)


class ServerPluginLoader(PluginLoaderABC, ServerFrontendLoadersMixin):
    _instance = None

    def __new__(cls, *args, **kwargs):
        assert (
            cls._instance is None
        ), "ServerPluginLoader is a singleton, don't construct it"
        cls._instance = PluginLoaderABC.__new__(cls, *args, **kwargs)
        return cls._instance

    def __init__(self, *args, **kwargs):
        PluginLoaderABC.__init__(self, *args, **kwargs)

    @property
    def _entryHookFuncName(self) -> str:
        return "peekLogicEntryHook"

    @property
    def _entryHookClassType(self):
        return PluginLogicEntryHookABC

    @property
    def _platformServiceNames(self) -> List[str]:
        return ["logic", "storage"]

    @inlineCallbacks
    def loadOptionalPlugins(self):
        yield PluginLoaderABC.loadOptionalPlugins(self)

        yield from self._buildAdminSite(self._loadedPlugins.values())
        yield from self._buildAdminDocs(self._loadedPlugins.values())

    def unloadPlugin(self, pluginName: str):
        PluginLoaderABC.unloadPlugin(self, pluginName)

        self._unloadPluginFromAdminSite(pluginName)

    @inlineCallbacks
    def _loadPluginThrows(
        self,
        pluginName: str,
        EntryHookClass: Type[PluginCommonEntryHookABC],
        pluginRootDir: str,
        requiresService: Tuple[str, ...],
    ) -> PluginCommonEntryHookABC:
        # Everyone gets their own instance of the plugin API
        platformApi = PeekServerPlatformHook(pluginName)

        pluginMain = EntryHookClass(
            pluginName=pluginName, pluginRootDir=pluginRootDir, platform=platformApi
        )

        # Load the plugin
        yield pluginMain.load()

        if (
            not isinstance(pluginMain, PluginServerWorkerEntryHookABC)
            and "worker" in requiresService
        ):
            raise Exception(
                "Plugin %s requires 'worker' service."
                " It must now inherit PluginServerWorkerEntryHookABC"
                " in its PluginLogicEntryHook implementation"
            )

        if isinstance(pluginMain, PluginServerStorageEntryHookABC):

            metadata = pluginMain.dbMetadata
            schemaName = pluginName.replace("peek_plugin_", "pl_").replace(
                "peek_core_", "core_"
            )
            if metadata.schema != schemaName:
                raise Exception(
                    "Peek plugin %s db schema name is %s, should be %s"
                    % (pluginName, metadata.schema, schemaName)
                )

            # Create/Migrate the database schema
            pluginMain._migrateStorageSchema(pluginMain.dbMetadata)

        # Check the implementation
        elif "storage" in requiresService:
            raise Exception(
                "Plugin %s requires 'storage' service."
                " It must now inherit PluginServerStorageEntryHookMixin"
                " in its PluginLogicEntryHook implementation"
            )

        # Add all the resources required to serve the backend site
        # And all the plugin custom resources it may create

        from peek_logic_service.backend.AdminSiteResource import (
            adminSiteRoot as adminSiteRoot,
        )

        adminSiteRoot.putChild(pluginName.encode(), platformApi.rootAdminResource)

        from peek_logic_service.server.PlatformSiteResource import (
            platformSiteRoot as platformRoot,
        )

        platformRoot.putChild(pluginName.encode(), platformApi.rootServerResource)

        self._loadedPlugins[pluginName] = pluginMain
