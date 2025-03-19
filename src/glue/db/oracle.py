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

    # from the docs:
    # connection = oracledb.connect(
    #   user="hr",
    #   password=userpwd,
    #   host="localhost",
    #   port=1521,
    #   service_name="orclpdb")

    port = 1521  # fixme: temp hard-coded

    logger.debug(
        "connecting to oracle server with the following parameters; "
        "user:%s "
        "host:%s "
        "port:%s "
        "service_name:%s",
        user,
        server,
        port,
        database,
    )
    cnxn = oracledb.connect(
        user=user,
        password=password,
        host=server,
        # port=1521,
        service_name=database,
    )

    return cnxn
