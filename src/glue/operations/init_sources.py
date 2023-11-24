#!/usr/bin/env python3
"""create the source and source_daimon entries for the CDM DB in the APP DB"""
import logging

from ..config import GlueConfig
from ..db.multidb import MultiDB
from ..webapi import WebAPIClient
from ..webapi_db import ensure_webapi_source, ensure_webapi_source_daimons

logger = logging.getLogger(__name__)

# resource(s):
# https://github.com/OHDSI/WebAPI/wiki/CDM-Configuration#example-webapi-source-and-source_daimon-inserts


def run(config: GlueConfig, api: WebAPIClient):
    """create the source and source_daimon entries for the CDM DB in the APP DB"""
    logger.info("connecting to app database")
    if api.version is None:
        raise RuntimeError("api.version is required for this operation")
    with MultiDB(*config.app_db_params()) as app_db:
        logger.info("creating webapi source/source_daimon entries in app database...")
        ensure_webapi_source(config, app_db, api.version)
        ensure_webapi_source_daimons(config, app_db)
        logger.info("refreshing webapi sources")
        api.source_refresh()
        logger.info("done")
