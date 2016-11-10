import logging

from peek_platform.sw_update_client.PeekSwUpdateHandler import peekPlatformVersionFilt
from peek_platform.sw_update_client.PeekSwVersionTuple import PeekSwVersionTuple
from peek_server.PeekServerConfig import peekServerConfig
from peek_server.server.sw_update_server.PappInfoUtil import getLatestPappVersionInfos
from rapui.vortex.PayloadEndpoint import PayloadEndpoint
from rapui.vortex.Vortex import vortexSendTuple

logger = logging.getLogger(__name__)


# -------------------------------------
# Software Update Handler for data from agents

# The filter we listen on

class PeekServerVersionHandler(object):
    def __init__(self, payloadFilter):
        self._ep = PayloadEndpoint(payloadFilter, self._process)

        self.platformVersion = None

    def _process(self, payload, vortexUuid, **kwargs):
        data = list()

        # First, name the platform version
        data.append(PeekSwVersionTuple(name="peek_platform",
                                       version=peekServerConfig.platformVersion))

        for pappVersionInfo in getLatestPappVersionInfos():
            data.append(PeekSwVersionTuple(name=pappVersionInfo.name,
                                           version=pappVersionInfo.version))

        vortexSendTuple(filt=peekPlatformVersionFilt,
                        tuple_=data,
                        vortexUuid=vortexUuid)

    def notifyOfVersion(self, name, version, vortexUuid=None):
        data = [PeekSwVersionTuple(name=name, version=version)]

        vortexSendTuple(filt=peekPlatformVersionFilt,
                        tuple_=data,
                        vortexUuid=vortexUuid)


peekServerVersionHandler = PeekServerVersionHandler(peekPlatformVersionFilt)
