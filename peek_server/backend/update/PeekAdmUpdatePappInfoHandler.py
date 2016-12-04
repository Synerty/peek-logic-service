'''
Created on 09/07/2014

@author: synerty
'''
from peek_server.server.sw_version.PappSwVersionInfoUtil import getLatestPappVersionInfos
from txhttputil.util.DeferUtil import deferToThreadWrap
from vortex.handler.ModelHandler import ModelHandler

pappVersionInfoHandlerKey = {
    'papp': 'peek_server',
    'key': "peek_server.papp.version.info"
}


class __PappVersionInfoHandler(ModelHandler):
    @deferToThreadWrap
    def buildModel(self, payloadFilt, **kwargs):
        return getLatestPappVersionInfos()


__pappVersionInfoHandler = __PappVersionInfoHandler(pappVersionInfoHandlerKey)
