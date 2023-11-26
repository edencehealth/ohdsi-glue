#!/usr/bin/env python3
""" classes and functions for manipulating the WebAPI appdb directly """
# pylint: disable=R0913
import logging
import re
from typing import List, NamedTuple

from . import semver
from .config import GlueConfig
from .db.multidb import MultiDB
from .util.security import bcrypt_hash

logger = logging.getLogger(__name__)

ADMIN_ROLE_ID = 2  # webapi sec_user_role role_id


class SecRole(NamedTuple):
    """Contains information about a webapi security role"""

    login: str
    user_id: int
    role_name: str
    role_id: int


class CDMSource(NamedTuple):
    """Contains information about a webapi cdm source"""

    source_id: int
    source_name: str
    source_key: str
    source_connection: str
    source_dialect: str


class CDMSourceDaimon(NamedTuple):
    """Contains information about a webapi cdm source_daimon"""

    source_daimon_id: int
    source_id: int
    daimon_type: int
    table_qualifier: str
    priority: int


def get_sec_roles(config: GlueConfig, app_db: MultiDB) -> List[SecRole]:
    """return a list of user records from the webapi sec_* databases"""
    # NOTE: this is not an f-string, these values are expanded by multidb
    query = """
    SELECT
        login,
        sec_user.id AS user_id,
        sec_role.name AS role_name,
        sec_role.id AS role_id
    FROM
        {ID_schema}.sec_user
        JOIN {ID_schema}.sec_user_role
            ON {ID_schema}.sec_user.id = {ID_schema}.sec_user_role.user_id
        JOIN {ID_schema}.sec_role
            ON {ID_schema}.sec_user_role.role_id = {ID_schema}.sec_role.id;
    """.strip()
    return [
        SecRole(*row) for row in app_db.get_rows(query, ID_schema=config.ohdsi_schema)
    ]


def update_basic_security_user(
    config: GlueConfig, sec_db: MultiDB, username: str, password: str
):
    """update the password for an existing basic security user"""

    logger.info("updating the password for the user %s", username)

    update_password_query = """
    UPDATE
        {ID_schema}.users
    SET
        password_hash={password_hash}
    WHERE
        username={username};
    """.strip()
    sec_db.execute(
        update_password_query,
        ID_schema=config.security_schema,
        username=username,
        password_hash=bcrypt_hash(password),
    )
    logger.debug("done")


def ensure_basic_security_user(
    config: GlueConfig, sec_db: MultiDB, username: str, password: str
):
    """
    ensure that the basic security tables have a user entry for the given user
    """
    get_users_query = """
    SELECT
        username
    FROM
        {ID_schema}.users;
    """.strip()
    users = sec_db.get_column(get_users_query, ID_schema=config.security_schema)
    if username in users:
        logger.debug("found the user %s in the database", username)
        if config.update_passwords:
            update_basic_security_user(config, sec_db, username, password)
        return

    logger.debug("the user %s was not found; creating...", username)

    create_user_query = """
    INSERT INTO
        {ID_schema}.users (username, firstname, lastname, password_hash)
    VALUES
        (
            {username},
            {firstname},
            {lastname},
            {password_hash}
        );
    """.strip()
    sec_db.execute(
        create_user_query,
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

    add_admin_role_query = """
    INSERT INTO
        {ID_schema}.sec_user_role (user_id, role_id)
    (
        SELECT
            id,
            {LIT_admin_role_id}
        FROM
            {ID_schema}.sec_user
        WHERE
            login = {login}
    );
    """.strip()
    app_db.execute(
        add_admin_role_query,
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
    get_sources_query = """
    SELECT source_id, source_name, source_key, source_connection, source_dialect
    FROM {ID_schema}.source
    WHERE source_key = {source_key};
    """.strip()
    existing_sources = [
        CDMSource(*row)
        for row in app_db.get_rows(
            get_sources_query,
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
    source_id_query = """
    SELECT source_id
    FROM {ID_schema}.source
    WHERE source_key = {source_key};
    """.strip()
    source_ids = app_db.get_column(
        source_id_query,
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
    get_source_daimons_query = """
    SELECT source_daimon_id, source_id, daimon_type, table_qualifier, priority
    FROM {ID_schema}.source_daimon
    WHERE source_id = {source_id};
    """.strip()
    existing_source_daimons = [
        CDMSourceDaimon(*row)
        for row in app_db.get_rows(
            get_source_daimons_query,
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
        logger.debug("update_source selected >=2.12.0 query")
        # this version includes "is_cache_enabled"
        source_update_query = """
        UPDATE {ID_schema}.source
        SET
            source_name = {source_name},
            source_connection = {source_connection},
            source_dialect = {source_dialect},
            is_cache_enabled = {is_cache_enabled}
        WHERE source_key = {source_key};
        """.strip()
    else:
        logger.debug("update_source selected <2.12.0 query")
        source_update_query = """
        UPDATE {ID_schema}.source
        SET
            source_name = {source_name},
            source_connection = {source_connection},
            source_dialect = {source_dialect}
        WHERE source_key = {source_key};
        """.strip()
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
        logger.debug("create_source selected >=2.12.0 query")
        # this version includes "is_cache_enabled"
        create_source_query = """
        INSERT INTO {ID_schema}.source
            (source_id, source_name, source_key, source_connection, source_dialect,
             is_cache_enabled)
        VALUES
            (nextval('{ID_schema}.source_sequence'),
            {source_name},
            {source_key},
            {source_connection},
            {source_dialect},
            {is_cache_enabled});
        """.strip()
    else:
        logger.debug("create_source selected <2.12.0 query")
        create_source_query = """
        INSERT INTO {ID_schema}.source
            (source_id, source_name, source_key, source_connection, source_dialect)
        VALUES
            (nextval('{ID_schema}.source_sequence'),
            {source_name},
            {source_key},
            {source_connection},
            {source_dialect});
        """.strip()
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
    update_source_daimon_query = """
    UPDATE {ID_schema}.source_daimon
    SET
        daimon_type = {daimon_type},
        table_qualifier = {table_qualifier},
        priority = {priority}
    WHERE source_daimon_id = {source_daimon_id};
    """.strip()
    app_db.execute(
        update_source_daimon_query,
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
    create_source_daimon_query = """
    INSERT INTO {ID_schema}.source_daimon
        (source_daimon_id, source_id, daimon_type, table_qualifier, priority)
    VALUES
        (nextval('{ID_schema}.source_daimon_sequence'),
        {source_id},
        {daimon_type},
        {table_qualifier},
        {priority});
    """.strip()
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
