from rapui.vortex.PayloadEndpoint import PayloadEndpoint
from rapui.vortex.Vortex import vortexSendPayload

__author__ = 'peek_server'
'''
Created on 09/07/2014

@author: synerty
'''

import logging

logger = logging.getLogger(__name__)

# -------------------------------------
# Payload echo for the agent
# Used for the agent to tell when the peek_server server restarts.

# The filter we listen on
agentEchoFilt = {'key': "peek_server.agent.echo"}  # LISTEN / SEND


class AgentEchoHandler(object):
    def __init__(self, payloadFilter):
        self._ep = PayloadEndpoint(payloadFilter, self._process)

    def _process(self, payload, vortexUuid, **kwargs):
        vortexSendPayload(payload, vortexUuid)


__agentEchoHandler = AgentEchoHandler(agentEchoFilt)
