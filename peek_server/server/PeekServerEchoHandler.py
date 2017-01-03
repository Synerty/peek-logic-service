import logging

from vortex.PayloadEndpoint import PayloadEndpoint
from vortex.VortexABC import SendVortexMsgResponseCallable

logger = logging.getLogger(__name__)

# -------------------------------------
# Payload echo for the platform
# Used for the platform to tell when the peek_server server restarts.

# The filter we listen on
peekServerEchoFilt = {
    'plugin' : 'peek_platform',
    'key': "peek_platform.echo"
}  # LISTEN / SEND


class PeekServerEchoHandler(object):
    def __init__(self, payloadFilter):
        self._ep = PayloadEndpoint(payloadFilter, self._process)

    def _process(self, payload,
                 sendResponse: SendVortexMsgResponseCallable,
                 **kwargs):
        sendResponse(payload.toVortexMsg())


__peekServerEchoHandler = PeekServerEchoHandler(peekServerEchoFilt)
