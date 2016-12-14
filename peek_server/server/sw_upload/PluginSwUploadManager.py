import json
import os
import shutil
import tarfile

from twisted.internet.defer import inlineCallbacks, returnValue

from peek_server.PeekServerConfig import peekServerConfig
from peek_server.server.sw_install.PluginSwInstallManager import pluginSwInstallManager
from peek_server.server.sw_version.PeekSwVersionDataHandler import \
    peekSwVersionDataHandler
from peek_server.storage.PeekPluginInfo import PeekPluginInfo
from pytmpdir.Directory import Directory

__author__ = 'synerty'


class PluginSwUploadManager(object):
    PLUGIN_VERSION_JSON = "plugin_version.json"

    def __init__(self):
        pass

    @inlineCallbacks
    def processUpdate(self, namedTempFile):

        if not tarfile.is_tarfile(namedTempFile.name):
            raise Exception("Uploaded archive is not a tar file")

        pluginName, pluginVersion, fullNewTarPath = yield self.updateToTarFile(namedTempFile)

        # Cascade this update to all the other Peek environment components
        yield pluginSwInstallManager.installAndReload(pluginName, pluginVersion, fullNewTarPath)

        # Cascade this update to all the other Peek environment components
        yield peekSwVersionDataHandler.notifyOfVersion(pluginName, pluginVersion)

        returnValue("%s, %s" % (pluginName, pluginVersion))

    def updateToTarFile(self, newSoftwareTar):
        dirName = tarfile.open(newSoftwareTar.name).getnames()[0]
        directory = Directory()
        try:
            with tarfile.open(newSoftwareTar.name) as tar:
                tar.extract("%s/%s" % (dirName, self.PLUGIN_VERSION_JSON), directory.path)

        except KeyError as e:
            raise Exception("Uploaded archive does not contain a Peek App sw_upload, %s"
                            % e.message)
        directory.scan()
        pluginVersion = directory.getFile(path=dirName, name=self.PLUGIN_VERSION_JSON)
        if '/' in pluginVersion.path:
            raise Exception("Expected %s to be one level down, it's at %s"
                            % (self.PLUGIN_VERSION_JSON, pluginVersion.path))

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

        with pluginVersion.open() as f:
            versionJson = json.load(f)

        peekAppInfo.title = versionJson["title"]
        peekAppInfo.name = versionJson["name"]
        peekAppInfo.creator = versionJson["creator"]
        peekAppInfo.website = versionJson["website"]
        peekAppInfo.version = versionJson["version"]
        peekAppInfo.buildNumber = versionJson["buildNumber"]
        peekAppInfo.buildDate = versionJson["buildDate"]

        pluginName, pluginVersion = peekAppInfo.name, peekAppInfo.version

        if not dirName.startswith(peekAppInfo.name):
            raise Exception("Peek app name '%s' does not match peek root dir name '%s"
                            % (peekAppInfo.name, dirName))

        newPath = os.path.join(peekServerConfig.pluginSoftwarePath, dirName)

        # Install the TAR file
        newSoftwareTar.delete = False
        fullNewTarPath = os.path.join(peekServerConfig.pluginSoftwarePath, peekAppInfo.fileName)
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

        return pluginName, pluginVersion, fullNewTarPath
