import logging

import sys
from twisted.internet import reactor
from twisted.internet.defer import Deferred
from twisted.trial import unittest

from PappServerLoader import pappLoader

logger = logging.getLogger(__name__)

PAPP_NOOP = "papp_noop"


class PappLoaderTest(unittest.TestCase):
    def testLoadAll(self):
        pappLoader.loadAllPapps()

        logger.info(pappLoader.listPapps())

        for papp in pappLoader._loadedPapps.values():
            logger.info("configUrl = %s", papp.configUrl())

        d = Deferred()
        reactor.callLater(5.0, d.callback, True)
        return d

    def testUnregister(self):
        loadedModuleBefore = set(sys.modules)

        pappLoader.loadPapp(PAPP_NOOP)
        self.assertTrue(PAPP_NOOP in sys.modules)

        pappLoader.unloadPapp(PAPP_NOOP)

        loadedModuleNow = set(sys.modules) - loadedModuleBefore

        # Ensure that none of the modules contain the papp_name
        for modName in loadedModuleNow:
            self.assertFalse(PAPP_NOOP in modName)

    def testReRegister(self):
        pappLoader.loadPapp(PAPP_NOOP)
        pappLoader.loadPapp(PAPP_NOOP)

        for papp in pappLoader._loadedPapps.values():
            logger.info("configUrl = %s", papp.configUrl())

        d = Deferred()
        reactor.callLater(5.0, d.callback, True)
        return d
