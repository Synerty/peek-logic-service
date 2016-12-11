'''
Created on 09/07/2014

@author: synerty
'''
from peek_server.storage.Setting import globalSetting

import rapui
from peek_server.storage import getNovaOrmSession, Setting
from rapui.handler.OrmCrudHandler import OrmCrudHandler

scheduleDataFiltKey = {"papp": "platform",
                       "key": "peekadm.setting.data"}


# HANDLER
class __CrudHandler(OrmCrudHandler):
    def createDeclarative(self, session, payloadFilt):
        return [p for p in globalSetting().propertyObjects]

    def postProcess(self, action, payloadFilt, vortexUuid):
        if action in [OrmCrudHandler.UPDATE, OrmCrudHandler.CREATE]:
            settings = globalSetting()
            rapui.DESCRIPTION = settings[Setting.SYSTEM_DESCRIPTION]
            rapui.TITLE = settings[Setting.SYSTEM_NAME]


__ormCrudHandler = __CrudHandler(getNovaOrmSession, Setting, scheduleDataFiltKey)
