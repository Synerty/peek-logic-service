import logging
import os
import shutil
import sys
import tarfile

import jsoncfg
from jsoncfg.value_mappers import require_string
from pytmpdir.Directory import Directory, File
from twisted.internet.defer import inlineCallbacks, returnValue

from peek_platform.sw_install.PluginSwInstallManagerABC import PLUGIN_PACKAGE_JSON
from peek_platform.util.PtyUtil import spawnSubprocess, logSpawnException, spawnPty
from peek_server.PeekServerConfig import peekServerConfig
from peek_server.server.sw_install.PluginSwInstallManager import pluginSwInstallManager
from peek_server.server.sw_version.PeekSwVersionDataHandler import \
    peekSwVersionDataHandler
from peek_server.storage.PeekPluginInfo import PeekPluginInfo

__author__ = 'synerty'

logger = logging.getLogger(__name__)


class PluginSwUploadManager(object):
    def __init__(self):
        pass

    @inlineCallbacks
    def processUpdate(self, namedTempFile):

        if not tarfile.is_tarfile(namedTempFile.name):
            raise Exception("Uploaded archive is not a tar file")

        pluginName, pluginVersion, fullNewTarPath = yield self.updateToTarFile(
            namedTempFile)

        # Cascade this update to all the other Peek environment components
        yield pluginSwInstallManager.installAndReload(pluginName, pluginVersion,
                                                      fullNewTarPath)

        # Cascade this update to all the other Peek environment components
        yield peekSwVersionDataHandler.notifyOfVersion(pluginName, pluginVersion)

        returnValue("%s, %s" % (pluginName, pluginVersion))

    def updateToTarFile(self, newSoftwareTar):

        # We need the file to end in .tar.gz
        # PIP doesn't like it otherwise
        shutil.move(newSoftwareTar.name, newSoftwareTar.name + ".tar.gz")
        newSoftwareTar.name = newSoftwareTar.name + ".tar.gz"

        dirName = tarfile.open(newSoftwareTar.name).getnames()[0]

        directory = Directory()
        tarfile.open(newSoftwareTar.name).extractall(directory.path)
        directory.scan()

        # CHECK 1
        pkgInfoFile = directory.getFile(path=dirName, name="PKG-INFO")
        if not pkgInfoFile:
            raise Exception("Unable to find PKG-INFO")

        # CHECK 2
        pgkName = None
        pkgVersion = None
        with pkgInfoFile.open() as f:
            for line in f:
                if line.startswith("Name: "):
                    pgkName = line.split(':')[1].strip()

                if line.startswith("Version: "):
                    pkgVersion = line.split(':')[1].strip()

        if not pgkName:
            raise Exception("Unable to determine package name")

        if not pkgVersion:
            raise Exception("Unable to determine package version")

        # CHECK 3
        pluginPackageFile = self._getFileForFileName(PLUGIN_PACKAGE_JSON, directory)
        self._testPackageUpdate(newSoftwareTar.name)

        # Example
        """
        {
          "title": "Peek App - Noop",
          "name": "plugin_noop",
          "company": "Synerty Pty Ltd",
          "website": "www.synerty.com",
          "version": "#PLUGIN_VER#",
          "buildNumber": "#PLUGIN_BUILD#",
          "buildDate": "#BUILD_DATE#"
        }
        """

        peekAppInfo = PeekPluginInfo()
        peekAppInfo.fileName = "%s.tar.bz2" % dirName
        peekAppInfo.dirName = dirName

        packageJson = jsoncfg.load_config(pluginPackageFile.realPath)

        peekAppInfo.title = packageJson.plugin.title(require_string)
        peekAppInfo.name = packageJson.plugin.name(require_string)
        peekAppInfo.creator = packageJson.plugin.creator(require_string)
        peekAppInfo.website = packageJson.plugin.website(require_string)
        peekAppInfo.version = packageJson.plugin.version(require_string)
        peekAppInfo.buildNumber = packageJson.plugin.buildNumber(require_string)
        peekAppInfo.buildDate = packageJson.plugin.buildDate(require_string)

        del packageJson  # No longer used

        pluginName = peekAppInfo.name

        # CHECK 4
        if pluginName != pgkName:
            raise Exception("PyPI package name and papp_package.json name missmatch,"
                            " %s VS %s" % (pluginName, pgkName))

        # CHECK 5
        if pluginPackageFile.path != os.path.join(dirName, pgkName):
            raise Exception("Expected %s to be at %s, it's at %s"
                            % (PLUGIN_PACKAGE_JSON, dirName, pluginPackageFile.path))

        # CHECK 6
        if not dirName.startswith(pluginName):
            raise Exception("Peek app name '%s' does not match peek root dir name '%s"
                            % (pluginName, dirName))

        # CHECK 7
        if peekAppInfo.version != pkgVersion:
            raise Exception("Plugin %s trget version is %s actual version is %s"
                            % (pluginName, peekAppInfo.version, pkgVersion))

        # Install the TAR file
        newSoftwareTar.delete = False
        fullNewTarPath = os.path.join(peekServerConfig.pluginSoftwarePath,
                                      peekAppInfo.fileName)

        shutil.move(newSoftwareTar.name, fullNewTarPath)

        from peek_server.storage import dbConn
        session = dbConn.ormSession
        existing = (session.query(PeekPluginInfo)
                    .filter(PeekPluginInfo.name == peekAppInfo.name,
                            PeekPluginInfo.version == peekAppInfo.version)
                    .all())
        if existing:
            peekAppInfo.id = existing[0].id
            session.merge(peekAppInfo)
        else:
            session.add(peekAppInfo)

        session.commit()
        session.expunge_all()
        session.close()

        return pluginName, pluginPackageFile, fullNewTarPath

    def _getFileForFileName(self, fileName: str, directory: Directory) -> File:
        """ Get File For FileName

        Get the file from the directory that matches the fileName, this directory
         contains the extracted package.

        :param fileName: The filename to look for.
        :param directory: The directory object where the package is extracted to.
        :return: The File object representing the PKG-INFO

        """
        files = [f for f in directory.files if f.name == fileName]

        if len(files) != 1:
            raise Exception("Uploaded package does not contain exatly 1 %s file, found %s"
                            % (fileName, len(files)))

        return files[0]

    def _testPackageUpdate(self, fileName: str) -> None:
        """ Test Package Update

        :param fileName: The full path to the package file to test install

        Since we ARE running on the server, we will test install these packages here
         first, this is done by creating a virtualenv.

        Currently we just use pip to try and install the package off line, if it's happy
         we're happy.

        """

        # Create the test virtualenv
        virtualEnvDir = Directory()

        virtExec = os.path.join(os.path.dirname(sys.executable), "virtualenv")
        virtArgs = [virtExec,
                    # Give the virtual environment access to the global
                    '--system-site-packages',
                    virtualEnvDir.path]
        virtArgs = ' '.join(virtArgs)

        try:
            spawnSubprocess(virtArgs)
            logger.debug("Vritual env created.")

        except Exception as e:
            logSpawnException(e)
            e.message = "Failed to create virtualenv for platform test"
            raise

        pipExec = os.path.join(virtualEnvDir.path, 'bin', 'pip')

        # Install all the packages from the directory
        pipArgs = [pipExec] + pluginSwInstallManager.makePipArgs(fileName)
        pipArgs = ' '.join(pipArgs)

        try:
            spawnPty(pipArgs)

        except Exception as e:
            logSpawnException(e)

            # Update the detail of the exception and raise it
            e.message = "Test install of updated plugin package failed."
            raise

        # Continue normally if it all succeeded
        logger.debug("Peek Plugin package update successfully tested.")
