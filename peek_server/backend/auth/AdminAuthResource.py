"""
 * view.common.uiobj.Style.py
 *
 *  Copyright Synerty Pty Ltd 2017
 *
 *  This software is proprietary, you are not free to copy
 *  or redistribute this code in any format.
 *
 *  All rights to this software are reserved by
 *  Synerty Pty Ltd
 *
"""
from peek_server.backend.auth.AdminAuthElement import AdminAuthElement
from twisted.python.failure import Failure
from twisted.web._flatten import flattenString
from twisted.web.resource import Resource
from twisted.web.server import NOT_DONE_YET
from twisted.web.util import redirectTo


class ElementRenderedCallback():
    def __init__(self, request):
        self.request = request

    def elementRenderedCallback(self, s):
        if self.request.finished or not self.request.channel:
            return

        if isinstance(s, Failure):
            if s.printDetailedTraceback():
                self.request.write(s.printDetailedTraceback())
            s.raiseException()

        else:
            self.request.write(s)

        self.request.finish()


class LoginResource(Resource):
    isLeaf = True

    def __init__(self, failureMsg=None):
        self._failureMsg = failureMsg

    def render_GET(self, request):
        return self._renderLogin(request)

    def render_POST(self, request):
        return self._renderLogin(request, failed=True)

    def _renderLogin(self, request, failed=False):
        request.responseHeaders.setRawHeaders(b"authorization", [b"basic"])

        callback = ElementRenderedCallback(request).elementRenderedCallback

        request.write(b'<!DOCTYPE html>\n')

        d = flattenString(request, AdminAuthElement(failed=failed,
                                                    failureMsg=self._failureMsg))
        d.addBoth(callback)
        return NOT_DONE_YET


class LoginSucceededResource(Resource):
    isLeaf = True

    def render_GET(self, request):
        return self._render(request)

    def render_POST(self, request):
        return self._render(request)

    def _render(self, request):
        return redirectTo(b'/', request)
