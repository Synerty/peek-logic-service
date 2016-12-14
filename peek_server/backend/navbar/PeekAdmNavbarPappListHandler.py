'''
Created on 09/07/2014

@author: synerty
'''
from vortex.handler.ModelHandler import ModelHandler
from vortex.Tuple import addTupleType, Tuple, TupleField

modelSetListDataFilt = {
    "plugin": "peek_server",
    "key": "nav.adm.plugin.list"
}



@addTupleType
class PluginAdminMenuItemTuple(Tuple):
    __tupleType__ = 'peek_server.PluginAdminMenuItemTuple'

    name = TupleField(comment="The name of the plugin, EG plugin_noop")
    title = TupleField(comment="The title of the plugin, EG No Op")
    resourcePath = TupleField(comment="The resource path of the plugin")

class PeekModelSetListHandler(ModelHandler):
    def buildModel(self, payloadFilt, **kwargs):
        from peek_server.plugin.PluginServerLoader import pluginServerLoader
        data = []
        for name, title, path in pluginServerLoader.pluginFrontendTitleUrls:
            data.append(
                PluginAdminMenuItemTuple(name=name,
                                   title=title,
                                   resourcePath=path))

        return data


peekModelSetListHandler = PeekModelSetListHandler(modelSetListDataFilt)
