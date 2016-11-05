import shutil
import tarfile

import os

from peek_server.PeekServerConfig import peekServerConfig
from peek_server.platform.PappServerLoader import pappServerLoader
from peek_server.storage import getNovaOrmSession
from peek_server.storage.PeekAppInfo import PeekAppInfo
from rapui.DeferUtil import deferToThreadWrap
from rapui.util.Directory import Directory

__author__ = 'synerty'


class PappUpdateManager(object):
    PAPP_VERSION_TXT = "papp_version.txt"

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
            with tarfile.open(newSoftware.name) as tar:
                tar.extract("%s/%s" % (dirName, self.PAPP_VERSION_TXT), directory.path)

        except KeyError as e:
            raise Exception("Uploaded archive does not contain a Peek App updater, %s"
                            % e.message)
        directory.scan()

        pappVersion = directory.getFile(path=dirName, name=self.PAPP_VERSION_TXT)

        if '/' in pappVersion.path:
            raise Exception("Expected %s to be one level down, it's at %s"
                            % (self.PAPP_VERSION_TXT, pappVersion.path))

        # Example
        """
        Peek App - Noop
        papp_noop
        Synerty Pty Ltd
        www.synerty.com
        #PPA_VER#
        #PPA_BUILD#
        #BUILD_DATE#
        """

        peekAppInfo = PeekAppInfo()
        peekAppInfo.fileName = "%s.tar.bz2" % dirName

        with pappVersion.open() as f:
            peekAppInfo.title = f.readline().strip()
            peekAppInfo.name = f.readline().strip()
            peekAppInfo.creator = f.readline().strip()
            peekAppInfo.website = f.readline().strip()
            peekAppInfo.version = f.readline().strip()
            peekAppInfo.buildNumber = f.readline().strip()
            peekAppInfo.buildDate = f.readline().strip()

        if peekAppInfo.name != dirName:
            raise Exception("Peek app name '%s' does not match peek root dir name '%s"
                            % (peekAppInfo.name, dirName))

        newPath = os.path.join(peekServerConfig.pappSoftwarePath, dirName)

        if os.path.exists(newPath):
            if os.path.isdir(newPath):
                shutil.rmtree(newPath)
            else:
                os.remove(newPath)

        with tarfile.open(newSoftware.name) as tar:
            tar.extractall(newPath)

        newSoftware.delete = False

        session = getNovaOrmSession()
        existing = (session.query(PeekAppInfo)
                    .filter(PeekAppInfo.name == peekAppInfo.name,
                            PeekAppInfo.version == peekAppInfo.version)
                    .all())
        if existing:
            peekAppInfo.id = existing[0].id
            session.merge(peekAppInfo)
        else:
            session.add(peekAppInfo)

        returnedVersion = "%s, %s" % (peekAppInfo.name, peekAppInfo.version)

        session.commit()

        # Tell the server platform loader that there is an update
        pappServerLoader.notifyOfPappVersionUpdate(peekAppInfo.name, peekAppInfo.version)

        session.expunge_all()
        session.close()

        return returnedVersion

    def restartAgent(self, agentUpdateInfo):
        """ Restart Agent

        Send a message to the agent to restart, it should auto update
        """
        pass
