from peek_server.backend.auth.AdminAuthRealm import IAuth
from peek_server.backend.navbar.PeekAdmNavbarUserTuple import PeekAdmNavbarUserTuple
from twisted.internet.defer import inlineCallbacks
from vortex.Payload import Payload
from vortex.PayloadEndpoint import PayloadEndpoint
from vortex.PayloadEnvelope import PayloadEnvelope

navbarDataFiltKey = {
    'plugin': 'peek_server',
    'key': "nav.adm.user.data"
}


# HANDLER
class __NavbarHandler:
    def __init__(self):
        self._ep = PayloadEndpoint(navbarDataFiltKey, self._process)

    def shutdown(self):
        self._ep.shutdown()

    @inlineCallbacks
    def _process(self, payloadEnvelope: PayloadEnvelope,
                 httpSession, sendResponse, **kwargs):
        userAccess = IAuth(httpSession).userAccess

        if payloadEnvelope.filt.get('logout'):
            httpSession.expire()
            userAccess.loggedIn = False
            return

        navbarTuple = PeekAdmNavbarUserTuple()
        navbarTuple.username = userAccess.username

        encodedPayload = yield Payload(navbarDataFiltKey, [navbarTuple]) \
            .toEncodedPayloadDefer()

        payloadEnvelope = PayloadEnvelope(navbarDataFiltKey, encodedPayload)
        vortexMsg = yield payloadEnvelope.toVortexMsgDefer()

        sendResponse(vortexMsg)


navbarDataHandler = __NavbarHandler()
