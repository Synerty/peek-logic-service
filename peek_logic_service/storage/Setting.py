"""
 *  Copyright Synerty Pty Ltd 2017
 *
 *  This software is proprietary, you are not free to copy
 *  or redistribute this code in any format.
 *
 *  All rights to this software are reserved by
 *  Synerty Pty Ltd
 *
"""
from typing import Optional, Any, Dict

from sqlalchemy.ext.associationproxy import association_proxy
from sqlalchemy.orm import relationship
from sqlalchemy.orm.collections import attribute_mapped_collection
from sqlalchemy.schema import Column, ForeignKey
from sqlalchemy.sql.expression import cast, null, case
from sqlalchemy.sql.schema import Index
from sqlalchemy.types import Integer, String, Boolean

from peek_logic_service.storage.DeclarativeBase import DeclarativeBase
from vortex.Tuple import Tuple, addTupleType

__author__ = "synerty"

"""Mapping a polymorphic-valued vertical table as a dictionary.

For any given properties row, the value of the 'type' column will point to the
'_value' column active for that row.

It only differs in the mapping for vertical rows.  Here,
we'll use a @hybrid_property to attune a smart '.value' attribute that wraps up
reading and writing those various '_value' columns and keeps the '.type' up to
date.

"""

from sqlalchemy.orm.interfaces import PropComparator
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy import event
from sqlalchemy import literal_column


class ProxiedDictMixin(object):
    """Adds obj[key] access to a mapped class.

    This class basically proxies dictionary access to an attribute
    called ``_proxied``.  The class which inherits this class
    should have an attribute called ``_proxied`` which points to a dictionary.

    """

    def __len__(self):
        return len(self._proxied)

    def __iter__(self):
        return iter(self._proxied)

    def __getitem__(self, key):
        return self._proxied[str(key)]

    def __contains__(self, key):
        return str(key) in self._proxied

    def __setitem__(self, key, value):
        self._proxied[str(key)] = value

    def __delitem__(self, key):
        del self._proxied[str(key)]


class PolymorphicVerticalProperty(object):
    """A key/value pair with polymorphic value storage.

    The class which is mapped should indicate typing information
    within the "info" dictionary of mapped Column objects; see
    the AnimalFact mapping below for an example.

    """

    def __init__(self, key, value=None):
        self.key = key
        self.value = value

    @hybrid_property
    def value(self):
        fieldname, discriminator = self.type_map[self.type]
        if fieldname is None:
            return None
        else:
            return getattr(self, fieldname)

    @value.setter
    def value(self, value):
        py_type = type(value)
        fieldname, discriminator = self.type_map[py_type]

        self.type = discriminator
        if fieldname is not None:
            setattr(self, fieldname, value)

    @value.deleter
    def value(self):
        self._set_value(None)

    @value.comparator
    class value(PropComparator):
        """A comparator for .value, builds a polymorphic comparison via CASE."""

        def __init__(self, cls):
            self.cls = cls

        def _case(self):
            pairs = set(self.cls.type_map.values())
            whens = [
                (
                    literal_column("'%s'" % discriminator),
                    cast(getattr(self.cls, attribute), String),
                )
                for attribute, discriminator in pairs
                if attribute is not None
            ]
            return case(whens, self.cls.type, null())

        def __eq__(self, other):
            return self._case() == cast(other, String)

        def __ne__(self, other):
            return self._case() != cast(other, String)

    def __repr__(self):
        return "<%s %r=%r>" % (self.__class__.__name__, self.key, self.value)


@addTupleType
class SettingProperty(PolymorphicVerticalProperty, Tuple, DeclarativeBase):
    """A setting property."""

    __tablename__ = "SettingProperty"
    __tupleType__ = "c.s.p.setting.property"

    id = Column(Integer, primary_key=True, autoincrement=True)
    settingId = Column(ForeignKey("Setting.id"), primary_key=True, nullable=False)
    key = Column(String(60), primary_key=True, nullable=False)
    type = Column(String(16))

    # add information about storage for different types
    # in the info dictionary of Columns
    int_value = Column(Integer, info={"type": (int, "integer")})
    char_value = Column(String, info={"type": (str, "string")})
    boolean_value = Column(Boolean, info={"type": (bool, "boolean")})

    def __init__(self, key=None, value=None):
        PolymorphicVerticalProperty.__init__(self, key=key, value=value)
        Tuple.__init__(self)

    __table_args__ = (Index("idx_SettingProperty_settingId", settingId),)


@addTupleType
class Setting(ProxiedDictMixin, Tuple, DeclarativeBase):
    """an Animal"""

    __tablename__ = "Setting"
    __tupleType__ = "c.s.p.setting"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String)

    properties = relationship(
        "SettingProperty", collection_class=attribute_mapped_collection("key")
    )

    propertyObjects = relationship("SettingProperty", viewonly=True, lazy=False)

    _proxied = association_proxy(
        "properties",
        "value",
        creator=lambda key, value: SettingProperty(key=key, value=value),
    )

    def __init__(self, name=None):
        self.name = name

    def __repr__(self):
        return "Setting(%r)" % self.name

    @classmethod
    def with_characteristic(self, key, value):
        return self.properties.any(key=key, value=value)


@event.listens_for(SettingProperty, "mapper_configured", propagate=True)
def on_new_class(mapper, cls_):
    """Look for Column objects with type info in them, and work up
    a lookup table."""

    info_dict = {}
    info_dict[type(None)] = (None, "none")
    info_dict["none"] = (None, "none")

    for k in list(mapper.c.keys()):
        col = mapper.c[k]
        if "type" in col.info:
            python_type, discriminator = col.info["type"]
            info_dict[python_type] = (k, discriminator)
            info_dict[discriminator] = (k, discriminator)
    cls_.type_map = info_dict


class PropertyKey(object):
    def __init__(self, name, defaultValue, propertyDict):
        self.name = name
        self.defaultValue = defaultValue
        propertyDict[name] = self

    def __repr__(self):
        return self.name


def _getSetting(name, propertyDict, key=None, value=None):
    from peek_logic_service.storage import dbConn

    session = dbConn.ormSessionCreator()
    all = session.query(Setting).filter(Setting.name == name).all()

    if all:
        setting = all[0]
        session.expire(setting)
    else:
        setting = Setting(name)
        session.add(setting)

    needsCommit = False
    for prop in list(propertyDict.values()):
        if not prop.name in setting:
            setting[prop.name] = prop.defaultValue
            needsCommit = True

    if needsCommit:
        session.commit()

    if not key:
        return setting

    # Make sure the propery is defined for this setting
    assert str(key) in propertyDict, "Key %s is not defined in setting %s" % (key, name)

    if value is None:
        return setting[key]

    setting[key] = value
    session.commit()

    return setting[key]


# =============================================================================
# GLOBAL PROPERTIES
# =============================================================================

globalProperties: Dict[str, PropertyKey] = {}


def globalSetting(key: Optional[str] = None, value: Optional[Any] = None):
    return _getSetting("Global", globalProperties, key=key, value=value)


EMAIL_SENDER = PropertyKey(
    "Email Sender", "Peek@company.com", propertyDict=globalProperties
)

EMAIL_SMTP_HOST = PropertyKey(
    "Email SMTP Server", "smtp.company.com", propertyDict=globalProperties
)

EMAIL_SERVER_ADMIN = PropertyKey(
    "Server Admin Email Address", "backend@company.com", propertyDict=globalProperties
)

SYSTEM_NAME = PropertyKey("Server Name", "Peek Server", propertyDict=globalProperties)

SYSTEM_DESCRIPTION = PropertyKey(
    "Server Description",
    "Peek - Extensible Model Viewer",
    propertyDict=globalProperties,
)

# =============================================================================
# INTERNAL PROPERTIES
# =============================================================================

internalProperties: Dict[str, PropertyKey] = {}


def internalSetting(key=None, value=None):
    return _getSetting("Internal", internalProperties, key=key, value=value)


CAPABILITIES_KEY = PropertyKey(
    "capabilities.key", None, propertyDict=internalProperties
)

# =============================================================================
# SERVICES PROPERTIES
# =============================================================================

serviceProperties: Dict[str, PropertyKey] = {}


def serviceSetting(key=None, value=None):
    return _getSetting("Service", serviceProperties, key=key, value=value)
