'''
Created on 09/07/2014

@author: synerty
'''
from twisted.internet import reactor

from peek_server.storage import getPeekServerOrmSession
from peek_server.storage.PeekEnv import PeekEnvServers, PeekEnvAgents, PeekEnvWorkers
from rapui.handler.OrmCrudHandler import OrmCrudHandler, OrmCrudHandlerExtension

# -----------------------------------------------------------------------------
# Servers
serverListDataKey = {
    'papp': 'peek_server',
    'key': "peakadm.env.server.list.data"
}


class EnvServerListHandler(OrmCrudHandler):
    pass


envServerListHandler = EnvServerListHandler(getPeekServerOrmSession,
                                            PeekEnvServers,
                                            serverListDataKey,
                                            retreiveAll=True)


@envServerListHandler.addExtension(PeekEnvServers)
class _EnvServerListHandlerExtension(OrmCrudHandlerExtension):
    def afterUpdateCommit(self, tuple_, tuples, session, payloadFilt):
        # from peek.api.client.ClientGridHandler import clientGridHandler
        # reactor.callLater(0.0, clientGridHandler.reload)
        return True


# -----------------------------------------------------------------------------
# workers
workerListDataKey = {
    'papp': 'peek_server',
    'key': "peakadm.env.worker.list.data"
}


class EnvWorkerListHandler(OrmCrudHandler):
    pass


envWorkerListHandler = EnvWorkerListHandler(getPeekServerOrmSession,
                                            PeekEnvWorkers,
                                            workerListDataKey,
                                            retreiveAll=True)


@envWorkerListHandler.addExtension(PeekEnvWorkers)
class _EnvWorkerListHandlerExtension(OrmCrudHandlerExtension):
    def afterUpdateCommit(self, tuple_, tuples, session, payloadFilt):
        # from peek.api.client.ClientGridHandler import clientGridHandler
        # reactor.callLater(0.0, clientGridHandler.reload)
        return True


# -----------------------------------------------------------------------------
# agents
agentListDataKey = {
    'papp': 'peek_server',
    'key': "peakadm.env.agent.list.data"
}


class EnvAgentListHandler(OrmCrudHandler):
    pass


envAgentListHandler = EnvAgentListHandler(getPeekServerOrmSession,
                                          PeekEnvAgents,
                                          agentListDataKey,
                                          retreiveAll=True)


@envAgentListHandler.addExtension(PeekEnvAgents)
class _EnvAgentListHandlerExtension(OrmCrudHandlerExtension):
    def afterUpdateCommit(self, tuple_, tuples, session, payloadFilt):
        return True
