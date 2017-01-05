import os
from peek_server.server.sw_upload.PeekSwUploadResource import PeekSwUploadResource
from txhttputil.site.FileUnderlayResource import FileUnderlayResource

from vortex.VortexFactory import VortexFactory

root = FileUnderlayResource()

def setup():
    # Setup properties for serving the site
    root.enableSinglePageApplication()

    # This dist dir is automatically generated, but check it's parent
    from peek_platform import PeekPlatformConfig
    buildDir = PeekPlatformConfig.config.feDistDir

    buildDirParent = os.path.dirname(buildDir)
    if not os.path.isdir(buildDirParent):
        raise NotADirectoryError(buildDirParent)

    # Make the dist dir, otherwise addFileSystemRoot throws an exception.
    # It rebuilds at a later date
    os.makedirs(buildDir, exist_ok=True)

    root.addFileSystemRoot(buildDir)

    # Create the Admin UI vortex
    VortexFactory.createServer(PeekPlatformConfig.componentName, root)

    # Add the platform update upload resource
    root.putChild(b'peek_server.update.platform',
                  PeekSwUploadResource(PeekSwUploadResource.UPDATE_TYPE_PLATFORM))

    # Add the plugin update upload resource
    root.putChild(b'peek_server.update.plugin',
                  PeekSwUploadResource(PeekSwUploadResource.UPDATE_TYPE_PLUGIN))