import os
import shutil
import tarfile

from twisted.internet import reactor

from peek_platform import PeekPlatformConfig
from peek_server.server.sw_install.PeekSwInstallManager import peekSwInstallManager
from pytmpdir.Directory import Directory
from txhttputil.util.DeferUtil import deferToThreadWrap

__author__ = 'synerty'


class PeekSwUploadManager(object):
    PEEK_PLATFORM_VERSION_JSON = 'peek_platform_version.json'

    def __init__(self):
        pass

    @deferToThreadWrap
    def processUpdate(self, namedTempFile):

        if not tarfile.is_tarfile(namedTempFile.name):
            raise Exception("Uploaded archive is not a tar file")

        newVersion = self.updateToTarFile(namedTempFile.name)

        # Tell the peek server to install and restart

        reactor.callLater(0, peekSwInstallManager.installAndRestart, newVersion)

        return newVersion

    def updateToTarFile(self, newSoftwareTar):
        ''' Update To Tar File

        This method inspects the tar file and finally extracts it to the platform
        path.

        '''

        directory = Directory()
        tarfile.open(newSoftwareTar).extractall(directory.path)
        directory.scan()

        platformVersionFile = [f for f in directory.files if f.name == self.PEEK_PLATFORM_VERSION_JSON]
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
            raise Exception("Peek server platform is missing from the platform update."
                            " %s is missing." % agentTarFile)

        if not directory.getFile(path=newVersionDir, name=workerTarFile):
            raise Exception("Peek server worker is missing from the platform update."
                            " %s is missing." % workerTarFile)

        newPath = os.path.join(PeekPlatformConfig.config.platformSoftwarePath,
                               newVersionDir)

        # Do we really need to keep the old version if it's the same build?
        if os.path.exists(newPath):
            shutil.rmtree(newPath)

        shutil.move(os.path.join(directory.path, newVersionDir), newPath)

        return newVersion
