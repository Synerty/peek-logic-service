'''
Created on 09/07/2014

@author: synerty
'''
from peek_server.backend.navbar.PeekAdmNavbarUserTuple import PeekAdmNavbarUserTuple
from vortex.handler.ModelHandler import ModelHandler

navbarDataFiltKey = {
    'plugin': 'peek_server',
    'key': "nav.adm.user.data"
}


# HANDLER
class __NavbarHandler(ModelHandler):
    def buildModel(self, payloadFilt, vortexUuid=None, session=None, userAccess=None,
                   **kwargs):
        from peek_server.PeekServerConfig import peekServerConfig

        navbarTuple = PeekAdmNavbarUserTuple()
        lic = peekServerConfig.capabilities

        navbarTuple.supportExceeded = lic['supportExceeded'] and not lic['demoExceeded']
        navbarTuple.demoExceeded = lic['demoExceeded']
        navbarTuple.countsExceeded = lic['countsExceeded']
        navbarTuple.username = "None"  # userAccess.username

        return [navbarTuple]


navbarDataHandler = __NavbarHandler(navbarDataFiltKey)
