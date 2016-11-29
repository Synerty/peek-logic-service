import json
import os
import shutil
import tarfile

from twisted.internet.defer import inlineCallbacks, returnValue

from peek_server.PeekServerConfig import peekServerConfig
from peek_server.server.sw_install.PappSwInstallManager import pappSwInstallManager
from peek_server.server.sw_version.PeekSwVersionDataHandler import \
    peekSwVersionDataHandler
from peek_server.storage import getPeekServerOrmSession
from peek_server.storage.PeekAppInfo import PeekAppInfo
from txhttputil import Directory

__author__ = 'synerty'


class PappSwUploadManager(object):
    PAPP_VERSION_JSON = "papp_version.json"

    def __init__(self):
        pass

    @inlineCallbacks
    def processUpdate(self, namedTempFiles):
        if len(namedTempFiles) != 1:
            raise Exception("Expected 1 platform update archive, received %s"
                            % len(namedTempFiles))

        newSoftwareTar = namedTempFiles[0]

        if not tarfile.is_tarfile(newSoftwareTar.name):
            raise Exception("Uploaded archive is not a tar file")

        pappName, pappVersion, fullNewTarPath = yield self.updateToTarFile(newSoftwareTar)

        # Cascade this update to all the other Peek environment components
        yield pappSwInstallManager.installAndReload(pappName, pappVersion, fullNewTarPath)

        # Cascade this update to all the other Peek environment components
        yield peekSwVersionDataHandler.notifyOfVersion(pappName, pappVersion)

        returnValue("%s, %s" % (pappName, pappVersion))

    def updateToTarFile(self, newSoftwareTar):
        dirName = tarfile.open(newSoftwareTar.name).getnames()[0]
        directory = Directory()
        try:
            with tarfile.open(newSoftwareTar.name) as tar:
                tar.extract("%s/%s" % (dirName, self.PAPP_VERSION_JSON), directory.path)

        except KeyError as e:
            raise Exception("Uploaded archive does not contain a Peek App sw_upload, %s"
                            % e.message)
        directory.scan()
        pappVersion = directory.getFile(path=dirName, name=self.PAPP_VERSION_JSON)
        if '/' in pappVersion.path:
            raise Exception("Expected %s to be one level down, it's at %s"
                            % (self.PAPP_VERSION_JSON, pappVersion.path))

        # Example
        """
        {
          "title": "Peek App - Noop",
          "name": "papp_noop",
          "company": "Synerty Pty Ltd",
          "website": "www.synerty.com",
          "version": "#PAPP_VER#",
          "buildNumber": "#PAPP_BUILD#",
          "buildDate": "#BUILD_DATE#"
        }
        """

        peekAppInfo = PeekAppInfo()
        peekAppInfo.fileName = "%s.tar.bz2" % dirName
        peekAppInfo.dirName = dirName

        with pappVersion.open() as f:
            versionJson = json.load(f)

        peekAppInfo.title = versionJson["title"]
        peekAppInfo.name = versionJson["name"]
        peekAppInfo.creator = versionJson["creator"]
        peekAppInfo.website = versionJson["website"]
        peekAppInfo.version = versionJson["version"]
        peekAppInfo.buildNumber = versionJson["buildNumber"]
        peekAppInfo.buildDate = versionJson["buildDate"]

        pappName, pappVersion = peekAppInfo.name, peekAppInfo.version

        if not dirName.startswith(peekAppInfo.name):
            raise Exception("Peek app name '%s' does not match peek root dir name '%s"
                            % (peekAppInfo.name, dirName))

        newPath = os.path.join(peekServerConfig.pappSoftwarePath, dirName)

        # Install the TAR file
        newSoftwareTar.delete = False
        fullNewTarPath = os.path.join(peekServerConfig.pappSoftwarePath, peekAppInfo.fileName)
        shutil.move(newSoftwareTar.name, fullNewTarPath)

        session = getPeekServerOrmSession()
        existing = (session.query(PeekAppInfo)
                    .filter(PeekAppInfo.name == peekAppInfo.name,
                            PeekAppInfo.version == peekAppInfo.version)
                    .all())
        if existing:
            peekAppInfo.id = existing[0].id
            session.merge(peekAppInfo)
        else:
            session.add(peekAppInfo)

        session.commit()
        session.expunge_all()
        session.close()

        return pappName, pappVersion, fullNewTarPath
