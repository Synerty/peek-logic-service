from peek_server.server.sw_download.PappSwDownloadResource import PappSwDownloadResource
from peek_server.server.sw_download.PeekSwDownloadResource import \
    PeekSwUpdateDownloadResource
from txhttputil.site.BasicResource import BasicResource
from vortex.VortexResource import VortexResource

root = BasicResource()

# Add in a vortex
root.putChild(b'vortex', VortexResource())

root.putChild(b'peek_server.sw_install.platform.download',
              PeekSwUpdateDownloadResource())

root.putChild(b'peek_server.sw_install.papp.download'
              , PappSwDownloadResource())

