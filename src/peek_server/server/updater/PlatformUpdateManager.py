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


class PlatformUpdateManager(object):
    def __init__(self):
        pass

    def processUpdate(self, namedTempFiles):
        d = defer.succeed(namedTempFiles)
        d.addCallback(self._processUpdate)
        return d

    def _processUpdate(self, namedTempFiles):
        if len(namedTempFiles) != 1:
            raise Exception("Expected 1 updater update archive, received %s"
                            % len(namedTempFiles))

        newSoftware = namedTempFiles[0]

        if not tarfile.is_tarfile(newSoftware.name):
            raise Exception("Uploaded archive is not a tar file")

        directory = Directory()
        tarfile.open(newSoftware.name).extractall(directory.path)
        directory.scan()

        peekPy = filter(lambda f: f.name == 'peek_server.pyc', directory.files)
        if len(peekPy) != 1:
            raise Exception("Uploaded archive does not contain Peek updater"
                            ", Expected 1 peek_server.py, got %s" % len(peekPy))
        peekPy = peekPy[0]

        if '/' in peekPy.path:
            raise Exception("Expected peek_server.py to be one level down, it's at %s"
                            % peekPy.path)

        home = expanduser("~")
        newPath = os.path.join(home, peekPy.path)

        oldPath = os.path.dirname(os.path.dirname(run_peek_server.__file__))

        if os.path.exists(newPath):
            oldPath = tempfile.mkdtemp(dir=home, prefix=peekPy.path)
            shutil.move(newPath, oldPath)

        shutil.move(os.path.join(directory.path, peekPy.path), newPath)

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

        newVersion = peekPy.path

        reactor.callLater(1.0, self.restartAttune)

        return newVersion

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
