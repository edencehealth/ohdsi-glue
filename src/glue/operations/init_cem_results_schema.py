#!/usr/bin/env python3
"""create the Common Evidence Model results schema in the CDM DB"""
import logging

from ..config import GlueConfig
from ..db.multidb import MultiDB
from ..db.utils import ensure_schema
from ..webapi import WebAPIClient

logger = logging.getLogger(__name__)

# resources:
# https://github.com/OHDSI/WebAPI/blob/v2.13.0/src/main/java/org/ohdsi/webapi/service/DDLService.java#L177
# https://github.com/OHDSI/WebAPI/blob/v2.13.0/src/main/resources/ddl/cemresults/nc_results.sql


def run(config: GlueConfig, api: WebAPIClient):
    """create the Common Evidence Model results schema in the CDM DB"""
    logger.info("connecting to CDM database")
    with MultiDB(*config.cdm_db_params()) as cdm_db:
        logger.info("starting")
        # ensure the schema exists
        ensure_schema(cdm_db, config.cem_schema)

        canary_table = "nc_results"
        if canary_table in cdm_db.list_tables(config.cem_schema):
            logger.info(
                "found canary table (%s), init has already happened", canary_table
            )
            return
        ddl = api.get_cem_results_ddl()
        logger.info("got %s-byte sql blob from webapi. Executing...", len(ddl))
        cdm_db.execute(ddl)
    logger.info("done")
