'''
Created on 09/07/2014

@author: synerty
'''
from vortex.handler.ModelHandler import ModelHandler
from vortex.Tuple import addTupleType, Tuple, TupleField

modelSetListDataFilt = {
    "papp": "peek_server",
    "key": "nav.adm.papp.list"
}



@addTupleType
class PappAdminMenuItemTuple(Tuple):
    __tupleType__ = 'peek_server.PappAdminMenuItemTuple'

    name = TupleField(comment="The name of the papp, EG papp_noop")
    title = TupleField(comment="The title of the papp, EG No Op")
    resourcePath = TupleField(comment="The resource path of the papp")

class PeekModelSetListHandler(ModelHandler):
    def buildModel(self, payloadFilt, **kwargs):
        from peek_server.papp.PappServerLoader import pappServerLoader
        data = []
        for name, title, path in pappServerLoader.pappFrontendTitleUrls:
            data.append(
                PappAdminMenuItemTuple(name=name,
                                   title=title,
                                   resourcePath=path))

        return data


peekModelSetListHandler = PeekModelSetListHandler(modelSetListDataFilt)
