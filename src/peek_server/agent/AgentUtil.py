from sqlalchemy.sql.functions import func

from peek_server.storage import getNovaOrmSession
# from peek_server.storage.AgentData import AgentUpdateInfo


def getLatestAgentUpdateInfos(name=None, session=None):
    closeSession = session == None

    session = session if session else getNovaOrmSession()

    maxGroupedIds = (session
                     .query(func.max(AgentUpdateInfo.id).label('maxId'))
                     .group_by(AgentUpdateInfo.name)
                     .subquery('maxGroupedIds'))

    qry = (session
              .query(AgentUpdateInfo)
              .filter(AgentUpdateInfo.id == maxGroupedIds.c.maxId)
              .order_by(AgentUpdateInfo.name, AgentUpdateInfo.id)
              )

    if name:
        qry = qry.filter(AgentUpdateInfo.name == name)

    tuples = qry.all()

    if closeSession:
        session.expunge_all()
        session.close()

    return tuples
