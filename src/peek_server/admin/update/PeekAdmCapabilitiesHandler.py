'''
Created on 09/07/2014

@author: synerty
'''
from peek_server.admin.navbar.PeekAdmNavbarHandler import navbarDataHandler
from rapui.vortex.DataWrapTuple import DataWrapTuple
from peek_server.storage import getPeekServerOrmSession
from rapui.vortex.Payload import Payload
from rapui.vortex.PayloadEndpoint import PayloadEndpoint

from rapui.vortex.Vortex import vortexSendPayload

capabilitiesDataFiltKey = {"key": "admin.capabilities.data"}


# HANDLER
class __CrudHandler():
    def __init__(self, payloadFilter):
        self._payloadFilter = payloadFilter
        self._ep = PayloadEndpoint(self._payloadFilter, self.process)

    def process(self, payload, vortexUuid=None, userAccess=None, **kwargs):
        from peek_server.PeekServerConfig import peekServerConfig
        from peek_server.server.auth import AuthValue
        from peek_server.storage.Setting import internalSetting, CAPABILITIES_KEY

        result = None
        session = getPeekServerOrmSession()

        # Force capabilities reload on page load
        peekServerConfig._capabilities = None

        # This is an update
        if payload.tuples:
            dataWrapTuple = payload.tuples[0]
            self._capabilities = None

            try:
                AuthValue.loadCapabilities(self, dataWrapTuple.data)
            except Exception as e:
                pass
            if self._capabilities is None:
                result = {"success": False,
                          "message": "The license entered is not valid for this server"}
                vortexSendPayload(Payload(filt=self._payloadFilter,
                                          result=result),
                                  vortexUuid=vortexUuid)
                return

            peekServerConfig._capabilities = self._capabilities

            internalSetting()[CAPABILITIES_KEY] = dataWrapTuple.data
            session.commit()
            result = {"success": True,
                      "message": "The license was successfully loaded"}
        dataWrapTuple = DataWrapTuple()
        dataWrapTuple.data = peekServerConfig.capabilities

        vortexSendPayload(Payload(filt=self._payloadFilter,
                                  tuples=[dataWrapTuple],
                                  result=result),
                          vortexUuid=vortexUuid)

        navbarDataHandler.sendModelUpdate(vortexUuid=vortexUuid, userAccess=userAccess)


__ormCrudHandler = __CrudHandler(capabilitiesDataFiltKey)
