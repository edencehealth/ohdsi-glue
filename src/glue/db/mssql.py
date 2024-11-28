#!/usr/bin/env python3
"""microsoft sql server related functions"""

import logging
from typing import Any

import ctds

logger = logging.getLogger(__name__)


def connect(*args, **kwargs) -> Any:
    """
    wrapper around ctds.connect that ensures paramstyle="named"
    """
    kwargs["paramstyle"] = "named"
    kwargs["timeout"] = 3600
    return ctds.connect(*args, **kwargs)
