'''
 *
 *  Copyright Synerty Pty Ltd 2013
 *
 *  This software is proprietary, you are not free to copy
 *  or redistribute this code in any format.
 *
 *  All rights to this software are reserved by 
 *  Synerty Pty Ltd
 *
 * Website : http://www.synerty.com
 * Support : support@synerty.com
 *
'''
import logging
from datetime import datetime
import os
from ConfigParser import SafeConfigParser, NoOptionError, NoSectionError
import shutil

logger = logging.getLogger(__name__)


class PeekServerConfig(object):
    '''
    classdocs
    '''

    #### Alembic Defaults ###
    _alembicSection = 'alembic'
    _alembicScriptLocation = '/home/peek_server/peek_server/alembic'
    _alembicSqlalchemyUrl = 'postgresql://peek_server:PASSWORD@localhost/peek_server'

    _alembicExcludeSection = 'alembic:exclude'

    #### Peek Defaults ###
    _diskStorageSection = 'disk_storage'

    # ------------ LOGGING SECTION -------------
    _loggingSection = "logging"

    _loggingLevelKey = "default_level"
    _loggingLevelDefault = "INFO"

    # ------------ DISK SECTION -------------

    _homePath = 'home_path'
    _tmpPath = 'tmp_path'
    _pappSoftwarePath = 'papp_software_path'
    _platformSoftwarePath = 'platform_software_path'

    #### Peek User Defaults ###
    _userSection = "user"

    _userAdminPass = "admin.pass"
    _userAdminPassDefault = "peeking"

    #### Peek Http Defaults ###
    _httpSection = "http"

    _httpPort = "port"
    _httpPortDefault = "8000"

    defaultFileChmod = 0600
    defaultDirChmod = 0700

    def __init__(self):
        '''
        Constructor
        '''
        self._capabilities = None

        appHome = os.environ.get('PEEK_HOME', '~/peek.home')
        self.homePath = os.path.expanduser(appHome)
        if not os.path.isdir(self.homePath):
            assert (not os.path.exists(self.homePath))
            os.makedirs(self.homePath, self.defaultDirChmod)

        self._configFilePath = os.path.join(self.homePath, 'peek_server.cfg')

        self._hp = '%(' + self._homePath + ')s'

        if not os.path.exists(self._configFilePath):
            self._writeDefaults()

    def _cfg(self):
        parser = SafeConfigParser()
        if not parser.read(self._configFilePath):
            raise Exception(
                "Failed to parse Peek config file %s" % self._configFilePath)
        return parser

    def _save(self, parser):
        parser.write(open(self._configFilePath, 'w'))

    def _writeDefaults(self):
        parser = SafeConfigParser()

        parser.add_section(self._diskStorageSection)
        parser.set(self._diskStorageSection, self._homePath, self.homePath)

        # Setup the alembic section
        parser.add_section(self._alembicSection)
        parser.set(self._alembicSection, 'script_location',
                   self._alembicScriptLocation)
        parser.set(self._alembicSection, 'sourceless', 'true')
        parser.set(self._alembicSection, 'sqlalchemy.url',
                   self._alembicSqlalchemyUrl)

        # Setup the alembic:exclude section
        parser.add_section(self._alembicExcludeSection)
        parser.set(self._alembicExcludeSection, 'tables', 'spatial_ref_sys')

        self._save(parser)
        os.chmod(self._configFilePath, self.defaultFileChmod)

    def _chkDir(self, path):
        if not os.path.isdir(path):
            assert (not os.path.exists(path))
            os.makedirs(path, self.defaultDirChmod)
        return path

    def _getDir(self, key, defaultDir):
        parser = self._cfg()
        try:
            return self._chkDir(parser.get(self._diskStorageSection, key))
        except NoOptionError:
            parser.set(self._diskStorageSection, key, self._hp + '/' + defaultDir)
            self._save(parser)
            return self._chkDir(parser.get(self._diskStorageSection, key))

    def _getStr(self, section, key, defaultVal):
        parser = self._cfg()
        try:
            return parser.get(section, key)

        except NoSectionError:
            parser.add_section(section)
            self._save(parser)
            return self._getStr(section, key, defaultVal)

        except NoOptionError:
            parser.set(section, key, defaultVal)
            self._save(parser)
            return self._getStr(section, key, defaultVal)

    def _getInt(self, section, key, defaultVal):
        try:
            strVal = self._getStr(section, key, str(defaultVal))
            return int(strVal)
        except ValueError as e:
            logger.exception(e)
            logger.error("Config section=%s, key=%s couldn't be converted to int"
                         " returning default of %s", section, key, defaultVal)
            return defaultVal

    ### LOGGING SECTION ###

    @property
    def loggingLevel(self):
        lvl = self._getStr(self._loggingSection,
                           self._loggingLevelKey,
                           self._loggingLevelDefault)

        if lvl in logging._levelNames:
            return lvl

        logger.warn("Logging level %s is not valid, defauling to INFO", lvl)
        return logging.INFO

    ### DISK SECTION ###

    @property
    def tmpPath(self):
        return self._getDir(self._tmpPath, 'tmp')

    @property
    def platformSoftwarePath(self):
        return self._getDir(self._platformSoftwarePath, 'platform_software')

    @property
    def pappSoftwarePath(self):
        return self._getDir(self._pappSoftwarePath, 'papp_software')

    ### USER SECTION ###
    @property
    def adminPass(self):
        return self._getStr(self._userSection,
                            self._userAdminPass,
                            self._userAdminPassDefault)

    ### SERVER SECTION ###
    @property
    def sitePort(self):
        return 8000

    ### ALEMBIC SECTION ###
    @property
    def dbConnectString(self):
        return self._getStr(self._alembicSection, 'sqlalchemy.url', '')

    @property
    def alembicIniPath(self):
        return self._configFilePath

    ### CAPABILITIES SECTION ###
    @property
    def capabilities(self):

        from peek_server.server.auth import AuthValue
        from peek_server.storage.Setting import globalSetting, SYSTEM_NAME
        from peek_server.storage.Setting import internalSetting, CAPABILITIES_KEY
        if not self._capabilities:
            data = internalSetting()[CAPABILITIES_KEY]
            AuthValue.loadCapabilities(self, data)

        if not self._capabilities:
            self._capabilities = {'sid': AuthValue.authKey(),
                                  'upd': "01-Jan-2014",

                                  'lil': 20,
                                  'lin': "Unlicensed",

                                  'sun': "Not Supported",
                                  'sul': 0,
                                  'aud': False,
                                  'dii': False,

                                  }

        self._capabilities['upd'] = "01-Jan-2018" # DEBUG

        from peek_server.storage import getPeekServerOrmSession

        lic = self._capabilities
        # session = getNovaOrmSession()

        # def limitText(countKey, limitKey):
        #     limit = lic[limitKey]
        #     count = lic[countKey]
        #     return "%s out of %s" % (count, ("Unlimited" if limit == -1 else limit))

        lic['serverName'] = globalSetting()[SYSTEM_NAME]

        # lic['planCount'] = session.query(Plan).count()
        # lic['planCountText'] = limitText('planCount', 'plc')
        # lic['planCountExceeded'] = (lic['plc'] != -1
        #                             and lic['planCount'] > lic['plc'])
        #
        #
        # lic['execHistoryCountText'] = ("Unlimited" if lic['ehc'] == -1 else lic['ehc'])

        upd = datetime.strptime(lic['upd'], '%d-%b-%Y')
        lic['supportExceeded'] = upd < datetime.today()
        lic['demoExceeded'] = lic['lil'] == 20 and lic['supportExceeded']
        lic['countsExceeded'] = False
        # (lic['planCountExceeded']
        #                      or lic['scheduleCountExceeded']
        #                      or lic['placevalueCountExceeded'])

        if lic['supportExceeded']:
            lic['sun'] = "Expired"

        return self._capabilities

    @property
    def popupMenuScript(self):
        p = os.path
        name = "PopupMenuItemMaker.py"

        if p.exists(p.join(self._homePath, name)):
            return p.join(self._homePath, name)

        import run_peek_server
        peekPath = p.dirname(run_peek_server.__file__)

        return p.join(peekPath, name)


peekServerConfig = PeekServerConfig()
