from peek_server.server.sw_upload.PeekSwUploadResource import PeekSwUploadResource
from txhttputil.site.FileUnderlayResource import FileUnderlayResource
from vortex.VortexResource import VortexResource

root = FileUnderlayResource()
# rootResource.addFileSystemRoot()

root.putChild(b'vortex', VortexResource())

root.putChild(b'peek_server.update.platform',
              PeekSwUploadResource(PeekSwUploadResource.UPDATE_TYPE_PLATFORM))

root.putChild(b'peek_server.update.papp',
              PeekSwUploadResource(PeekSwUploadResource.UPDATE_TYPE_PAPP))