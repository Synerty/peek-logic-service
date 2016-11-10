import shutil
import sys
import tarfile
import tempfile

import os
from os.path import expanduser
from twisted.internet import defer, reactor

import run_peek_server
from peek_server import storage
from peek_server.storage import getPeekServerOrmSession
from peek_server.storage import closeAllSessions
from rapui.util.Directory import Directory

__author__ = 'synerty'


class ServerUpdateManager(object):
    RUN_PEEK_SERVER_PY = 'run_peek_server.pyc'

    def __init__(self):
        pass

    def notifyOfPlatformVersionUpdate(self, newVersion):
        self.installAndRestart(newVersion)

    def installAndRestart(self, newVersion):

        from peek_server.PeekServerConfig import peekServerConfig

        newSoftwareTar = os.path.join(peekServerConfig.platformSoftwarePath,
                                      'peek_platform_%s' % newVersion,
                                      'peek_server_%s.tar.bz2' % newVersion)

        if not tarfile.is_tarfile(newSoftwareTar):
            raise Exception("Uploaded archive is not a tar file")

        directory = Directory()
        tarfile.open(newSoftwareTar).extractall(directory.path)
        directory.scan()

        runPeekServerPy = filter(lambda f: f.name == self.RUN_PEEK_SERVER_PY,
                                 directory.files)
        if len(runPeekServerPy) != 1:
            raise Exception("Uploaded archive does not contain a Peek Server update"
                            ", Expected 1 %s, got %s"
                            % (self.RUN_PEEK_SERVER_PY, len(runPeekServerPy)))

        runPeekServerPy = runPeekServerPy[0]

        if '/' in runPeekServerPy.path:
            raise Exception("Expected %s to be one level down, it's at %s"
                            % (self.RUN_PEEK_SERVER_PY, runPeekServerPy.path))

        newVersionDir = runPeekServerPy.path

        home = expanduser("~")
        newPath = os.path.join(home, newVersionDir)

        oldPath = os.path.dirname(os.path.dirname(run_peek_server.__file__))

        if os.path.exists(newPath):
            oldPath = tempfile.mkdtemp(dir=home, prefix=newVersionDir)
            shutil.move(newPath, oldPath)

        shutil.move(os.path.join(directory.path, newVersionDir), newPath)

        self._synlinkTo(home, newPath)

        try:
            closeAllSessions()
            storage.doMigration(storage.SynSqlaConn.dbEngine)
            getPeekServerOrmSession()

        except:
            self._synlinkTo(home, oldPath)
            raise

        reactor.callLater(1.0, self._restartPeek)

        return newVersionDir

    def _synlinkTo(self, home, newPath):
        symLink = os.path.join(home, 'peek_server')
        if os.path.exists(symLink):
            os.remove(symLink)
        os.symlink(newPath, symLink)

    def _restartPeek(self):
        """Restarts the current program.
        Note: this function does not return. Any cleanup action (like
        saving data) must be done before calling this function."""
        python = sys.executable
        argv = list(sys.argv)
        argv.insert(0, "-u")
        os.execl(python, python, *argv)


serverUpdateManager = ServerUpdateManager()
