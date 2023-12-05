#!/usr/bin/env python3
""" setup / update the basic security database in the security db """
import logging
from typing import Set

from ..config import GlueConfig
from ..db.multidb import MultiDB
from ..db.utils import ensure_schema, ensure_table
from ..webapi import WebAPIClient
from ..webapi_db import (
    bulk_ensure_basic_security_users,
    ensure_admin_role,
    ensure_basic_security_user,
)

logger = logging.getLogger(__name__)

# resources:
# https://github.com/OHDSI/WebAPI/wiki/Basic-Security-Configuration


def run(config: GlueConfig):
    """setup / update the basic security database in the security db"""
    # this has to go first, the other methods rely on being able to
    # communicate with webapi using bearer auth
    admins: Set[str] = set((config.atlas_username,))
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
            "ddl_basic_security_users.sql",
        )

        # ensure the atlas user exists in the users table
        ensure_basic_security_user(
            config,
            security_db,
            config.atlas_username,
            config.atlas_password,
        )

        # if we were given a bulk user CSV file, we create/update/delete those users
        if config.bulk_user_file:
            ops = bulk_ensure_basic_security_users(config, security_db)
            for user, status in ops.items():
                if status not in ("DELETED", "ERROR"):
                    # sign-in with no-privs to init the sec_* tables entries
                    _ = WebAPIClient(config, user.username, user.password)
                    admins.add(user.username)

    # sign-in with no-privs to init the sec_* tables entries
    _ = WebAPIClient(config)

    # now augment those entries...
    with MultiDB(*config.app_db_params()) as app_db:
        for username in admins:
            ensure_admin_role(config, app_db, username)

    logger.info("done")
