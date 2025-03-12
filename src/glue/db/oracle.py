#!/usr/bin/env python3
"""microsoft sql server related functions"""

import logging

import oracledb

logger = logging.getLogger(__name__)


def connect(
    server: str,
    user: str,
    password: str,
    database: str,
    timeout: int,
    autocommit: bool = False,
) -> oracledb.Connection:
    """
    wrapper around pyodbc.connect that ensures paramstyle="named"
    """

    # fixme: implement and expose
    # tls options
    # timeout option
    # autocommit option

    cnxn = oracledb.connect(
        user=user,
        password=password,
        host=server,
        # port=1521,
        service_name=database,
    )

    return cnxn
