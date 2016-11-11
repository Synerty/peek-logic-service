"""
 *
 *  Copyright Synerty Pty Ltd 2013
 *
 *  This software is proprietary, you are not free to copy
 *  or redistribute this code in any format.
 *
 *  All rights to this software are reserved by 
 *  Synerty Pty Ltd
 *
"""
import logging

import os
from sqlalchemy.orm.exc import NoResultFound
from twisted.web.server import NOT_DONE_YET

from peek_server.storage import getPeekServerOrmSession
# from peek_server.storage.AgentData import AgentUpdateInfo
from peek_platform import PeekPlatformConfig
from rapui.site.ResourceUtil import RapuiResource, resourceCacheAndServeStaticFile, \
    addResourceCreator

logger = logging.getLogger(__name__)


class PeekSwUpdateDownloadResource(RapuiResource):
    isLeaf = True
    isGzipped = True

    def render_GET(self, request):
        componentName = request.args.get('name', [None])[0]
        version = request.args.get('version', [None])[0]

        if not componentName and not version:
            msg = "Download requires sw_update_server name and version, Name=%s, Version=%s"
            msg %= (componentName, version)
            logger.error(msg)
            request.write(msg)
            request.finish()
            return NOT_DONE_YET

        logger.debug("Peek Platform Download Resource GET, name=%s, version=%s",
                     componentName, version)

        newSoftwareTar = os.path.join(PeekPlatformConfig.config.platformSoftwarePath,
                                      'peek_platform_%s' % version,
                                      '%s_%s.tar.bz2' % (componentName, version))

        request.responseHeaders.setRawHeaders('content-type',
                                              ['application/octet-stream'])

        return resourceCacheAndServeStaticFile(request, newSoftwareTar)


@addResourceCreator('/peek_server.sw_install.platform.download')
def _creatorAgent(userAccess):
    return PeekSwUpdateDownloadResource(userAccess)
