from txhttputil.site.BasicResource import BasicResource

from peek_server.server.sw_download.PeekSwDownloadResource import \
    PeekSwUpdateDownloadResource
from peek_server.server.sw_download.PluginSwDownloadResource import PluginSwDownloadResource

root = BasicResource()

def setup():

    # Add the platform download resource
    root.putChild(b'peek_server.sw_install.platform.download',
                  PeekSwUpdateDownloadResource())

    # Add the plugin download resource
    root.putChild(b'peek_server.sw_install.plugin.download'
                  , PluginSwDownloadResource())

