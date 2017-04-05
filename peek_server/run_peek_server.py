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

from peek_plugin_base.PeekVortexUtil import peekServerName
from peek_server import importPackages
from peek_server.storage import setupDbConn
from peek_server.storage.DeclarativeBase import metadata
from vortex.VortexFactory import VortexFactory

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
    PeekPlatformConfig.componentName = peekServerName

    # Tell the platform classes about our instance of the pluginSwInstallManager
    from peek_server.server.sw_install.PluginSwInstallManager import PluginSwInstallManager
    PeekPlatformConfig.pluginSwInstallManager = PluginSwInstallManager()

    # Tell the platform classes about our instance of the PeekSwInstallManager
    from peek_server.server.sw_install.PeekSwInstallManager import PeekSwInstallManager
    PeekPlatformConfig.peekSwInstallManager = PeekSwInstallManager()

    # Tell the platform classes about our instance of the PeekLoaderBase
    from peek_server.plugin.ServerPluginLoader import ServerPluginLoader
    PeekPlatformConfig.pluginLoader = ServerPluginLoader()

    # The config depends on the componentName, order is important
    from peek_server.PeekServerConfig import PeekServerConfig
    PeekPlatformConfig.config = PeekServerConfig()

    # Set default logging level
    logging.root.setLevel(PeekPlatformConfig.config.loggingLevel)

    # Set paths for the Directory object
    DirSettings.defaultDirChmod = PeekPlatformConfig.config.DEFAULT_DIR_CHMOD
    DirSettings.tmpDirPath = PeekPlatformConfig.config.tmpPath
    FileUploadRequest.tmpFilePath = PeekPlatformConfig.config.tmpPath


def main():
    # defer.setDebugging(True)
    # sys.argv.remove(DEBUG_ARG)
    # import pydevd
    # pydevd.settrace(suspend=False)

    setupPlatform()
    from peek_platform import PeekPlatformConfig
    import peek_server

    # Configure sqlalchemy
    setupDbConn(
        metadata=metadata,
        dbEngineArgs = PeekPlatformConfig.config.dbEngineArgs,
        dbConnectString=PeekPlatformConfig.config.dbConnectString,
        alembicDir=os.path.join(os.path.dirname(peek_server.__file__), "alembic")
    )

    # Force model migration
    from peek_server.storage import dbConn
    dbConn.migrate()

    # Import remaining components
    importPackages()

    from peek_server.backend.SiteRootResource import setup as setupSiteRoot
    from peek_server.backend.SiteRootResource import root as siteRoot
    setupSiteRoot()

    setupSite("Peek Admin",
              siteRoot,
              PeekPlatformConfig.config.sitePort,
              enableLogin=False)

    from peek_server.server.PeekServerPlatformRootResource import setup as setupPlatRoot
    from peek_server.server.PeekServerPlatformRootResource import root as platformRoot
    setupPlatRoot()

    setupSite("Peek Platform Data Exchange",
              platformRoot,
              PeekPlatformConfig.config.peekServerHttpPort,
              enableLogin=False)

    VortexFactory.createTcpServer(name=PeekPlatformConfig.componentName,
                                  port=PeekPlatformConfig.config.peekServerVortexTcpPort)


    webSocketPort = PeekPlatformConfig.config.webSocketPort
    VortexFactory.createWebsocketServer(PeekPlatformConfig.componentName, webSocketPort)

    reactor.addSystemEventTrigger('before', 'shutdown',
                                  PeekPlatformConfig.pluginLoader.unloadAllPlugins)

    # Load all plugins
    PeekPlatformConfig.pluginLoader.loadAllPlugins()

    reactor.run()


if __name__ == '__main__':
    main()
