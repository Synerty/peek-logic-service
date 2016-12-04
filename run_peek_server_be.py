#!/usr/bin/env python
""" 
 * synnova.py
 *
 *  Copyright Synerty Pty Ltd 2013
 *
 *  This sw_upload is proprietary, you are not free to copy
 *  or redistribute this code in any format.
 *
 *  All rights to this sw_upload are reserved by
 *  Synerty Pty Ltd
 *
"""
from pytmpdir.Directory import DirSettings

from peek_server import importPackages
from txhttputil.site.FileUploadRequest import FileUploadRequest
from txhttputil.util.LoggingUtil import setupLogging

setupLogging()

import logging
import os

from twisted.internet import reactor, defer

from txhttputil.site.SiteUtil import setupSite

logger = logging.getLogger(__name__)

# ------------------------------------------------------------------------------
# Set the parallelism of the database and reactor

reactor.suggestThreadPoolSize(10)
defer.setDebugging(True)


def getAlembicDir():
    p = os.path
    pappDir = p.dirname(__file__)

    if p.isdir(p.join(pappDir, "alembic")):
        # Deployed
        return p.join(pappDir, "alembic")
    else:
        # Checked out code
        return p.join(p.dirname(pappDir), "alembic")


def main():
    # defer.setDebugging(True)
    # sys.argv.remove(DEBUG_ARG)
    # import pydevd
    # pydevd.settrace(suspend=False)

    from peek_platform import PeekPlatformConfig
    PeekPlatformConfig.componentName = "peek_server"

    # Tell the platform classes about our instance of the pappSwInstallManager
    from peek_server.server.sw_install.PappSwInstallManager import pappSwInstallManager
    PeekPlatformConfig.pappSwInstallManager = pappSwInstallManager

    # Tell the platform classes about our instance of the PeekSwInstallManager
    from peek_server.server.sw_install.PeekSwInstallManager import peekSwInstallManager
    PeekPlatformConfig.peekSwInstallManager = peekSwInstallManager

    # Tell the platform classes about our instance of the PeekLoaderBase
    from peek_server.papp.PappServerLoader import pappServerLoader
    PeekPlatformConfig.pappLoader = pappServerLoader

    # The config depends on the componentName, order is important
    from peek_server.PeekServerConfig import peekServerConfig
    PeekPlatformConfig.config = peekServerConfig

    # Set paths for the Directory object
    DirSettings.defaultDirChmod = peekServerConfig.DEFAULT_DIR_CHMOD
    DirSettings.tmpDirPath = peekServerConfig.tmpPath
    FileUploadRequest.tmpFilePath = peekServerConfig.tmpPath

    # Set default logging level
    logging.root.setLevel(peekServerConfig.loggingLevel)

    # Configure sql alchemy
    from peek_server import storage
    storage.SynSqlaConn.dbEngineArgs = peekServerConfig.sqlaEngineArgs
    storage.SynSqlaConn.dbConnectString = peekServerConfig.dbConnectString
    storage.SynSqlaConn.alembicDir = getAlembicDir()

    # Force model migration
    from peek_server.storage import getPeekServerOrmSession
    session = getPeekServerOrmSession()
    session.close()

    # Import remaining components
    importPackages()

    # Load all papps
    from peek_server.papp.PappServerLoader import pappServerLoader
    pappServerLoader.loadAllPapps()

    from peek_server.backend.PeekServerBackendRootResource import root as siteRoot
    setupSite("Peek Admin",
              siteRoot,
              peekServerConfig.sitePort,
              enableLogin=False)

    from peek_server.server.PeekServerPlatformRootResource import  root as platformRoot
    setupSite("Peek Platform Data Exchange",
              platformRoot,
              peekServerConfig.platformHttpPort,
              enableLogin=False)

    reactor.run()


if __name__ == '__main__':
    main()
