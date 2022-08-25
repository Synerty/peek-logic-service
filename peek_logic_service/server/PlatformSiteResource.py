from txhttputil.site.BasicResource import BasicResource
from vortex.VortexFactory import VortexFactory

from peek_logic_service.server.sw_download.PeekSwDownloadResource import (
    PeekSwUpdateDownloadResource,
)
from peek_logic_service.server.sw_download.PluginSwDownloadResource import (
    PluginSwDownloadResource,
)
from peek_platform import PeekPlatformConfig

platformSiteRoot = BasicResource()


def setupPlatformSite():
    # Add the platform download resource
    platformSiteRoot.putChild(
        b"peek_logic_service.sw_install.platform.download",
        PeekSwUpdateDownloadResource(),
    )

    # Add the plugin download resource
    platformSiteRoot.putChild(
        b"peek_logic_service.sw_install.plugin.download",
        PluginSwDownloadResource(),
    )
    vortexWebsocketResource = VortexFactory.createHttpWebsocketResource(
        PeekPlatformConfig.componentName
    )
    platformSiteRoot.putChild(b"vortexws", vortexWebsocketResource)
