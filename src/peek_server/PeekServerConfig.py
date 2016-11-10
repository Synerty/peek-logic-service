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

import os

from jsoncfg.value_mappers import require_string, require_integer
from peek_platform.file_config.PeekFileConfigBase import PeekFileConfigBase
from peek_platform.file_config.PeekFileConfigPlatformMixin import \
    PeekFileConfigPlatformMixin
from peek_platform.file_config.PeekFileConfigSqlAlchemyMixin import \
    PeekFileConfigSqlAlchemyMixin
from peek_server.PeekServerConfigLicMixin import PeekServerConfigLicMixin

logger = logging.getLogger(__name__)


class PeekServerConfig(PeekFileConfigBase,
                       PeekFileConfigPlatformMixin,
                       PeekFileConfigSqlAlchemyMixin,
                       PeekServerConfigLicMixin):
    ### USER SECTION ###
    @property
    def adminPass(self):
        with self._cfg as c:
            return c.user.admin["pass"]("peeking", require_string)

    @property
    def adminUser(self):
        with self._cfg as c:
            return c.user.admin.user("admin", require_string)

    ### SERVER SECTION ###
    @property
    def sitePort(self):
        with self._cfg as c:
            return c.server.port(8000, require_integer)

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
