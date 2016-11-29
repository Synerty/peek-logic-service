from sqlalchemy.sql.functions import func

from peek_server.storage import getPeekServerOrmSession
from peek_server.storage.PeekAppInfo import PeekAppInfo


def getLatestPappVersionInfos(name=None, session=None):
    closeSession = session == None

    session = session if session else getPeekServerOrmSession()

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

    if closeSession:
        session.expunge_all()
        session.close()

    return tuples
