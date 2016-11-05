from copy import copy
import json

from sqlalchemy.orm.exc import NoResultFound

from peek_server.storage import getPeekServerOrmSession
# from peek_server.storage.AgentData import AgentUpdateInfo
from rapui.vortex.Payload import Payload
from rapui.vortex.PayloadEndpoint import PayloadEndpoint
from rapui.vortex.Vortex import vortexSendVortexMsg

__author__ = 'peek_server'
'''
Created on 09/07/2014

@author: synerty
'''

import logging

logger = logging.getLogger(__name__)

# -------------------------------------
# Software Update Handler for data from agents

# The filter we listen on
agentSwUpdateFilt = {'key': "c.s.p.agent.sw_update.check"}  # LISTEN / SEND


class AgentSwUpdateHandler(object):
    def __init__(self, payloadFilter):
        self._ep = PayloadEndpoint(payloadFilter, self._process)

    def _process(self, payload, vortexUuid, **kwargs):
        name = payload.filt["name"]

        session = getPeekServerOrmSession()
        version = None
        try:
            versionRow = (session
                       .query(AgentUpdateInfo)
                       .order_by(AgentUpdateInfo.id.desc())
                       .first())
            if versionRow:
                version = versionRow.version

        except NoResultFound as e:
            logger.warn("There are no updates for agent %s, ignoring request", name)

        self.notifyOfVersion(name, version, vortexUuid=vortexUuid)

    def notifyOfVersion(self, name, version, vortexUuid=None):
        filt = copy(agentSwUpdateFilt)
        filt["name"] = name
        filt["version"] = version
        vortexSendVortexMsg(Payload(filt=filt).toVortexMsg(), vortexUuid)


agentSwUpdateHandler = AgentSwUpdateHandler(agentSwUpdateFilt)
