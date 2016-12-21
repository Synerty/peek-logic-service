from peek_server.server.sw_download.PluginSwDownloadResource import PluginSwDownloadResource
from peek_server.server.sw_download.PeekSwDownloadResource import \
    PeekSwUpdateDownloadResource
from txhttputil.site.BasicResource import BasicResource
from vortex.VortexResource import VortexResource

root = BasicResource()

def setup():

    # Add in a vortex
    root.putChild(b'vortex', VortexResource())

    root.putChild(b'peek_server.sw_install.platform.download',
                  PeekSwUpdateDownloadResource())

    root.putChild(b'peek_server.sw_install.plugin.download'
                  , PluginSwDownloadResource())

