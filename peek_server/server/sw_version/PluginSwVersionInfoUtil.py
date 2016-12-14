from sqlalchemy.sql.functions import func

from peek_server.storage.PeekPluginInfo import PeekPluginInfo


def getLatestPluginVersionInfos(name=None):
    from peek_server.storage import dbConn
    session = dbConn.ormSession

    maxGroupedIds = (session
                     .query(func.max(PeekPluginInfo.id).label('maxId'))
                     .group_by(PeekPluginInfo.name)
                     .subquery('maxGroupedIds'))

    qry = (session
           .query(PeekPluginInfo)
           .filter(PeekPluginInfo.id == maxGroupedIds.c.maxId)
           .order_by(PeekPluginInfo.name, PeekPluginInfo.id)
           )

    if name:
        qry = qry.filter(PeekPluginInfo.name == name)

    tuples = qry.all()

    session.expunge_all()

    return tuples
