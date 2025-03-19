#!/usr/bin/env python3
"""microsoft sql server related functions"""

import logging

import pyodbc

logger = logging.getLogger(__name__)


def connect(
    server: str,
    user: str,
    password: str,
    database: str,
    timeout: int,
    autocommit: bool = False,
) -> pyodbc.Connection:
    """
    wrapper around pyodbc.connect that ensures paramstyle="named"
    """

    # fixme: implement and expose the following options:
    #
    # Encrypt Union["yes", "no", "strict"]
    # TrustServerCertificate bool

    connstring = (
        "Driver={ODBC Driver 18 for SQL Server};"
        f"Server={server};"
        f"Database={database};"
        f"UID={user};"
        f"PWD={password};"
        # "TrustServerCertificate=yes;"
    )

    # https://github.com/mkleehammer/pyodbc/wiki/The-pyodbc-Module#connect
    cnxn = pyodbc.connect(connstring, timeout=timeout, autocommit=autocommit)

    return cnxn
