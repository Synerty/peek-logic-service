from txhttputil.site.BasicResource import BasicResource

from peek_logic_service.server.sw_download.PeekSwDownloadResource import (
    PeekSwUpdateDownloadResource,
)
from peek_logic_service.server.sw_download.PluginSwDownloadResource import (
    PluginSwDownloadResource,
)

platformSiteRoot = BasicResource()


def setupPlatformSite():
    # Add the platform download resource
    platformSiteRoot.putChild(
        b"peek_logic_service.sw_install.platform.download",
        PeekSwUpdateDownloadResource(),
    )

    # Add the plugin download resource
    platformSiteRoot.putChild(
        b"peek_logic_service.sw_install.plugin.download", PluginSwDownloadResource()
    )
