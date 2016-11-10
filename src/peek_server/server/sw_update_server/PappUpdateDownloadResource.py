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
from sqlalchemy.sql.expression import desc
from twisted.web.server import NOT_DONE_YET

from peek_server.storage import getPeekServerOrmSession
# from peek_server.storage.AgentData import AgentUpdateInfo
from peek_server.storage.PeekAppInfo import PeekAppInfo
from rapui.site.ResourceUtil import RapuiResource, resourceCacheAndServeStaticFile, \
    addResourceCreator

logger = logging.getLogger(__name__)


class PappUpdateDownloadResource(RapuiResource):
    isLeaf = True
    isGzipped = True

    AGENT = 1
    WORKER = 2

    def __init__(self, userAccess, component):
        RapuiResource.__init__(self, userAccess)
        self._component = component

    def render_GET(self, request):
        name = request.args.get('name', [None])[0]
        version = request.args.get('version', [None])[0]

        if not name and not version:
            msg = "Download requires peek app name, Name=%s" % name
            logger.error(msg)
            request.write(msg)
            request.finish()
            return NOT_DONE_YET

        logger.debug("Papp Download Resource GET, name=%s, version=%s",
                      name, version)

        session = getPeekServerOrmSession()
        qry = session.query(PeekAppInfo).filter(PeekAppInfo.name == name)

        try:
            if version:
                pappInfo = qry.filter(PeekAppInfo.version == version).one()
            else:
                # Choose the latest
                pappInfo = qry.order_by(desc(PeekAppInfo.id)).first()


        except NoResultFound as e:
            logger.warning("There are no builds for papp %s, version %s",
                           name, version)
            request.finish()
            return NOT_DONE_YET

        from peek_server.PeekServerConfig import peekServerConfig


        newSoftwareTar = os.path.join(peekServerConfig.pappSoftwarePath, pappInfo.fileName)

        request.responseHeaders.setRawHeaders('content-type',
                                              ['application/octet-stream'])

        return resourceCacheAndServeStaticFile(request, newSoftwareTar)


@addResourceCreator('/peek_server.sw_update_client.papp.download')
def _creatorWorker(userAccess):
    return PappUpdateDownloadResource(userAccess)
