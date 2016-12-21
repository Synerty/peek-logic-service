'''
Created on 09/07/2014

@author: synerty
'''
from peek_platform import PeekPlatformConfig
from peek_server.backend.navbar.PeekAdmNavbarHandler import navbarDataHandler
from vortex.DataWrapTuple import DataWrapTuple
from vortex.Payload import Payload
from vortex.PayloadEndpoint import PayloadEndpoint
from vortex.Vortex import vortexSendPayload

capabilitiesDataFiltKey = {
    "plugin": "peek_server",
    "key": "admin.capabilities.data"
}


# HANDLER
class __CrudHandler():
    def __init__(self, payloadFilter):
        self._payloadFilter = payloadFilter
        self._ep = PayloadEndpoint(self._payloadFilter, self.process)

    def process(self, payload, vortexUuid=None, userAccess=None, **kwargs):
        from peek_server.server.auth import AuthValue
        from peek_server.storage.Setting import internalSetting, CAPABILITIES_KEY

        result = None
        from peek_server.storage import dbConn
        session = dbConn.ormSession

        # Force capabilities reload on page load
        PeekPlatformConfig.config._capabilities = None

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

            PeekPlatformConfig.config._capabilities = self._capabilities

            internalSetting()[CAPABILITIES_KEY] = dataWrapTuple.data
            session.commit()
            result = {"success": True,
                      "message": "The license was successfully loaded"}
        dataWrapTuple = DataWrapTuple()
        dataWrapTuple.data = PeekPlatformConfig.config.capabilities

        vortexSendPayload(Payload(filt=self._payloadFilter,
                                  tuples=[dataWrapTuple],
                                  result=result),
                          vortexUuid=vortexUuid)

        navbarDataHandler.sendModelUpdate(vortexUuid=vortexUuid, userAccess=userAccess)


__ormCrudHandler = __CrudHandler(capabilitiesDataFiltKey)
