#!/usr/bin/python3
""" module for capturing the app configuration """
# pylint: disable=too-few-public-methods
from typing import Optional

from basecfg import BaseCfg, opt


class GlueConfig(BaseCfg):
    """class which captures the runtime configuration of the app"""

    log_level: str = opt(
        default="DEBUG",
        doc="how verbosely to log (one of: DEBUG, INFO, WARNING, ERROR)",
        choices=["DEBUG", "INFO", "WARNING", "ERROR"],
    )

    log_dir: str = opt(
        default="logs",
        doc="directory in which to create run logs",
    )

    input_dir: str = opt(
        default="input",
        doc="directory from which to load CSV-format input data files",
    )

    batch_size: Optional[int] = opt(
        default=None,
        doc=(
            "batch size to use during bulk insert, see "
            "https://zillow.github.io/ctds/bulk_insert.html#batch-size"
        ),
    )

    atlas_username: str = opt(
        default="admin",
        doc="an admin user which will be created in the basic security database",
    )

    atlas_password: str = opt(
        default="",
        doc="the password associated the atlas_username account",
    )

    db_dialect: str = opt(
        default="postgresql",
        doc="the sql database dialect",
        choices=["postgresql", "sql server"],
    )

    db_server: str = opt(
        default="db:1433",
        doc="host address of the database to load data into",
    )

    db_username: str = opt(
        default="postgres",
        doc="username to use when connecting to the database",
    )

    db_password: str = opt(
        default="",
        doc="password associated with the given db_username",
    )

    db_database: str = opt(
        default="cdm",
        doc="name of database on the server to write to",
    )

    cdm_db_dialect: str = opt(
        default="postgresql",
        doc="sql database dialect of the OMOP CDM database to connect to WebAPI",
        choices=["postgresql", "sql server"],
    )

    cdm_db_server: str = opt(
        default="sourcedb:1433",
        doc="host address of the OMOP CDM database to connect to WebAPI",
    )

    cdm_db_username: str = opt(
        default="postgres",
        doc="username of the OMOP CDM database to connect to WebAPI",
    )

    cdm_db_password: str = opt(
        default="",
        doc="password of the OMOP CDM database to connect to WebAPI",
    )

    cdm_db_database: str = opt(
        default="cdm",
        doc="name of of the OMOP CDM database to connect to WebAPI",
    )

    security_db_dialect: str = opt(
        default="postgresql",
        doc="sql database dialect of the WebAPI basic security database",
        choices=["postgresql", "sql server"],
    )

    security_db_server: str = opt(
        default="sourcedb:1433",
        doc="host address of the WebAPI basic security database",
    )

    security_db_username: str = opt(
        default="postgres",
        doc="username of the WebAPI basic security database",
    )

    security_db_password: str = opt(
        default="",
        doc="password of the WebAPI basic security database",
    )

    security_db_database: str = opt(
        default="basic_security",
        doc="name of of the WebAPI basic security database",
    )

    webapi_addr: str = opt(
        default="webapi",
        doc="the hostname (and optional port) of the webapi instance",
    )

    webapi_tls: bool = opt(
        default=True,
        doc=(
            "boolean that determines if http or https should be used to "
            "communicate with webapi"
        ),
    )

    webapi_base_path: str = opt(
        default="/WebAPI",
        doc="the path to WebAPI on its host, this is almost always /WebAPI",
    )

    init_concept_hierarchy: bool = opt(
        default=True,
        doc=(
            "whether to establish the concept_hierarchy (a cached version of the "
            "OMOP vocabulary specific to the concepts found in your CDM)"
        ),
    )

    ohdsi_schema: str = opt(
        default="ohdsi",
        doc=(
            "the schema used by webapi to manage its own configuration and other "
            "state"
        ),
    )

    security_schema: str = opt(
        default="basic_security",
        doc="",
    )

    cdm_schema: str = opt(
        default="cdm",
        doc="",
    )

    cem_schema: str = opt(
        default="cemresults",
        doc='Common Evidence Model ("CEM") results schema',
    )

    results_schema: str = opt(
        default="results",
        doc="",
    )

    temp_schema: str = opt(
        default="temp",
        doc="",
    )

    vocab_schema: str = opt(
        default="vocabulary",
        doc="",
    )

    source_name: str = opt(
        default="My Cdm",
        doc=(
            "the name of the data source, used by webapi to refer to the data " "source"
        ),
    )

    source_cache: bool = opt(
        default=True,
        doc="determines is_cache_enabled when adding a CDM source to WebAPI",
    )

    source_key: Optional[str] = opt(
        default=None,
        doc=(
            "a key identifying the data source, used by webapi, if not given it "
            "will be derived from source_name"
        ),
    )

    enable_cem_results_init: bool = opt(
        default=False,
        doc=("enable creating the Common Evidence Model results schema"),
    )

    enable_concept_count_init: bool = opt(
        default=False,
        doc=(
            "enable creating the concept count table(s) (see: "
            "https://github.com/OHDSI/WebAPI/wiki/CDM-Configuration"
            "#concept-count-tables)"
            "NOTE: this assumes you have already run achilles"
        ),
    )

    enable_result_init: bool = opt(
        default=True,
        doc=(
            "enable setting up the results tables (see: https://github.com"
            "/OHDSI/WebAPI/wiki/CDM-Configuration#results-schema-setup)"
        ),
    )

    enable_source_setup: bool = opt(
        default=True,
        doc=(
            "enable setting up the WebAPI source & source_daimon tables (see: "
            "https://github.com/OHDSI/WebAPI/wiki/CDM-Configuration"
            "#source-and-source_daimon-table-setup)"
        ),
    )

    enable_basic_security: bool = opt(
        default=True,
        doc=(
            "enable setting up the basic security schema & table (see: "
            "https://github.com/OHDSI/WebAPI/wiki/Basic-Security-Configuration)"
        ),
    )

    update_passwords: bool = opt(
        default=False,
        doc=(
            "enable glue to update the password for existing atlas users when "
            "verifying the basic security configuration"
        ),
    )

    def app_db_params(self) -> tuple[str, str, str, str, str]:
        """returns the connection parameters associated with the app db"""
        return (
            self.db_dialect,
            self.db_server,
            self.db_username,
            self.db_password,
            self.db_database,
        )

    def cdm_db_params(self) -> tuple[str, str, str, str, str]:
        """returns the connection parameters associated with the cdm db"""
        return (
            self.cdm_db_dialect,
            self.cdm_db_server,
            self.cdm_db_username,
            self.cdm_db_password,
            self.cdm_db_database,
        )

    def security_db_params(self) -> tuple[str, str, str, str, str]:
        """returns the connection parameters associated with the security db"""
        return (
            self.security_db_dialect,
            self.security_db_server,
            self.security_db_username,
            self.security_db_password,
            self.security_db_database,
        )
