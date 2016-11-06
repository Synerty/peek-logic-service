import shutil
import sys
import tarfile
import tempfile

import os
from os.path import expanduser
from twisted.internet import defer, reactor

import run_peek_server
from peek_server.storage import closeAllSessions
from rapui.util.Directory import Directory

__author__ = 'synerty'


class ServerUpdateManager(object):
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

        from peek_server.PeekServerConfig import peekServerConfig


        newPath = os.path.join(peekServerConfig.platformSoftwarePath,
                               newVersionDir)

        # Do we really need to keep the old version if it's the same build?
        if os.path.exists(newPath):
            shutil.rmtree(newPath)

        shutil.move(os.path.join(directory.path, newVersionDir), newPath)

    def updatePeekServer(self, newVersionDir):

        home = expanduser("~")
        newPath = os.path.join(home, newVersionDir)

        oldPath = os.path.dirname(os.path.dirname(run_peek_server.__file__))

        if os.path.exists(newPath):
            oldPath = tempfile.mkdtemp(dir=home, prefix=newVersionDir)
            shutil.move(newPath, oldPath)

        shutil.move(os.path.join(directory.path, newVersionDir), newPath)

        self._synlinkTo(home, newPath)

        from peek_server.server import orm
        from peek_server.server.orm import getNovaOrmSession
        from peek_server.server.queue_processesors.DispQueueIndexer import dispQueueCompiler
        from peek_server.server.queue_processesors.GridKeyQueueCompiler import gridKeyQueueCompiler

        try:
            try:
                dispQueueCompiler.stop()
            except AssertionError as e:
                if "not running" not in str(e):
                    raise

            try:
                gridKeyQueueCompiler.stop()
            except AssertionError as e:
                if "not running" not in str(e):
                    raise

            closeAllSessions()
            orm.doMigration(orm.SynSqlaConn.dbEngine)
            getNovaOrmSession()

        except:
            self._synlinkTo(home, oldPath)
            dispQueueCompiler.start()
            gridKeyQueueCompiler.start()
            raise


        reactor.callLater(1.0, self.restartAttune)

        return newVersionDir

    def _synlinkTo(self, home, newPath):
        symLink = os.path.join(home, 'peek_server')
        if os.path.exists(symLink):
            os.remove(symLink)
        os.symlink(newPath, symLink)

    def restartAttune(self):
        """Restarts the current program.
        Note: this function does not return. Any cleanup action (like
        saving data) must be done before calling this function."""
        python = sys.executable
        argv = list(sys.argv)
        argv.insert(0,"-u")
        os.execl(python, python, *argv)
