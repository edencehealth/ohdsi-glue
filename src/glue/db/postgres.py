#!/usr/bin/env python3
"""postgres-related functions"""

import re
from typing import Optional, TypeAlias

import psycopg2
from psycopg2.extensions import connection as Psycopg2Connection

from ..config import GlueConfig

Connection: TypeAlias = Psycopg2Connection


def connect(
    server: str,
    user: str,
    password: str,
    database: str,
    config: GlueConfig,
) -> Connection:
    """adapt psycopg2.connect to the 'host:port'-style server param"""
    port: Optional[int]
    if ":" in server:
        # potential port specification
        if (match := re.match(r"^\[([A-Fa-f0-9\:]+)\]+:(\d+)$", server)) is not None:
            # IPv6 host & port; e.g. [fec2::10]:80
            host = match.group(1)
            port = int(match.group(2))
        else:
            host, port_str = server.split(":")
            port = int(port_str)
    else:
        host = server
        port = None

    return psycopg2.connect(
        host=host,
        port=port,
        user=user,
        password=password,
        dbname=database,
    )
