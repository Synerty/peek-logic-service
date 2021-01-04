import logging
import os

from peek_platform.build_doc.DocBuilder import DocBuilder
from peek_platform.build_frontend.WebBuilder import WebBuilder

logger = logging.getLogger(__name__)


class ServerFrontendLoadersMixin:
    def _buildAdminSite(self, loadedPlugins):
        from peek_platform import PeekPlatformConfig

        try:
            import peek_admin_app

            frontendProjectDir = os.path.dirname(peek_admin_app.__file__)
        except:
            logger.warning(
                "Skipping builds of peek-admin-app" ", the package can not be imported"
            )
            return

        webBuilder = WebBuilder(
            frontendProjectDir,
            "peek-admin-app",
            PeekPlatformConfig.config,
            loadedPlugins,
        )
        yield webBuilder.build()

    def _buildAdminDocs(self, loadedPlugins):
        # --------------------
        # Prepare the Admin Docs
        from peek_platform import PeekPlatformConfig

        try:
            import peek_admin_doc

            docProjectDir = os.path.dirname(peek_admin_doc.__file__)

        except:
            logger.warning(
                "Skipping builds of peek_admin_doc" ", the package can not be imported"
            )
            return

        docBuilder = DocBuilder(
            docProjectDir, "peek-admin-doc", PeekPlatformConfig.config, loadedPlugins
        )
        yield docBuilder.build()

    def _unloadPluginFromAdminSite(self, pluginName):
        # JJC - This doesn't seem right, maybe if it was removing it from the platform
        # JJC - I think this is old code

        # Remove the Plugin resource tree
        from peek_logic_service.backend.AdminSiteResource import adminSiteRoot

        try:
            adminSiteRoot.deleteChild(pluginName.encode())
        except KeyError:
            pass
