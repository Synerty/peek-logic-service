#!/usr/bin/env python
""" 
 * synnova.py
 *
 *  Copyright Synerty Pty Ltd 2013
 *
 *  This updater is proprietary, you are not free to copy
 *  or redistribute this code in any format.
 *
 *  All rights to this updater are reserved by
 *  Synerty Pty Ltd
 *
"""

from rapui import LoggingSetup
from rapui.util.Directory import DirSettings

LoggingSetup.setup()

import logging

from twisted.internet import reactor, defer

import rapui
from rapui import addMetaTag
from rapui.site.Site import setupSite

rapui.DESCRIPTION = "Peek"
rapui.TITLE = "Peek"

addMetaTag(name="apple-mobile-web-app-capable", content="yes")
addMetaTag(name="apple-mobile-web-app-app-title", content="Peek")
addMetaTag(name="apple-mobile-web-app-status-bar-style", content="black")
addMetaTag(name="viewport", content="initial-scale=1")
addMetaTag(name="format-detection", content="telephone=no")

logger = logging.getLogger(__name__)

# ------------------------------------------------------------------------------
# Set the parallelism of the database and reactor

from peek_server import storage
from peek_server.storage import getNovaOrmSession

reactor.suggestThreadPoolSize(10)
storage.SynSqlaConn.dbEngineArgs = {
    'pool_size': 20,  # Number of connections to keep open
    'max_overflow': 50,  # Number that the pool size can exceed when required
    'pool_timeout': 60,  # Timeout for getting conn from pool
    'pool_recycle': 600  # Reconnect?? after 10 minutes
}

defer.setDebugging(True)


def main():
    # defer.setDebugging(True)
    # sys.argv.remove(DEBUG_ARG)
    # import pydevd
    # pydevd.settrace(suspend=False)

    from peek_server.PeekServerConfig import peekServerConfig

    # Set paths for the Directory object
    DirSettings.defaultDirChmod = peekServerConfig.defaultDirChmod
    DirSettings.tmpDirPath = peekServerConfig.tmpPath

    # Set default logging level
    logging.root.setLevel(peekServerConfig.loggingLevel)

    # Force model migration
    session = getNovaOrmSession()
    session.close()


    sitePort = 8000
    setupSite(sitePort, debug=True)
    # setupSite(8000, debug=True, protectedResource=AuthSessionWrapper())

    reactor.run()


if __name__ == '__main__':
    main()
