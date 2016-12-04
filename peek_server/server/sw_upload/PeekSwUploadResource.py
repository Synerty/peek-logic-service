""" 
 * view.common.uiobj.Style.py
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
import json
import logging

from twisted.web.server import NOT_DONE_YET

from peek_server.server.sw_upload.PappSwUploadManager import PappSwUploadManager
from peek_server.server.sw_upload.PeekSwUploadManager import PeekSwUploadManager
from txhttputil.site.BasicResource import BasicResource

logger = logging.getLogger(name=__name__)


class PeekSwUploadResource(BasicResource):
    isLeaf = True
    useLargeRequest = True

    UPDATE_TYPE_PLATFORM = 0
    UPDATE_TYPE_PAPP = 1

    def __init__(self, updateType, *args):
        BasicResource.__init__(self, *args)

        self._updateType = updateType
        self._desc = {self.UPDATE_TYPE_PLATFORM: "Peek Platform",
                      self.UPDATE_TYPE_PAPP: "Peek App",
                      }[self._updateType]

    def render_GET(self, request):
        # TODO, This is where the platform gets it's lates download from
        raise Exception("Updates must be done via the UI")

    def render_POST(self, request):
        request.responseHeaders.setRawHeaders('content-type', ['text/plain'])
        logger.info("received %s sw_upload update request" % self._desc)

        try:
            from peek_server.PeekServerConfig import peekServerConfig
            if peekServerConfig.capabilities['supportExceeded']:
                return json.dumps({'error': "License has expired, Updates not allowed"})

        except Exception as e:
            return json.dumps({'error': str(e.message)})

        updateManager = {self.UPDATE_TYPE_PLATFORM: PeekSwUploadManager,
                         self.UPDATE_TYPE_PAPP: PappSwUploadManager,
                         }[self._updateType]()

        def good(data):
            request.write(json.dumps({'message': str(data)}).encode())
            request.finish()
            logger.info("Finished updating %s sw_upload" % self._desc)

        def bad(failure):
            request.write(json.dumps({'error': str(failure.value)}).encode())
            request.finish()
            return failure

        d = updateManager.processUpdate(request.content)
        d.addCallbacks(good, bad)

        def closedError(failure):
            logger.error("Got closedError %s" % failure)

        request.notifyFinish().addErrback(closedError)

        return NOT_DONE_YET

