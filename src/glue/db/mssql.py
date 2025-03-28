#!/usr/bin/env python3
"""microsoft sql server related functions"""

import logging

import pyodbc
from ..config import GlueConfig

from typing import TypeAlias

logger = logging.getLogger(__name__)


Connection: TypeAlias = pyodbc.Connection


def connect(
    server: str,
    user: str,
    password: str,
    database: str,
    config: GlueConfig,
) -> Connection:
    """
    wrapper around pyodbc.connect that ensures paramstyle="named"
    """

    # fixme: implement and expose the following options:
    #
    # Encrypt

    connstring = (
        "Driver={ODBC Driver 18 for SQL Server};"
        f"Server={server};"
        f"Database={database};"
        f"UID={user};"
        f"PWD={password};"
        f"TrustServerCertificate={config.trust_server_certificate};"
    )

    # https://github.com/mkleehammer/pyodbc/wiki/The-pyodbc-Module#connect
    cnxn = pyodbc.connect(
        connstring,
        timeout=config.db_timeout,
        autocommit=config.mssql_autocommit,
    )

    return cnxn
