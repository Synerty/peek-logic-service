import logging

import sys
from twisted.internet import reactor
from twisted.internet.defer import Deferred
from twisted.trial import unittest

from PappServerLoader import pappServerLoader

logger = logging.getLogger(__name__)

PAPP_NOOP = "papp_noop"


class PappLoaderTest(unittest.TestCase):
    def testLoadAll(self):
        pappServerLoader.loadAllPapps()

        logger.info(pappServerLoader.listPapps())

        for papp in pappServerLoader._loadedPapps.values():
            logger.info("configUrl = %s", papp.configUrl())

        d = Deferred()
        reactor.callLater(5.0, d.callback, True)
        return d

    def testUnregister(self):
        loadedModuleBefore = set(sys.modules)

        pappServerLoader.loadPapp(PAPP_NOOP)
        self.assertTrue(PAPP_NOOP in sys.modules)

        pappServerLoader.unloadPapp(PAPP_NOOP)

        loadedModuleNow = set(sys.modules) - loadedModuleBefore

        # Ensure that none of the modules contain the papp_name
        for modName in loadedModuleNow:
            self.assertFalse(PAPP_NOOP in modName)

    def testReRegister(self):
        pappServerLoader.loadPapp(PAPP_NOOP)
        pappServerLoader.loadPapp(PAPP_NOOP)

        for papp in pappServerLoader._loadedPapps.values():
            logger.info("configUrl = %s", papp.configUrl())

        d = Deferred()
        reactor.callLater(5.0, d.callback, True)
        return d
