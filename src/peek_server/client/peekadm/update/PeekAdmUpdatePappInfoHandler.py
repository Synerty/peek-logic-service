'''
Created on 09/07/2014

@author: synerty
'''
# from peek_server.api.agent.AgentUtil import getLatestAgentUpdateInfos
from rapui.handler.ModelHandler import ModelHandlerInThread

# HANDLER
agentUpdateInfoHandlerKey = {
    'papp': 'platform',
    'key': "peekadm.agent.update.info"}


class __AgentUpdateInfoHandler(ModelHandlerInThread):
    def buildModel(self, payloadFilt, **kwargs):
        return getLatestAgentUpdateInfos()


__agentUpdateInfoHandler = __AgentUpdateInfoHandler(agentUpdateInfoHandlerKey)
