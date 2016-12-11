import shutil
import tarfile

import os

from peek_server.storage import getNovaOrmSession
from rapui.DeferUtil import deferToThreadWrap
from rapui.util.Directory import Directory

__author__ = 'synerty'


class PappUpdateManager(object):
    def __init__(self):
        pass

    @deferToThreadWrap
    def processUpdate(self, namedTempFiles):
        if len(namedTempFiles) != 1:
            raise Exception("Expected 1 agent update archive, received %s"
                            % len(namedTempFiles))

        newSoftware = namedTempFiles[0]

        if not tarfile.is_tarfile(newSoftware.name):
            raise Exception("Uploaded archive is not a tar file")

        dirName = tarfile.open(newSoftware.name).getnames()[0]
        directory = Directory()
        try:
            tarfile.open(newSoftware.name).extract(dirName + "/papp_version.txt",
                                                   directory.path)
        except KeyError as e:
            raise Exception("Uploaded archive does not contain Peek Agent updater, %s"
                            % e.message)
        directory.scan()

        agentVersion = directory.getFile(path=dirName, name='papp_version.txt')

        if '/' in agentVersion.path:
            raise Exception("Expected papp_version.txt to be one level down, it's at %s"
                            % agentVersion.path)

        # Example
        """
        Peek PoF Agent
        Synerty Pty Ltd
        www.synerty.com
        #PPA_VER#
        #PPA_BUILD#
        #BUILD_DATE#
        """

        agentUpdateInfo = AgentUpdateInfo()
        agentUpdateInfo.fileName = "%s.tar.bz2" % dirName

        with agentVersion.open() as f:
            agentUpdateInfo.name = f.readline().strip()
            agentUpdateInfo.creator = f.readline().strip()
            agentUpdateInfo.website = f.readline().strip()
            agentUpdateInfo.version = f.readline().strip()
            agentUpdateInfo.buildNumber = f.readline().strip()
            agentUpdateInfo.buildDate = f.readline().strip()

        newPath = os.path.join(appConfig.platformSoftwarePath, agentUpdateInfo.fileName)

        if os.path.exists(newPath):
            if os.path.isdir(newPath):
                shutil.rmtree(newPath)
            else:
                os.remove(newPath)

        shutil.move(newSoftware.name, newPath)
        newSoftware.delete = False

        session = getNovaOrmSession()
        existing = (session.query(AgentUpdateInfo)
                    .filter(AgentUpdateInfo.name == agentUpdateInfo.name,
                            AgentUpdateInfo.version == agentUpdateInfo.version)
                    .all())
        if existing:
            agentUpdateInfo.id = existing[0].id
            session.merge(agentUpdateInfo)
        else:
            session.add(agentUpdateInfo)

        returnedVersion = "%s, %s" % (agentUpdateInfo.name, agentUpdateInfo.version)

        session.commit()

        # Tell the agent we have an update
        from peek_server.api.agent.sw_update.AgentSwUpdateHandler import agentSwUpdateHandler
        agentSwUpdateHandler.notifyOfVersion(agentUpdateInfo.name,
                                             agentUpdateInfo.version)

        session.expunge_all()
        session.close()

        return returnedVersion

    def restartAgent(self, agentUpdateInfo):
        """ Restart Agent

        Send a message to the agent to restart, it should auto update
        """
        pass
