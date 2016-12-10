from sqlalchemy.sql.functions import func

from peek_server.storage.PeekAppInfo import PeekAppInfo


def getLatestPappVersionInfos(name=None):
    from peek_server.storage import dbConn
    session = dbConn.ormSession

    maxGroupedIds = (session
                     .query(func.max(PeekAppInfo.id).label('maxId'))
                     .group_by(PeekAppInfo.name)
                     .subquery('maxGroupedIds'))

    qry = (session
           .query(PeekAppInfo)
           .filter(PeekAppInfo.id == maxGroupedIds.c.maxId)
           .order_by(PeekAppInfo.name, PeekAppInfo.id)
           )

    if name:
        qry = qry.filter(PeekAppInfo.name == name)

    tuples = qry.all()

    session.expunge_all()

    return tuples
