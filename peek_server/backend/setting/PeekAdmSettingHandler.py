'''
Created on 09/07/2014

@author: synerty
'''
import txhttputil

from peek_server.storage import Setting, dbConn
from peek_server.storage.Setting import globalSetting
from vortex.handler.OrmCrudHandler import OrmCrudHandler

filtKey = {"papp": "peek_server",
           "key": "server.setting.data"}


# HANDLER
class __CrudHandler(OrmCrudHandler):
    def createDeclarative(self, session, payloadFilt):
        return [p for p in globalSetting().propertyObjects]

    def postProcess(self, action, payloadFilt, vortexUuid):
        if action in [OrmCrudHandler.UPDATE, OrmCrudHandler.CREATE]:
            settings = globalSetting()
            txhttputil.DESCRIPTION = settings[Setting.SYSTEM_DESCRIPTION]
            txhttputil.TITLE = settings[Setting.SYSTEM_NAME]


__ormCrudHandler = __CrudHandler(lambda: dbConn.ormSession, Setting, filtKey)
