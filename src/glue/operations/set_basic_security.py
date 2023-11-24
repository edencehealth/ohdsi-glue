#!/usr/bin/env python3
""" setup / update the basic security database in the AppDB """
import logging

from ..config import GlueConfig
from ..db.multidb import MultiDB
from ..db.utils import ensure_schema, ensure_table
from ..sql import queries
from ..webapi import WebAPIClient
from ..webapi_db import ensure_admin_role, ensure_basic_security_user

logger = logging.getLogger(__name__)

# resources:
# https://github.com/OHDSI/WebAPI/wiki/Basic-Security-Configuration


def run(config: GlueConfig):
    """setup / update the basic security database in the AppDB"""
    # this has to go first, the other methods rely on being able to
    # communicate with webapi using bearer auth
    logger.info("connecting to security database")
    with MultiDB(*config.security_db_params()) as security_db:
        logger.info("ensuring the basic security schema is setup")

        # ensure the schema exists
        ensure_schema(security_db, config.security_schema)

        # ensure the users table exists
        ensure_table(
            security_db,
            config.security_schema,
            "users",
            queries["basic_security_users"],
        )

        # ensure the atlas user exists in the users table
        ensure_basic_security_user(
            config,
            security_db,
            config.atlas_username,
            config.atlas_password,
        )

    # sign-in with no-privs to init the sec_* tables entries
    _ = WebAPIClient(config)

    # now augment those entries...
    with MultiDB(*config.app_db_params()) as app_db:
        ensure_admin_role(config, app_db, config.atlas_username)

    logger.info("done")
