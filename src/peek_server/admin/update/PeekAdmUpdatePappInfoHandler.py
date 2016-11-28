'''
Created on 09/07/2014

@author: synerty
'''
# from peek_server.api.platform.AgentUtil import getLatestAgentUpdateInfos
from peek_server.server.sw_version.PappSwVersionInfoUtil import getLatestPappVersionInfos
from vortex.handler import ModelHandlerInThread

# HANDLER
pappVersionInfoHandlerKey = {
    'papp': 'platform',
    'key': "admin.papp.version.info"}


class __PappVersionInfoHandler(ModelHandlerInThread):
    def buildModel(self, payloadFilt, **kwargs):
        return getLatestPappVersionInfos()


__pappVersionInfoHandler = __PappVersionInfoHandler(pappVersionInfoHandlerKey)
