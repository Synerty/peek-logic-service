""" 
 * orm.ExtensionData.py
 *
 *  Copyright Synerty Pty Ltd 2011
 *
 *  This software is proprietary, you are not free to copy
 *  or redistribute this code in any format.
 *
 *  All rights to this software are reserved by 
 *  Synerty Pty Ltd
 *
"""
import logging

from sqlalchemy import Column
from sqlalchemy import Integer, String
from sqlalchemy.orm import relationship
from sqlalchemy.sql.schema import ForeignKey

from peek_server.storage.DeclarativeBase import DeclarativeBase
from txhttputil import Tuple, addTupleType

logger = logging.getLogger(__name__)


@addTupleType
class PeekEnvServers(Tuple, DeclarativeBase):
    """ PeekAppInfo

    This table stores information on the version of Peek apps that are stored in Peek.

    """
    __tupleType__ = 'peek_server_be.env.server'
    __tablename__ = 'PeekEnvServers'

    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False, unique=True)
    description = Column(String, nullable=True)
    ip = Column(String, nullable=True, unique=True)

    workers = relationship("PeekEnvWorkers")
    agent = relationship("PeekEnvAgents")


@addTupleType
class PeekEnvWorkers(Tuple, DeclarativeBase):
    """ PeekAppInfo

    This table stores information on the version of Peek apps that are stored in Peek.

    """
    __tupleType__ = 'peek_server_be.env.worker'
    __tablename__ = 'PeekEnvWorkers'

    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False, unique=True)
    description = Column(String, nullable=True)
    ip = Column(String, nullable=True, unique=True)

    serverId = Column(ForeignKey('peek_server_be.PeekEnvServers.id'), primary_key=True)
    server = relationship("PeekEnvServers")


@addTupleType
class PeekEnvAgents(Tuple, DeclarativeBase):
    """ PeekAppInfo

    This table stores information on the version of Peek apps that are stored in Peek.

    """
    __tupleType__ = 'peek_server_be.env.platform'
    __tablename__ = 'PeekEnvAgents'

    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False, unique=True)
    description = Column(String, nullable=True)
    ip = Column(String, nullable=True, unique=True)

    serverId = Column(ForeignKey('peek_server_be.PeekEnvServers.id'), primary_key=True)
    server = relationship("PeekEnvServers")
