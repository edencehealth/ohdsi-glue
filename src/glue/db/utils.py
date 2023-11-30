#!/usr/bin/env python3
""" utils for setting up the target database and populating some tables """
from __future__ import annotations

import logging

from .multidb import MultiDB

logger = logging.getLogger(__name__)


def ensure_schema(db: MultiDB, schema_name: str):
    """if the given schema_name doesn't exist in the database, create it"""
    if schema_name in db.list_schemas():
        logger.debug("Found '%s' schema in database", schema_name)
    else:
        logger.info("Did not find '%s' schema in database; creating...", schema_name)
        db.execute("CREATE schema {ID_schema_name}", ID_schema_name=schema_name)


def ensure_table(db: MultiDB, schema: str, table: str, ddl_filename: str) -> None:
    """if the given table doesn't exist in the database, create it"""
    if table in db.list_tables(schema):
        logger.info("found table '%s.%s' in the database", schema, table)
    else:
        logger.info("table '%s.%s' not found. creating.", schema, table)
        db.execute(MultiDB.sqlfile(ddl_filename), ID_schema=schema, ID_table=table)


def clear_table(db, table: str) -> None:
    """truncates the rows in the given table"""
    # execute_sql(cnxn, "truncate table " + table_name)
    db.execute("DELETE FROM {ID_table}", ID_table=table)
