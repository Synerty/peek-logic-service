import logging

from peek_server.backend.auth.AdminAuthChecker import AdminAuthChecker
from peek_server.backend.auth.AdminAuthResource import LoginSucceededResource, \
    LoginResource
from peek_server.backend.auth.AdminUserAccess import AdminUserAccess
from twisted.python.components import registerAdapter
from twisted.web.resource import IResource
from twisted.web.server import Session
from twisted.web.util import DeferredResource
from zope.interface import Interface, Attribute, implementer

logger = logging.getLogger(name="AuthRealm")

__author__ = 'synerty'


class IAuth(Interface):
    value = Attribute("An int value which counts up once per page view.")


@implementer(IAuth)
class Auth:

    def __init__(self, session):
        self.userAccess = AdminUserAccess()
        self.userAccess.loggedIn = False
        self.userAccess.readOnly = True


registerAdapter(Auth, Session, IAuth)


@implementer(IResource)
class AdminAuthRealm:
    isLeaf = False

    def __init__(self, rootResource, authChecker: AdminAuthChecker):
        self._rootResource = rootResource
        self._authChecker = authChecker

    def _authorizedResource(self, request):
        """
        Get the L{IResource} which the given request is authorized to receive.
        If the proper authorization headers are present, the resource will be
        requested from the portal.  If not, an anonymous login attempt will be
        made.
        """

        # The Angular web app does not need authentication
        # if request.uri.endswith(b".js") or request.uri.endswith(b".html"):
        #     return self._rootResource

        auth = IAuth(request.getSession())
        if auth.userAccess.loggedIn:
            request.getSession().touch()
            return self._rootResource

        # TRY form based authentication
        a = request.args
        if request.method == b"POST":
            if b"username" in a and b"password" in a:
                user = a[b'username'][0].decode()
                pass_ = a[b"password"][0].decode()

                def loginCb(_):
                    auth.userAccess = AdminUserAccess()
                    auth.userAccess.username = user
                    auth.userAccess.loggedIn = True
                    return LoginSucceededResource()

                d = self._authChecker.check(user, pass_)
                d.addCallback(loginCb)
                d.addErrback(lambda failure: LoginResource(str(failure.value)))
                return DeferredResource(d)

        # Return login form
        return LoginResource()

    def render(self, request):
        """
        Find the L{IResource} avatar suitable for the given request, if
        possible, and render it.  Otherwise, perhaps render an error page
        requiring authorization or describing an internal server failure.
        """
        return self._authorizedResource(request).render(request)

    def getChildWithDefault(self, path, request):
        """
        Inspect the Authorization HTTP header, and return a deferred which,
        when fired after successful authentication, will return an authorized
        C{Avatar}. On authentication failure, an C{UnauthorizedResource} will
        be returned, essentially halting further dispatch on the wrapped
        resource and all children
        """
        # Don't consume any segments of the request - this class should be
        # transparent!
        request.postpath.insert(0, request.prepath.pop())
        return self._authorizedResource(request)
