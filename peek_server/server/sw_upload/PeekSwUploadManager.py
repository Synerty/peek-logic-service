import logging
import os
import shutil
import subprocess
import sys
import tarfile
from subprocess import PIPE

from pytmpdir.Directory import Directory
from twisted.internet import reactor
from twisted.internet.defer import inlineCallbacks
from txhttputil.util.DeferUtil import deferToThreadWrap

from peek_platform import PeekPlatformConfig
from peek_platform.sw_install.PeekSwInstallManagerABC import PEEK_PLATFORM_STAMP_FILE, \
    PlatformInstallException
from peek_server.server.sw_install.PeekSwInstallManager import peekSwInstallManager

__author__ = 'synerty'

logger = logging.getLogger(__name__)


class PlatformTestException(PlatformInstallException):
    """ Platform Test Exception

    This is thrown with stdout and stderr when the test install fails
    """


class PeekSwUploadManager(object):

    def __init__(self):
        pass

    @inlineCallbacks
    def processUpdate(self, namedTempFile):

        if not tarfile.is_tarfile(namedTempFile.name):
            raise Exception("Uploaded archive is not a tar file")

        newVersion, newPath = yield self.updateToTarFile(namedTempFile.name)

        # Tell the peek server to install and restart
        yield peekSwInstallManager.installAndRestart(newVersion)

        return newVersion

    @deferToThreadWrap
    def updateToTarFile(self, newSoftwareTar):
        """ Update To Tar File

        This method inspects the tar file and finally extracts it to the platform
        path.

        """

        directory = Directory()
        tarfile.open(newSoftwareTar).extractall(directory.path)
        directory.scan()

        self._testPackageUpdate(directory)

        platformVersionFile = [f for f in directory.files if
                               f.name == PEEK_PLATFORM_STAMP_FILE]
        if len(platformVersionFile) != 1:
            raise Exception("Uploaded archive does not contain a Peek Platform update"
                            ", Expected 1 %s, got %s"
                            % (PEEK_PLATFORM_STAMP_FILE, len(platformVersionFile)))

        platformVersionFile = platformVersionFile[0]

        if '/' in platformVersionFile.path:
            raise Exception("Expected %s to be one level down, it's at %s"
                            % (PEEK_PLATFORM_STAMP_FILE, platformVersionFile.path))

        with platformVersionFile.open() as f:
            newVersion = f.read().strip()

        newPath = peekSwInstallManager.makeReleaseFileName(newVersion)

        # Do we really need to keep the old version if it's the same build?
        if os.path.isdir(newPath):
            shutil.rmtree(newPath)

        elif os.path.isfile(newPath):
            os.remove(newPath)

        shutil.copy(newSoftwareTar, newPath)

        return newVersion, newPath

    def _testPackageUpdate(self, directory: Directory) -> None:
        """ Test Package Update

        :param directory: The directory where the packages are extracted

        Since we ARE running on the server, we will test install these packages here
         first, this is done by creating a virtualenv.

        There isn't a lot of testing for the release at this stage.
        Currently we just use pip to try and install the packages off line, if it's happy
         we're happy.

        """

        bashExec = PeekPlatformConfig.config.bashLocation

        # Create the test virtualenv
        virtualEnvDir = Directory()

        virtExec = os.path.join(os.path.dirname(sys.executable), "virtualenv")
        virtArgs = [virtExec,
                    # Give the virtual environment access to the global
                    '--system-site-packages',
                    virtualEnvDir.path]

        commandComplete = subprocess.run(' '.join(virtArgs),
                                         executable=bashExec,
                                         stdout=PIPE, stderr=PIPE, shell=True)

        if commandComplete.returncode:
            [logger.error(l) for l in commandComplete.stdout.splitlines()]
            [logger.error(l) for l in commandComplete.stderr.splitlines()]
            raise Exception("Failed to create virtualenv for platform test")

        # We could use import pip, pip.main(..), except:
        # We want to capture, the output, and:
        # we can't tell it to use the virtualenv

        pipExec = os.path.join(virtualEnvDir.path, 'bin', 'pip')

        # Install all the packages from the directory
        pipArgs = [pipExec] + peekSwInstallManager.makePipArgs(directory)

        logger.debug("Using interpreter : %s", bashExec)
        logger.debug("Executing command : %s", pipArgs)

        commandComplete = subprocess.run(' '.join(pipArgs),
                                         executable=bashExec,
                                         stdout=PIPE, stderr=PIPE, shell=True)

        if commandComplete.returncode:
            raise PlatformTestException(
                "Test install of updated packages failed.",
                stdout=commandComplete.stdout.decode(),
                stderr=commandComplete.stderr.decode())

        # Continue normally if it all succeeded
        logger.debug("Peek update successfully tested.")
