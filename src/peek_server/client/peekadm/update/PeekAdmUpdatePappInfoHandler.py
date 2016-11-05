'''
Created on 09/07/2014

@author: synerty
'''
# from peek_server.api.agent.AgentUtil import getLatestAgentUpdateInfos
from peek_server.papp.PappInfoUtil import getLatestPappVersionInfos
from rapui.handler.ModelHandler import ModelHandlerInThread

# HANDLER
pappVersionInfoHandlerKey = {
    'papp': 'platform',
    'key': "peekadm.papp.version.info"}


class __PappVersionInfoHandler(ModelHandlerInThread):
    def buildModel(self, payloadFilt, **kwargs):
        return getLatestPappVersionInfos()


__pappVersionInfoHandler = __PappVersionInfoHandler(pappVersionInfoHandlerKey)
