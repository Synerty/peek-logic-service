"""
 * SynNOVA.rdbms.__init__.py
 *
 *  Copyright Synerty Pty Ltd 2013
 *
 *  This software is proprietary, you are not free to copy
 *  or redistribute this code in any format.
 *
 *  All rights to this software are reserved by
 *  Synerty Pty Ltd
 *
"""
import logging
from mutex import mutex
from time import sleep

import os
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session
from sqlalchemy.orm import sessionmaker
from sqlalchemy.sql.schema import Sequence

logger = logging.getLogger(__name__)


class SynSqlaConn(object):
    dbEngine = None
    ScopedSession = None

    dbEngineArgs = {}
    sqlaConnectUrl = None


def closeAllSessions():
    getPeekServerOrmSession()  # Ensure we have a session maker
    SynSqlaConn.ScopedSession.close_all()


def getPeekServerOrmSession():
    if SynSqlaConn.ScopedSession:
        return SynSqlaConn.ScopedSession()

    SynSqlaConn.dbEngine = create_engine(
        SynSqlaConn.sqlaConnectUrl,
        echo=False,
        **SynSqlaConn.dbEngineArgs
    )

    # Always required as we need to install geoalchemy
    doMigration(SynSqlaConn.dbEngine)

    # checkForeignKeys(engine=SqlaConn.dbEngine)

    SynSqlaConn.ScopedSession = scoped_session(
        sessionmaker(bind=SynSqlaConn.dbEngine))

    return SynSqlaConn.ScopedSession()


# def checkForeignKeys(engine):
#     from DeclarativeBase import DeclarativeBase
#     missing = sqlalchemy_utils.functions.non_indexed_foreign_keys(
#         DeclarativeBase.metadata,
#         engine=engine)
#     for table, keys in missing.items():
#         for key in keys:
#             logger.warning("Missing index on ForeignKey %s" % key.columns)


sequenceMutex = mutex()


def getPgSequenceGenerator(Declarative, count, session=None):
    if not count:
        return

    session = session if session else getPeekServerOrmSession()
    session.commit()

    while not sequenceMutex.testandset():
        sleep(0.001)

    # Something about the backend not updating curval/nextval causes issues when
    #
    sequence = Sequence('%s_id_seq' % Declarative.__tablename__)
    startId = session.execute(sequence) + 1
    endId = startId + count

    session.execute('alter sequence "%s" restart with %s'
                    % (sequence.name, endId + 1))
    session.commit()

    sequenceMutex.unlock()

    while startId < endId:
        yield startId
        startId += 1


def _runAlembicCommand(command, *args):
    from peek_server.PeekServerConfig import peekServerConfig

    curdir = os.getcwd()
    os.chdir(os.path.dirname(peekServerConfig.alembicIniPath))

    # then, load the Alembic configuration and generate the
    # version table, "stamping" it with the most recent rev:
    from alembic.config import Config
    alembic_cfg = Config(peekServerConfig.alembicIniPath)
    command(alembic_cfg, *args)

    os.chdir(curdir)


def doCreateAll(engine):
    from DeclarativeBase import DeclarativeBase
    DeclarativeBase.metadata.create_all(SynSqlaConn.dbEngine)

    from alembic import command
    _runAlembicCommand(command.stamp, "head")


def doMigration(engine):
    from alembic import command
    _runAlembicCommand(command.upgrade, "head")


import PeekAppInfo
import Setting
