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

from peek_platform.file_config.PeekFileConfigABC import PeekFileConfigABC
from peek_platform.file_config.PeekFileConfigFrontendDirMixin import \
    PeekFileConfigFrontendDirMixin
from peek_platform.file_config.PeekFileConfigOsMixin import PeekFileConfigOsMixin
from peek_platform.file_config.PeekFileConfigPlatformMixin import PeekFileConfigPlatformMixin
from peek_platform.file_config.PeekFileConfigSqlAlchemyMixin import \
    PeekFileConfigSqlAlchemyMixin
from peek_server.PeekServerConfigLicMixin import PeekServerConfigLicMixin

logger = logging.getLogger(__name__)


class PeekServerConfig(PeekFileConfigABC,
                       PeekFileConfigOsMixin,
                       PeekFileConfigPlatformMixin,
                       PeekFileConfigSqlAlchemyMixin,
                       PeekServerConfigLicMixin,
                       PeekFileConfigFrontendDirMixin):
    """
    This class creates a server configuration
    """

    import peek_server_fe
    _frontendProjectDir = os.path.dirname(peek_server_fe.__file__)

    ### USER SECTION ###
    @property
    def adminPass(self):
        with self._cfg as c:
            return c.user.admin["pass"]("peeking", require_string)

    @property
    def adminUser(self):
        with self._cfg as c:
            return c.user.admin.user("backend", require_string)

    ### SERVER SECTION ###
    @property
    def sitePort(self) -> int:
        """ Site Port

        The port used to serve the admin web page on
        """
        with self._cfg as c:
            return c.server.sitePort(8010, require_integer)

    ### SERVER SECTION ###
    @property
    def peekServerHttpPort(self):
        with self._cfg as c:
            return c.peekServer.httpPort(8011, require_integer)

    @property
    def peekServerVortexTcpPort(self):
        with self._cfg as c:
            return c.peekServer.tcpVortexPort(8012, require_integer)