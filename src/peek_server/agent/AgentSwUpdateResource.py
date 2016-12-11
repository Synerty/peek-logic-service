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

from peek_server.storage import getNovaOrmSession
# from peek_server.storage.AgentData import AgentUpdateInfo
from rapui.site.ResourceUtil import RapuiResource, resourceCacheAndServeStaticFile, \
    addResourceCreator

logger = logging.getLogger(__name__)

class AgentSwUpdateResource(RapuiResource):
    isLeaf = True
    isGzipped = True

    def render_GET(self, request):
        name = request.args.get('name', [None])[0]
        version = request.args.get('version', [None])[0]

        if not name and not version:
            msg = "Download requires agent name and version, Name=%s, Version=%s"
            msg %= (name, version)
            logger.error(msg)
            request.write(msg)
            request.finish()
            return NOT_DONE_YET

        logger.debug("Agent Download Resource GET, name=%s, version=%s",
                     name, version)

        session = getNovaOrmSession()
        qry = session.query(AgentUpdateInfo).filter(AgentUpdateInfo.name == name)
        if version:
            qry = qry.filter(AgentUpdateInfo.version == version)

        try:
            agentInfo = qry.one()

        except NoResultFound as e:
            logger.warning("There are no agent builds for agent %s, version %s",
                           name, version)
            request.finish()
            return NOT_DONE_YET

        from peek_server.AppConfig import appConfig
        appConfig.platformSoftwarePath

        fillFilePath = os.path.join(appConfig.platformSoftwarePath, agentInfo.fileName)

        request.responseHeaders.setRawHeaders('content-type',
                                              ['application/octet-stream'])
        return resourceCacheAndServeStaticFile(request, fillFilePath)


@addResourceCreator('/peek_server.agent.sw_update.download')
def _creator(userAccess):
    return AgentSwUpdateResource(userAccess)
