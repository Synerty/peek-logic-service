'''
Created on 09/07/2014

@author: synerty
'''
from peek_server.client.peekadm.navbar.PeekAdmNavbarTuple import PeekAdmNavbarTuple
from rapui.handler.ModelHandler import ModelHandler
from rapui.vortex.Payload import Payload
from rapui.vortex.Vortex import vortexSendPayload

navbarDataFiltKey = {
    'papp': 'platform',
    'key': "peekadm.navbar.data"
}


# HANDLER
class __NavbarHandler(ModelHandler):
    def buildModel(self, payloadFilt, vortexUuid=None, session=None, userAccess=None,
                   **kwargs):
        from peek_server.PeekServerConfig import peekServerConfig

        navbarTuple = PeekAdmNavbarTuple()
        lic = peekServerConfig.capabilities

        navbarTuple.supportExceeded = lic['supportExceeded'] and not lic['demoExceeded']
        navbarTuple.demoExceeded = lic['demoExceeded']
        navbarTuple.countsExceeded = lic['countsExceeded']
        navbarTuple.username = "None"  # userAccess.username

        return [navbarTuple]


navbarDataHandler = __NavbarHandler(navbarDataFiltKey)
