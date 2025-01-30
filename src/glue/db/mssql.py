#!/usr/bin/env python3
"""microsoft sql server related functions"""

import logging
from typing import Any

import pyodbc

logger = logging.getLogger(__name__)


def connect(*args, **kwargs) -> Any:
    """
    wrapper around pyodbc.connect that ensures paramstyle="named"
    """
    # https://github.com/mkleehammer/pyodbc/wiki/The-pyodbc-Module#connect
    return pyodbc.connect(*args, **kwargs)
