import logging

from twisted.internet import reactor
from twisted.trial import unittest
from twisted.internet.defer import Deferred

from PappRegister import pappRegister
from PappRegister import PAPP_CLIENTS

logger = logging.getLogger(__name__)


class PappRegisterTest(unittest.TestCase):
    def testRegister(self):
        pappRegister.registerAll()
        pappRegister.registerAll()

        logger.info(pappRegister.listPapps())

        for papp in PAPP_CLIENTS.values():
            logger.info("configUrl = %s", papp.configUrl())

        d = Deferred()
        reactor.callLater(5.0, d.callback, True)
        return d
