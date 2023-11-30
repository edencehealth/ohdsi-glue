#!/usr/bin/env python3
""" classes and functions for manipulating the WebAPI appdb directly """
# pylint: disable=R0913
import csv
import logging
import re
from typing import Dict, List, Literal

from . import semver
from .config import GlueConfig
from .db.multidb import MultiDB
from .models import (
    BasicSecurityUser,
    BasicSecurityUserBulkEntry,
    CDMSource,
    CDMSourceDaimon,
    SecRole,
)
from .util.security import bcrypt_check, bcrypt_hash

logger = logging.getLogger(__name__)

ADMIN_ROLE_ID = 2  # webapi sec_user_role role_id

BULK_USER_STATUS = Literal[
    "OK",
    "CREATED",
    "UPDATED",
    "DELETED",
    "ERROR",
]


def get_sec_roles(config: GlueConfig, app_db: MultiDB) -> List[SecRole]:
    """return a list of user records from the webapi sec_* databases"""
    return [
        SecRole(*row)
        for row in app_db.get_rows(
            MultiDB.sqlfile("get_sec_roles.sql"),
            ID_schema=config.ohdsi_schema,
        )
    ]


def update_basic_security_user(
    config: GlueConfig, sec_db: MultiDB, username: str, password: str
):
    """update the password for an existing basic security user"""
    logger.info("updating the password for the user %s", username)
    sec_db.execute(
        MultiDB.sqlfile("update_password.sql"),
        ID_schema=config.security_schema,
        username=username,
        password_hash=bcrypt_hash(password),
    )
    logger.debug("done")


def bulk_ensure_basic_security_users(
    config: GlueConfig,
    sec_db: MultiDB,
) -> Dict[str, BULK_USER_STATUS]:
    """ensure that the users in the given csv file exist with the given passwords"""
    csv_users: Dict[str, BasicSecurityUserBulkEntry] = {}
    db_users: Dict[str, BasicSecurityUser] = {}
    result: Dict[str, BULK_USER_STATUS] = {}

    if config.bulk_user_file is None:
        raise RuntimeError("bulk_user_file cannot be none")

    # load users from the bulk file
    with open(
        config.bulk_user_file, "rt", newline="", encoding="utf-8", errors="strict"
    ) as csvfh:
        csvfile = csv.DictReader(
            csvfh,
            BasicSecurityUserBulkEntry._fields,
            dialect=csv.unix_dialect,
        )
        for row in csvfile:
            csv_record = BasicSecurityUserBulkEntry(**row)
            csv_users[csv_record.username] = csv_record

    # load users from the database
    for row in sec_db.get_rows(
        MultiDB.sqlfile("get_users.sql"),
        ID_schema=config.security_schema,
    ):
        db_record = BasicSecurityUser(*row)
        db_users[db_record.username] = db_record

    # create the set of operations to perform
    deletes = db_users.keys() - csv_users.keys()  # delete - user in db, not csv
    creates = csv_users.keys() - db_users.keys()  # create - in csv, not db
    updates = db_users.keys() & csv_users.keys()  # update - user in both

    for user in deletes:
        logger.warning("DELETE USER %s - delete is not currently implemented", user)
        result[user] = "ERROR"
        # result[user] = BULK_USER_STATUS_DELETED

    for user in updates:
        csv_record = csv_users[user]
        if bcrypt_check(csv_record.password, db_users[user].password_hash):
            logger.debug("OK USER %s", user)
            result[user] = "OK"
            continue
        logger.info("UPDATE USER %s", user)
        update_basic_security_user(config, sec_db, user, csv_record.password)
        result[user] = "UPDATED"

    for user in creates:
        csv_record = csv_users[user]
        logger.info("CREATE USER %s", user)
        sec_db.execute(
            MultiDB.sqlfile("create_user.sql"),
            ID_schema=config.security_schema,
            username=csv_record.username,
            firstname=csv_record.firstname,
            middlename=csv_record.middlename,
            lastname=csv_record.lastname,
            password_hash=bcrypt_hash(csv_record.password),
        )
        result[user] = "CREATED"

    return result


def ensure_basic_security_user(
    config: GlueConfig, sec_db: MultiDB, username: str, password: str
):
    """
    ensure that the basic security tables have a user entry for the given user
    """
    user = sec_db.get_rows(
        MultiDB.sqlfile("get_user.sql"),
        ID_schema=config.security_schema,
        username=username,
    )

    if len(user) == 1:
        logger.debug("found the user %s in the database", username)
        user_record = BasicSecurityUser(*user[0])
        if config.update_passwords:
            if bcrypt_check(password, user_record.password_hash):
                logger.info("found user %s in security db; password OK", username)
            else:
                logger.info("found user %s in security db; changing password", username)
                update_basic_security_user(config, sec_db, username, password)
        return
    if len(user) != 0:
        raise RuntimeError("expected exactly one response from the get_user query")

    logger.debug("the user %s was not found; creating...", username)

    sec_db.execute(
        MultiDB.sqlfile("create_user.sql"),
        ID_schema=config.security_schema,
        username=username,
        firstname=username,
        lastname="",
        password_hash=bcrypt_hash(password),
    )
    logger.debug("done")


def ensure_admin_role(config: GlueConfig, app_db: MultiDB, username: str):
    """
    ensure that the atlas admin user is an admin
    """
    # insert into ohdsi.sec_user_role (user_id, role_id) values (1000,2);
    for role in get_sec_roles(config, app_db):
        if role.login == username and role.role_id == ADMIN_ROLE_ID:
            # the user exists, our work here is done
            logger.info("the user %s already has the admin sec role", username)
            return

    logger.info(
        "the user %s does not appear to have the admin sec role; adding role...",
        username,
    )

    app_db.execute(
        MultiDB.sqlfile("add_admin_role.sql"),
        ID_schema=config.ohdsi_schema,
        LIT_admin_role_id=ADMIN_ROLE_ID,
        login=username,
    )
    logger.debug("done")


def derived_source_key(config: GlueConfig) -> str:
    """
    return a safely-formatted version of config.source_name to be used as a cdm
    source_key
    """
    return re.sub("[^A-Za-z0-9]", "_", config.source_name).strip("_")


def ensure_webapi_source(
    config: GlueConfig, app_db: MultiDB, webapi_version: semver.SemVer
):
    """
    ensure that the webapi source table has an entry for the current cdm config
    """

    if config.cdm_db_dialect in ("sqlserver", "sql server"):
        jdbc_url = (
            f"jdbc:sqlserver://{config.cdm_db_server}"
            f";databaseName={config.cdm_db_database}"
            f";user={config.cdm_db_username}"
            f";password={config.cdm_db_password}"
        )
    elif config.cdm_db_dialect == "postgresql":
        jdbc_url = (
            f"jdbc:postgresql://{config.cdm_db_server}"
            f"/{config.cdm_db_database}"
            f"?user={config.cdm_db_username}"
            f"&password={config.cdm_db_password}"
        )
    else:
        raise RuntimeError(
            "Unrecognized cdm database dialect: " + config.cdm_db_dialect
        )

    # see if a source exists
    existing_sources = [
        CDMSource(*row)
        for row in app_db.get_rows(
            MultiDB.sqlfile("get_sources.sql"),
            ID_schema=config.ohdsi_schema,
            source_key=config.source_key,
        )
    ]
    if len(existing_sources) == 0:
        # no source exists, create one
        create_source(config, app_db, jdbc_url, webapi_version)
        return

    if len(existing_sources) == 1:
        # there is a source, check it
        existing_source = existing_sources[0]
        if (
            existing_source.source_name == config.source_name
            and existing_source.source_connection == jdbc_url
            and existing_source.source_dialect == config.cdm_db_dialect
        ):
            # the source looks ok
            return

        # the source does not look right; update it
        update_source(config, app_db, jdbc_url, webapi_version)
        return

    # there is more than 1 existing source with that source_key... that's weird
    raise RuntimeError(
        f"Expected either no matching sources or exactly 1. Got these: "
        f"{existing_sources!r}"
    )


def ensure_webapi_source_daimons(config: GlueConfig, app_db: MultiDB):
    """
    ensure that the appropriate source_daimon entries exist for a particular source
    """
    # find out our source_id
    source_ids = app_db.get_column(
        MultiDB.sqlfile("get_source_id.sql"),
        ID_schema=config.ohdsi_schema,
        source_key=config.source_key,
    )
    if len(source_ids) != 1:
        # no daimons; create them
        raise RuntimeError(
            (
                "Expected exactly 1 source to exist with the given source key. Got "
                f"this list: {source_ids!r}"
            )
        )
    source_id = source_ids[0]

    # get the existing daimons for this id
    existing_source_daimons = [
        CDMSourceDaimon(*row)
        for row in app_db.get_rows(
            MultiDB.sqlfile("get_source_daimons.sql"),
            ID_schema=config.ohdsi_schema,
            source_id=source_id,
        )
    ]

    # this list specifies the 4 daimons we expect to exist for every source
    expected_daimons = [
        CDMSourceDaimon(
            source_daimon_id=-1,  # phony value
            source_id=source_id,
            daimon_type=0,
            table_qualifier=config.cdm_schema,
            priority=0,
        ),
        CDMSourceDaimon(
            source_daimon_id=-1,  # phony value
            source_id=source_id,
            daimon_type=1,
            table_qualifier=config.vocab_schema,
            priority=1,
        ),
        CDMSourceDaimon(
            source_daimon_id=-1,  # phony value
            source_id=source_id,
            daimon_type=2,
            table_qualifier=config.results_schema,
            priority=1,
        ),
        CDMSourceDaimon(
            source_daimon_id=-1,  # phony value
            source_id=source_id,
            daimon_type=5,
            table_qualifier=config.temp_schema,
            priority=0,
        ),
    ]
    for expected in expected_daimons:
        matching_daimons = [
            daimon
            for daimon in existing_source_daimons
            if daimon.daimon_type == expected.daimon_type
        ]
        if len(matching_daimons) == 0:
            # no such daimon exists; create it
            create_source_daimon(
                config,
                app_db,
                source_id,
                expected.daimon_type,
                expected.table_qualifier,
                expected.priority,
            )
            continue

        if len(matching_daimons) == 1:
            existing_daimon = matching_daimons[0]
            # verify it is a complete match
            if (
                existing_daimon.table_qualifier == expected.table_qualifier
                and existing_daimon.priority == expected.priority
            ):
                # complete match; done
                continue
            # incomplete match; update
            update_source_daimon(
                config,
                app_db,
                existing_daimon.source_daimon_id,
                existing_daimon.daimon_type,
                expected.table_qualifier,
                expected.priority,
            )
            continue

        # len is not 1 or 0. this is weird.
        raise RuntimeError(
            (
                "Expected either no matching source_daimons or exactly 1. Got these: "
                f"{matching_daimons!r}"
            )
        )


def update_source(
    config: GlueConfig,
    app_db: MultiDB,
    jdbc_url: str,
    webapi_version: semver.SemVer,
):
    """update a webapi CDM source entry"""
    if webapi_version >= "2.12.0":
        logger.debug("update_source selected v2 query")
        source_update_query = MultiDB.sqlfile("source_update-v2.sql")
    else:
        logger.debug("update_source selected v1 query")
        source_update_query = MultiDB.sqlfile("source_update-v1.sql")

    app_db.execute(
        source_update_query,
        ID_schema=config.ohdsi_schema,
        source_key=config.source_key,
        source_name=config.source_name,
        source_connection=jdbc_url,
        source_dialect=config.cdm_db_dialect,
        is_cache_enabled=config.source_cache,
    )


def create_source(
    config: GlueConfig,
    app_db: MultiDB,
    jdbc_url: str,
    webapi_version: semver.SemVer,
):
    """create a webapi CDM source entry"""
    if webapi_version >= "2.12.0":
        logger.debug("create_source selected v2 query")
        create_source_query = MultiDB.sqlfile("create_source-v2.sql")
    else:
        logger.debug("create_source selected v1 query")
        create_source_query = MultiDB.sqlfile("create_source-v1.sql")

    logger.debug("sending webapi create source query: %s", create_source_query)
    app_db.execute(
        create_source_query,
        ID_schema=config.ohdsi_schema,
        source_name=config.source_name,
        source_key=config.source_key,
        source_connection=jdbc_url,
        source_dialect=config.cdm_db_dialect,
        is_cache_enabled="TRUE" if config.source_cache else "FALSE",
    )


def update_source_daimon(
    config: GlueConfig,
    app_db: MultiDB,
    source_daimon_id: int,
    daimon_type: int,
    table_qualifier: str,
    priority: int,
):
    """create an existing webapi source_daimon entry"""
    app_db.execute(
        MultiDB.sqlfile("update_source_daimon.sql"),
        ID_schema=config.ohdsi_schema,
        source_daimon_id=source_daimon_id,
        daimon_type=daimon_type,
        table_qualifier=table_qualifier,
        priority=priority,
    )


def create_source_daimon(
    config: GlueConfig,
    app_db: MultiDB,
    source_id: int,
    daimon_type: int,
    table_qualifier: str,
    priority: int,
):
    """create a webapi source_daimon entry"""
    # create the daimons for this new source
    create_source_daimon_query = MultiDB.sqlfile("create_source_daimon.sql")
    logger.debug(
        "sending webapi create source_daimon query: %s", create_source_daimon_query
    )
    app_db.execute(
        create_source_daimon_query,
        ID_schema=config.ohdsi_schema,
        source_id=source_id,
        daimon_type=daimon_type,
        table_qualifier=table_qualifier,
        priority=priority,
    )
