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
from txhttputil.site.FileUploadRequest import FileUploadRequest
from txhttputil.util.LoggingUtil import setupLogging

from peek_server import importPackages
from peek_server.storage import setupDbConn
from peek_server.storage.DeclarativeBase import metadata

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



def setupPlatform():
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

    # Set default logging level
    logging.root.setLevel(peekServerConfig.loggingLevel)

    # Set paths for the Directory object
    DirSettings.defaultDirChmod = peekServerConfig.DEFAULT_DIR_CHMOD
    DirSettings.tmpDirPath = peekServerConfig.tmpPath
    FileUploadRequest.tmpFilePath = peekServerConfig.tmpPath


def main():
    # defer.setDebugging(True)
    # sys.argv.remove(DEBUG_ARG)
    # import pydevd
    # pydevd.settrace(suspend=False)

    setupPlatform()

    # Configure sqlalchemy
    from peek_server.PeekServerConfig import peekServerConfig
    setupDbConn(
        metadata=metadata,
        dbEngineArgs = peekServerConfig.dbEngineArgs,
        dbConnectString=peekServerConfig.dbConnectString,
        alembicDir=os.path.join(os.path.dirname(__file__), "alembic")
    )

    # Force model migration
    from peek_server.storage import dbConn
    dbConn.migrate()

    # Import remaining components
    importPackages()

    # Load all papps
    from peek_server.papp.PappServerLoader import pappServerLoader
    pappServerLoader.loadAllPapps()

    from peek_server.backend.SiteRootResource import root as siteRoot
    setupSite("Peek Admin",
              siteRoot,
              peekServerConfig.sitePort,
              enableLogin=False)

    from peek_server.server.PeekServerPlatformRootResource import root as platformRoot
    setupSite("Peek Platform Data Exchange",
              platformRoot,
              peekServerConfig.platformHttpPort,
              enableLogin=False)

    reactor.run()


if __name__ == '__main__':
    main()
