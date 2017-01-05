from peek_server.server.sw_download.PluginSwDownloadResource import PluginSwDownloadResource
from peek_server.server.sw_download.PeekSwDownloadResource import \
    PeekSwUpdateDownloadResource
from txhttputil.site.BasicResource import BasicResource

from vortex.VortexFactory import VortexFactory
from vortex.VortexResource import VortexResource

root = BasicResource()

def setup():

    # Create the Platform data exchange vortex
    from peek_platform import PeekPlatformConfig
    VortexFactory.createServer(PeekPlatformConfig.componentName, root)

    # Add the platform download resource
    root.putChild(b'peek_server.sw_install.platform.download',
                  PeekSwUpdateDownloadResource())

    # Add the plugin download resource
    root.putChild(b'peek_server.sw_install.plugin.download'
                  , PluginSwDownloadResource())

