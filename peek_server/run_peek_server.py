#!/usr/bin/env python
"""
 *  Copyright Synerty Pty Ltd 2020
 *
 *  This sw_upload is proprietary, you are not free to copy
 *  or redistribute this code in any format.
 *
 *  All rights to this sw_upload are reserved by
 *  Synerty Pty Ltd
 *
"""

import logging
import os

from peek_platform.util.LogUtil import setupPeekLogger, updatePeekLoggerHandlers, \
    setupLoggingToSysloyServer
from peek_plugin_base.PeekVortexUtil import peekServerName
from peek_server import importPackages
from peek_server.storage import setupDbConn
from peek_server.storage.DeclarativeBase import metadata
from pytmpdir.Directory import DirSettings
from txhttputil.site.FileUploadRequest import FileUploadRequest
from vortex.DeferUtil import vortexLogFailure
from vortex.VortexFactory import VortexFactory

setupPeekLogger(peekServerName)

from twisted.internet import reactor, defer

from txhttputil.site.SiteUtil import setupSite

from txhttputil.site.BasicResource import BasicResource

logger = logging.getLogger(__name__)


# ------------------------------------------------------------------------------
# Set the parallelism of the database and reactor

def setupPlatform():
    from peek_platform import PeekPlatformConfig
    PeekPlatformConfig.componentName = peekServerName

    # Tell the platform classes about our instance of the pluginSwInstallManager
    from peek_server.server.sw_install.PluginSwInstallManager import \
        PluginSwInstallManager
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

    # Initialise the recovery user
    # noinspection PyStatementEffect
    PeekPlatformConfig.config.adminUser
    # noinspection PyStatementEffect
    PeekPlatformConfig.config.adminPass

    # Update the version in the config file
    from peek_server import __version__
    PeekPlatformConfig.config.platformVersion = __version__

    # Set default logging level
    logging.root.setLevel(PeekPlatformConfig.config.loggingLevel)
    updatePeekLoggerHandlers(PeekPlatformConfig.componentName,
                             PeekPlatformConfig.config.loggingRotateSizeMb,
                             PeekPlatformConfig.config.loggingRotationsToKeep,
                             PeekPlatformConfig.config.logToStdout)

    if PeekPlatformConfig.config.loggingLogToSyslogHost:
        setupLoggingToSysloyServer(PeekPlatformConfig.config.loggingLogToSyslogHost,
                                   PeekPlatformConfig.config.loggingLogToSyslogPort,
                                   PeekPlatformConfig.config.loggingLogToSyslogFacility)

    # Enable deferred debugging if DEBUG is on.
    if logging.root.level == logging.DEBUG:
        defer.setDebugging(True)

    # If we need to enable memory debugging, turn that on.
    if PeekPlatformConfig.config.loggingDebugMemoryMask:
        from peek_platform.util.MemUtil import setupMemoryDebugging
        setupMemoryDebugging(PeekPlatformConfig.componentName,
                             PeekPlatformConfig.config.loggingDebugMemoryMask)

    # Set the reactor thread count
    reactor.suggestThreadPoolSize(PeekPlatformConfig.config.twistedThreadPoolSize)

    # Set paths for the Directory object
    DirSettings.defaultDirChmod = PeekPlatformConfig.config.DEFAULT_DIR_CHMOD
    DirSettings.tmpDirPath = PeekPlatformConfig.config.tmpPath
    FileUploadRequest.tmpFilePath = PeekPlatformConfig.config.tmpPath

    # Configure the celery app
    from peek_platform.ConfigCeleryApp import configureCeleryApp
    from peek_plugin_base.worker.CeleryApp import celeryApp
    configureCeleryApp(celeryApp, PeekPlatformConfig.config, forCaller=True)

class HACK_AllowJsFilesUnauthed(BasicResource):
    """ HACK Allow JS Files Un-Authenticated

    This class is a temporary class that must be cleaned up when
    PEEK-666 is resolved.

    It solves an issue caused by old browsers and angular9.

    """
    def __init__(self, fileUnderlayResource, adminAuthRealm):
        self._fileUnderlayResource = fileUnderlayResource
        self._adminAuthRealm = adminAuthRealm

    def getChildWithDefault(self, path, request):
        """ Get Child With Default

        Allow .js files to bypass the authentication

        """
        if path.lower().endswith(b'.js'):
           return self._fileUnderlayResource.getChildWithDefault(path, request)

        return self._adminAuthRealm.getChildWithDefault(path, request)

    def getChild(self, path, request):
        """ Get Child

        Allow .js files to bypass the authentication

        """
        if path.lower().endswith(b'.js'):
            return self._fileUnderlayResource.getChildWithDefault(path, request)

        return self._adminAuthRealm.getChildWithDefault(path, request)

def startListening():
    from peek_server.backend.AdminSiteResource import setupAdminSite, adminSiteRoot
    from peek_server.backend.auth.AdminAuthChecker import AdminAuthChecker
    from peek_server.backend.auth.AdminAuthRealm import AdminAuthRealm
    from peek_platform import PeekPlatformConfig

    setupAdminSite()

    adminAuthChecker = AdminAuthChecker()
    adminAuthRealm = AdminAuthRealm(adminSiteRoot, adminAuthChecker)
    hackMixedAuthRealm = HACK_AllowJsFilesUnauthed(adminSiteRoot,
                                                   adminAuthRealm)

    adminSiteCfg = PeekPlatformConfig.config.adminHttpServer
    setupSite("Peek Admin",
              hackMixedAuthRealm,
              portNum=adminSiteCfg.sitePort,
              enableLogin=False,
              redirectFromHttpPort=adminSiteCfg.redirectFromHttpPort,
              sslBundleFilePath=adminSiteCfg.sslBundleFilePath)

    from peek_server.server.PlatformSiteResource import setupPlatformSite
    from peek_server.server.PlatformSiteResource import platformSiteRoot

    setupPlatformSite()

    platformCfg = PeekPlatformConfig.config.platformHttpServer
    setupSite("Peek Platform Data Exchange",
              platformSiteRoot,
              portNum=platformCfg.sitePort,
              enableLogin=False,
              redirectFromHttpPort=platformCfg.redirectFromHttpPort,
              sslBundleFilePath=platformCfg.sslBundleFilePath)

    VortexFactory.createTcpServer(name=PeekPlatformConfig.componentName,
                                  port=PeekPlatformConfig.config.peekServerVortexTcpPort)


def main():
    setupPlatform()
    from peek_platform import PeekPlatformConfig
    import peek_server

    cfg = PeekPlatformConfig.config

    # Configure sqlalchemy
    setupDbConn(
        metadata=metadata,
        dbEngineArgs=cfg.dbEngineArgs,
        dbConnectString=cfg.dbConnectString,
        alembicDir=os.path.join(os.path.dirname(peek_server.__file__), "alembic")
    )

    # Force model migration
    from peek_server.storage import dbConn
    dbConn.migrate()

    # Import remaining components
    importPackages()

    ###########################################################################
    # BEGIN - INTERIM STORAGE SETUP
    # Force model migration

    from peek_storage._private.storage import setupDbConn as storage_setupDbConn
    from peek_storage import _private as storage_private

    from peek_storage._private.storage.DeclarativeBase import metadata as storage_metadata
    storage_setupDbConn(
        metadata=storage_metadata,
        dbEngineArgs=cfg.dbEngineArgs,
        dbConnectString=cfg.dbConnectString,
        alembicDir=os.path.join(os.path.dirname(storage_private.__file__), "alembic"))

    # Perform any storage initialisation after the migration is done.
    from peek_storage._private.storage import dbConn as storage_dbConn
    from peek_storage._private.StorageInit import StorageInit
    storageInit = StorageInit(storage_dbConn)

    # Perform the migration, including and pre and post migration inits.
    storageInit.runPreMigrate()
    storage_dbConn.migrate()
    storageInit.runPostMigrate()

    # END - INTERIM STORAGE SETUP
    ###########################################################################

    ###########################################################################
    # BEGIN - PATCH CELERY TASKS TO RUN IN PostGreSQL

    # Setup TX Celery
    if cfg.celeryPlPythonEnablePatch:
        from peek_platform.CeleryPatchToPlPython import _DeferredTaskPatch

        _DeferredTaskPatch \
            .setupPostGreSQLConnection(storage_dbConn.ormSessionCreator,
                                       cfg.dbConnectString,
                                       parallelism=cfg.celeryPlPythonWorkerCount)

    else:
        from txcelery.defer import _DeferredTask
        _DeferredTask.startCeleryThreads(
            cfg.celeryConnectionPoolSize,
            cfg.celeryConnectionRecycleTime)

    # END - PATCH CELERY TASKS TO RUN IN PostGreSQL
    ###########################################################################

    reactor.addSystemEventTrigger('before', 'shutdown',
                                  PeekPlatformConfig.pluginLoader.stopOptionalPlugins)
    reactor.addSystemEventTrigger('before', 'shutdown',
                                  PeekPlatformConfig.pluginLoader.stopCorePlugins)

    reactor.addSystemEventTrigger('before', 'shutdown',
                                  PeekPlatformConfig.pluginLoader.unloadOptionalPlugins)
    reactor.addSystemEventTrigger('before', 'shutdown',
                                  PeekPlatformConfig.pluginLoader.unloadCorePlugins)

    # Load all plugins
    d = PeekPlatformConfig.pluginLoader.loadCorePlugins()
    d.addCallback(lambda _: PeekPlatformConfig.pluginLoader.loadOptionalPlugins())
    d.addCallback(lambda _: startListening())
    d.addCallback(lambda _: PeekPlatformConfig.pluginLoader.startCorePlugins())
    d.addCallback(lambda _: PeekPlatformConfig.pluginLoader.startOptionalPlugins())

    def startedSuccessfully(_):
        logger.info('Peek Server is running, version=%s',
                    cfg.platformVersion)
        return _

    d.addErrback(vortexLogFailure, logger, consumeError=True)
    d.addCallback(startedSuccessfully)

    reactor.run()


if __name__ == '__main__':
    main()
