#!/usr/bin/env python3
"""creates the achilles result table(s) which facilitate searching"""

import logging
import re

from ..config import GlueConfig
from ..db.multidb import MultiDB
from ..webapi import WebAPIClient

logger = logging.getLogger(__name__)

# resources:
# https://github.com/OHDSI/WebAPI/wiki/CDM-Configuration#concept-count-tables
# https://github.com/OHDSI/WebAPI/blob/v2.13.0/src/main/resources/ddl/achilles/achilles_result_concept_count.sql


def run(config: GlueConfig, api: WebAPIClient):
    """creates the achilles result table(s) which facilitate searching"""
    if api.version is None:
        raise RuntimeError("api.version is required for this operation")
    if api.version < "2.13.0":
        logger.info("skipping for webapi version < 2.13: %s", api.version)
        return
    logger.info("connecting to CDM database")
    with MultiDB(**config.cdm_db_params()) as cdm_db:
        logger.info("starting")
        ddl = api.get_achilles_ddl()
        # remove c-style comments which may currently contain strings that look
        # like named param references
        ddl = re.sub(r"/\*.+?\*/", "", ddl, flags=re.DOTALL)
        logger.info("got %s-byte sql blob from webapi. Executing...", len(ddl))
        cdm_db.execute(ddl)
    logger.info("enable_result_init: done")
