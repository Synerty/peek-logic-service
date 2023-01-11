import os
from peek_logic_service.server.sw_upload.PeekSwUploadResource import (
    PeekSwUploadResource,
)
from txhttputil.site.FileUnderlayResource import FileUnderlayResource

from vortex.VortexFactory import VortexFactory

adminSiteRoot = FileUnderlayResource()


def setupAdminSite():
    # Setup properties for serving the site
    adminSiteRoot.enableSinglePageApplication()

    import peek_admin_app

    frontendProjectDir = os.path.dirname(peek_admin_app.__file__)
    buildDir = os.path.join(frontendProjectDir, "dist")

    buildDirParent = os.path.dirname(buildDir)
    if not os.path.isdir(buildDirParent):
        raise NotADirectoryError(buildDirParent)

    # Make the dist dir, otherwise addFileSystemRoot throws an exception.
    # It rebuilds at a later date
    os.makedirs(buildDir, exist_ok=True)

    adminSiteRoot.addFileSystemRoot(buildDir)

    # Create the Admin UI vortex
    from peek_platform import PeekPlatformConfig

    # Add the platform update upload resource
    adminSiteRoot.putChild(
        b"peek_logic_service.update.platform",
        PeekSwUploadResource(PeekSwUploadResource.UPDATE_TYPE_PLATFORM),
    )

    # Add the plugin update upload resource
    adminSiteRoot.putChild(
        b"peek_logic_service.update.plugin",
        PeekSwUploadResource(PeekSwUploadResource.UPDATE_TYPE_PLUGIN),
    )

    # ---------------
    # Add the websocket to the site root
    VortexFactory.createHttpWebsocketServer(
        PeekPlatformConfig.componentName, adminSiteRoot
    )

    # ---------------
    # Setup the documents
    docSiteRoot = FileUnderlayResource()
    docSiteRoot.enableSinglePageApplication()

    import peek_admin_doc

    docProjectDir = os.path.dirname(peek_admin_doc.__file__)
    distDir = os.path.join(docProjectDir, "doc_dist")

    buildDirParent = os.path.dirname(distDir)
    if not os.path.isdir(buildDirParent):
        raise NotADirectoryError(buildDirParent)

    # Make the dist dir, otherwise addFileSystemRoot throws an exception.
    # It rebuilds at a later date
    os.makedirs(distDir, exist_ok=True)

    docSiteRoot.addFileSystemRoot(distDir)

    adminSiteRoot.putChild(b"docs", docSiteRoot)
