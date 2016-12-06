'''
Created on 09/07/2014

@author: synerty
'''
from vortex.Tuple import addTupleType, Tuple, TupleField
from vortex.handler.ModelHandler import ModelHandler

pappRouteListFilt = {
    "papp": "peek_server",
    "key": "peek_server.papp.routerModules"
}


@addTupleType
class PappRoutesTuple(Tuple):
    __tupleType__ = 'peek_server.PappRoutesTuple'

    pappName = TupleField(comment="The name of the papp, EG papp_noop")
    lazyLoadModulePath = TupleField(comment="The resource path of the papp module")


class PappRouteListHandler(ModelHandler):
    def buildModel(self, payloadFilt, **kwargs):
        from peek_server.papp.PappServerLoader import pappServerLoader
        data = []
        for name, angularModle in pappServerLoader.pappAdminAngularRoutes():
            data.append(
                PappRoutesTuple(pappName=name,
                                lazyLoadModulePath='%s/%s' % (name, angularModle)))

        return data


pappRouteListHandler = PappRouteListHandler(pappRouteListFilt)
