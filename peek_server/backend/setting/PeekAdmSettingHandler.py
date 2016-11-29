'''
Created on 09/07/2014

@author: synerty
'''
import txhttputil
from peek_server.storage import getPeekServerOrmSession, Setting
from peek_server.storage.Setting import globalSetting
from vortex.handler import OrmCrudHandler

scheduleDataFiltKey = {"papp": "papp",
                       "key": "backend.setting.data"}


# HANDLER
class __CrudHandler(OrmCrudHandler):
    def createDeclarative(self, session, payloadFilt):
        return [p for p in globalSetting().propertyObjects]

    def postProcess(self, action, payloadFilt, vortexUuid):
        if action in [OrmCrudHandler.UPDATE, OrmCrudHandler.CREATE]:
            settings = globalSetting()
            txhttputil.DESCRIPTION = settings[Setting.SYSTEM_DESCRIPTION]
            txhttputil.TITLE = settings[Setting.SYSTEM_NAME]


__ormCrudHandler = __CrudHandler(getPeekServerOrmSession, Setting, scheduleDataFiltKey)
