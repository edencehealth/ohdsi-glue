#!/usr/bin/env python3
""" create the results schema in the CDM DB """
import logging

from ..config import GlueConfig
from ..db.multidb import MultiDB
from ..db.utils import ensure_schema
from ..webapi import WebAPIClient

logger = logging.getLogger(__name__)

# resources:
# https://github.com/OHDSI/WebAPI/wiki/CDM-Configuration#results-schema-tables
# https://github.com/OHDSI/WebAPI/blob/v2.13.0/src/main/java/org/ohdsi/webapi/service/DDLService.java#L136


def run(config: GlueConfig, api: WebAPIClient):
    """create the results schema in the CDM DB"""
    logger.info("connecting to CDM database")
    with MultiDB(*config.cdm_db_params()) as cdm_db:
        logger.info("starting")
        # ensure the results schema exists
        # creating it here will not enable our next steps, but it
        # may be helpful if the other tools aren't creating it
        ensure_schema(cdm_db, config.results_schema)

        # see if the results.cohort table exists, if so init has already happened
        canary_table = "cohort"
        if canary_table in cdm_db.list_tables(config.results_schema):
            logger.info(
                "found canary table (%s), init has already happened", canary_table
            )
            return
        ddl = api.get_results_ddl()
        logger.info("got %s-byte sql blob from webapi. Executing...", len(ddl))
        cdm_db.execute(ddl)
        logger.info("done")
