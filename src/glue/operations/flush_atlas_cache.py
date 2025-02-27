#!/usr/bin/env python3
"""clear the webapi db achilles_cache and cdm_cache"""

import logging

from ..config import GlueConfig
from ..db.multidb import MultiDB
from ..webapi import WebAPIClient

logger = logging.getLogger(__name__)

# resources:
# fixme: link to some resources on this step

# in APPDB, we run these:
# truncate ohdsi.achilles_cache;
# truncate ohdsi.cdm_cache;


def run(config: GlueConfig, api: WebAPIClient):
    """flush appdb caches"""
    logger.info("connecting to appdb database")
    with MultiDB(*config.app_db_params()) as app_db:
        logger.info("starting flush_atlas_cache")

        if config.ohdsi_schema not in app_db.list_schemas():
            logger.warning("schema '%s' not found in appdb", config.ohdsi_schema)
            return

        ohdsi_tables = app_db.list_tables(config.ohdsi_schema)
        for table in ("achilles_cache", "cdm_cache"):
            if table in ohdsi_tables:
                app_db.execute(
                    "truncate {ID_schema}.{ID_table}",
                    ID_schema=config.ohdsi_schema,
                    ID_table=table,
                )
                logger.info("flushed appdb table:%s", table)
    logger.info("flush_atlas_cache done")
