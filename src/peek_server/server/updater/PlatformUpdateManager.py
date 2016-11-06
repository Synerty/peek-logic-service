import shutil
import tarfile

import os
from twisted.internet import defer, reactor

from peek_server.server.updater.ServerUpdateManager import serverUpdateManager
from rapui.util.Directory import Directory

__author__ = 'synerty'


class PlatformUpdateManager(object):
    PEEK_PLATFORM_VERSION_JSON = 'peek_platform_version.json'

    def __init__(self):
        pass

    def processUpdate(self, namedTempFiles):
        d = defer.succeed(namedTempFiles)
        d.addCallback(self._processUpdate)
        return d

    def _processUpdate(self, namedTempFiles):
        if len(namedTempFiles) != 1:
            raise Exception("Expected 1 Peek Platform update, received %s"
                            % len(namedTempFiles))

        newSoftware = namedTempFiles[0]

        if not tarfile.is_tarfile(newSoftware.name):
            raise Exception("Uploaded archive is not a tar file")

        directory = Directory()
        tarfile.open(newSoftware.name).extractall(directory.path)
        directory.scan()

        platformVersionFile = filter(lambda f: f.name == self.PEEK_PLATFORM_VERSION_JSON,
                                     directory.files)
        if len(platformVersionFile) != 1:
            raise Exception("Uploaded archive does not contain a Peek Platform update"
                            ", Expected 1 %s, got %s"
                            % (self.PEEK_PLATFORM_VERSION_JSON, len(platformVersionFile)))

        platformVersionFile = platformVersionFile[0]

        if '/' in platformVersionFile.path:
            raise Exception("Expected %s to be one level down, it's at %s"
                            % (self.PEEK_PLATFORM_VERSION_JSON, platformVersionFile.path))

        newVersionDir = platformVersionFile.path
        newVersion = newVersionDir.replace("peek_platform_", "")

        serverTarFile = newVersionDir.replace('_platform_', '_server_') + '.tar.bz2'
        agentTarFile = newVersionDir.replace('_platform_', '_agent_') + '.tar.bz2'
        workerTarFile = newVersionDir.replace('_platform_', '_worker_') + '.tar.bz2'

        if not directory.getFile(path=newVersionDir, name=serverTarFile):
            raise Exception("Peek server software is missing from the platform update."
                            " %s is missing." % serverTarFile)

        if not directory.getFile(path=newVersionDir, name=agentTarFile):
            raise Exception("Peek server agent is missing from the platform update."
                            " %s is missing." % agentTarFile)

        if not directory.getFile(path=newVersionDir, name=workerTarFile):
            raise Exception("Peek server worker is missing from the platform update."
                            " %s is missing." % workerTarFile)

        from peek_server.PeekServerConfig import peekServerConfig

        newPath = os.path.join(peekServerConfig.platformSoftwarePath,
                               newVersionDir)

        # Do we really need to keep the old version if it's the same build?
        if os.path.exists(newPath):
            shutil.rmtree(newPath)

        shutil.move(os.path.join(directory.path, newVersionDir), newPath)

        # TODO, Restart server, agents and workers

        # Tell the server papp loader that there is an update
        reactor.callLater(1.0, serverUpdateManager.notifyOfPlatformVersionUpdate,
                          newVersion)

        return newVersion
