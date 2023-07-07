"""
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
"""
import logging
import os
import random
import string
import time

from jsoncfg.value_mappers import require_string, require_integer
from peek_platform.file_config.PeekFileConfigABC import PeekFileConfigABC
from peek_platform.file_config.PeekFileConfigDocBuildMixin import (
    PeekFileConfigDocBuildMixin,
)
from peek_platform.file_config.PeekFileConfigFrontendDirMixin import (
    PeekFileConfigFrontendDirMixin,
)
from peek_platform.file_config.PeekFileConfigHttpServerMixin import (
    PeekFileConfigHttpMixin,
)
from peek_platform.file_config.PeekFileConfigOsMixin import (
    PeekFileConfigOsMixin,
)
from peek_platform.file_config.PeekFileConfigDataExchangeServerMixin import (
    PeekFileConfigDataExchangeServerMixin,
)
from peek_platform.file_config.PeekFileConfigPlatformMixin import (
    PeekFileConfigPlatformMixin,
)
from peek_platform.file_config.PeekFileConfigSqlAlchemyMixin import (
    PeekFileConfigSqlAlchemyMixin,
)
from peek_platform.file_config.PeekFileConfigWorkerMixin import (
    PeekFileConfigWorkerMixin,
)

logger = logging.getLogger(__name__)


class PeekServerConfig(
    PeekFileConfigABC,
    PeekFileConfigOsMixin,
    PeekFileConfigPlatformMixin,
    PeekFileConfigSqlAlchemyMixin,
    PeekFileConfigFrontendDirMixin,
    PeekFileConfigDocBuildMixin,
    PeekFileConfigWorkerMixin,
):
    """
    This class creates a server configuration
    """

    def __init__(self):
        super().__init__()
        self.adminHttpServer = PeekFileConfigHttpMixin(self, "admin", 8010)
        self.dataExchangeHttpServer = PeekFileConfigDataExchangeServerMixin(
            self, "dataExchange", 8011
        )

    import peek_admin_app

    _frontendProjectDir = os.path.dirname(peek_admin_app.__file__)

    ### ADMIN USER SECTION ###
    @property
    def adminPass(self):
        # Define the characters that can be used in the password
        characters = string.ascii_letters + string.digits + string.punctuation

        # Generate a random password with 32 characters
        default = "".join(random.choice(characters) for _ in range(32))

        with self._cfg as c:
            return c.httpServer.admin.recovery_user.password(
                default, require_string
            )

    @property
    def adminUser(self):
        with self._cfg as c:
            return c.httpServer.admin.recovery_user.username(
                "recovery", require_string
            )
