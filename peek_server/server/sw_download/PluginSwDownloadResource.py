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
from txhttputil.site.BasicResource import BasicResource
from txhttputil.site.StaticFileResource import StaticFileResource

from peek_platform import PeekPlatformConfig
from peek_server.storage.PeekPluginInfo import PeekPluginInfo

logger = logging.getLogger(__name__)


class PluginSwDownloadResource(BasicResource):
    isLeaf = True
    isGzipped = True

    def render_GET(self, request):
        name = request.args.get('name', [None])[0]
        version = request.args.get('version', [None])[0]

        if not name and not version:
            msg = "Download requires peek app name, Name=%s" % name
            logger.error(msg)
            request.write(msg.encode())
            request.finish()
            return NOT_DONE_YET

        logger.debug("Plugin Download Resource GET, name=%s, version=%s",
                      name, version)

        from peek_server.storage import dbConn
        session = dbConn.ormSession
        qry = session.query(PeekPluginInfo).filter(PeekPluginInfo.name == name)

        try:
            if version:
                pluginInfo = qry.filter(PeekPluginInfo.version == version).one()
            else:
                # Choose the latest
                pluginInfo = qry.order_by(desc(PeekPluginInfo.id)).first()


        except NoResultFound as e:
            logger.warning("There are no builds for plugin %s, version %s",
                           name, version)
            request.finish()
            return NOT_DONE_YET


        newSoftwareTar = os.path.join(PeekPlatformConfig.config.pluginSoftwarePath, pluginInfo.fileName)

        request.responseHeaders.setRawHeaders('content-type',
                                              ['application/octet-stream'])

        resource = StaticFileResource(newSoftwareTar)
        return resource.render_GET(request)
