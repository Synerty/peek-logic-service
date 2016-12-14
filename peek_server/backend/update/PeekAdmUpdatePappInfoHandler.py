'''
Created on 09/07/2014

@author: synerty
'''
from peek_server.server.sw_version.PluginSwVersionInfoUtil import getLatestPluginVersionInfos
from txhttputil.util.DeferUtil import deferToThreadWrap
from vortex.handler.ModelHandler import ModelHandler

pluginVersionInfoHandlerKey = {
    'plugin': 'peek_server',
    'key': "peek_server.plugin.version.info"
}


class __PluginVersionInfoHandler(ModelHandler):
    @deferToThreadWrap
    def buildModel(self, payloadFilt, **kwargs):
        return getLatestPluginVersionInfos()


__pluginVersionInfoHandler = __PluginVersionInfoHandler(pluginVersionInfoHandlerKey)
