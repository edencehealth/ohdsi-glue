#!/usr/bin/env python3
""" models used to contain data"""
from typing import NamedTuple, Type, TypeVar

T = TypeVar("T")


class BasicSecurityUser(NamedTuple):
    """Represents an entry in the security DB's users table"""

    username: str
    password_hash: str
    firstname: str
    middlename: str
    lastname: str


class BasicSecurityUserBulkEntry(NamedTuple):
    """Represents a row in the bulk user import csv file"""

    username: str
    password: str
    firstname: str
    middlename: str
    lastname: str

    @classmethod
    def from_BasicSecurityUser(cls: Type[T], user: BasicSecurityUser) -> T:
        """create an instance from an existing BasicSecurityUser"""
        user_dict = user._asdict()
        del user_dict["password_hash"]
        user_dict["password"] = ""  # nosec: this field is unused downstream
        return cls(**user_dict)


class CDMSource(NamedTuple):
    """Contains information about a webapi cdm source"""

    source_id: int
    source_name: str
    source_key: str
    source_connection: str
    source_dialect: str


class CDMSourceDaimon(NamedTuple):
    """Contains information about a webapi cdm source_daimon"""

    source_daimon_id: int
    source_id: int
    daimon_type: int
    table_qualifier: str
    priority: int


class SecRole(NamedTuple):
    """Contains information about a webapi security role"""

    login: str
    user_id: int
    role_name: str
    role_id: int
