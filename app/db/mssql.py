#!/usr/bin/env python3
""" microsoft sql server related functions """
from typing import Any
import logging

import ctds

logger = logging.getLogger("ohdsi_glue.db.mssql")


def connect(*args, **kwargs) -> Any:
    """
    wrapper around ctds.connect that ensures paramstyle="named"
    """
    kwargs["paramstyle"] = "named"
    return ctds.connect(*args, **kwargs)
