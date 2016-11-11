import shutil
import sys
import tarfile
import tempfile

import os
from os.path import expanduser
from twisted.internet import defer, reactor

import run_peek_server
from peek_platform.sw_install.PeekSwInstallManagerBase import PeekSwInstallManagerBase
from peek_server import storage
from peek_server.papp.PappServerLoader import pappServerLoader
from peek_server.storage import getPeekServerOrmSession
from peek_server.storage import closeAllSessions
from rapui.util.Directory import Directory

__author__ = 'synerty'


class PeekSwInstallManager(PeekSwInstallManagerBase):

    def _stopCode(self):
        pappServerLoader.unloadAllPapps()

    def _upgradeCode(self):
        # Ensure the migration succeeds before restarting.
        closeAllSessions()
        storage.doMigration()
        getPeekServerOrmSession()

    def _startCode(self):
        pappServerLoader.loadAllPapps()


peekSwInstallManager = PeekSwInstallManager()
