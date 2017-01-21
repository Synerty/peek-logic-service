"""
 *  Copyright Synerty Pty Ltd 2016
 *
 *  This software is proprietary, you are not free to copy
 *  or redistribute this code in any format.
 *
 *  All rights to this software are reserved by
 *  Synerty Pty Ltd
 *
"""
import logging

from sqlalchemy import create_engine
import pymssql

logging.basicConfig(format='%(asctime)s %(levelname)s %(name)s:%(message)s'
                    , datefmt='%d-%b-%Y %H:%M:%S'
                    , level=logging.DEBUG)

logger = logging.getLogger(__name__)

mssqlHost = 'localhost'
mssqlPort = '1433'
mssqlUser = '.\peek'
mssqlPass = 'PASSWORD'
mssqlDbName = 'peek'

sqlaEngineUrl = 'mssql+pymssql://%(user)s:%(pass)s@%(host)s/%(db)s' % {
    'host': mssqlHost,
    'user': mssqlUser,
    'pass': mssqlPass,
    'db': mssqlDbName
}

sqlaEngineArgs = {"echo": True}


def testPymssqlConnection():
    logging.debug("Testing pymssql connection to host=%s, port=%s, user=%s, pass=%s, "
                  "db=%s", mssqlUser, mssqlPort, mssqlUser, mssqlPass, mssqlDbName)

    conn = pymssql.connect(server=mssqlHost, port=mssqlPort, user=mssqlUser,
                           password=mssqlPass, database=mssqlDbName)

    logger.debug("Created connection, testing execute")
    cursor = conn.cursor()
    cursor.execute("SELECT 1")
    row = cursor.fetchone()

    logger.debug("Test SQL executed, result : %s", row)
    cursor.close()


def testSqlalchemyConnection():
    logging.debug("Testing SQLAlchemy connection to %s", sqlaEngineUrl)

    engine = create_engine(sqlaEngineUrl, **sqlaEngineArgs)

    logger.debug("Created engine, testing execute")

    result = engine.execute("SELECT 1")

    logger.debug("Test SQL executed, result : %s", list(result)[0])


if __name__ == '__main__':
    testPymssqlConnection()
    testSqlalchemyConnection()
