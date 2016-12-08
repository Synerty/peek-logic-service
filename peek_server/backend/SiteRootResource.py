from peek_server.PeekServerConfig import peekServerConfig
from peek_server.server.sw_upload.PeekSwUploadResource import PeekSwUploadResource
from txhttputil.site.FileUnderlayResource import FileUnderlayResource
from vortex.VortexResource import VortexResource

root = FileUnderlayResource()

# Setup properties for serving the site
root.enableSinglePageApplication()
root.addFileSystemRoot(peekServerConfig.feDistDir)

# Add the vortex
root.putChild(b'vortex', VortexResource())

# Add the
root.putChild(b'peek_server.update.platform',
              PeekSwUploadResource(PeekSwUploadResource.UPDATE_TYPE_PLATFORM))

root.putChild(b'peek_server.update.papp',
              PeekSwUploadResource(PeekSwUploadResource.UPDATE_TYPE_PAPP))