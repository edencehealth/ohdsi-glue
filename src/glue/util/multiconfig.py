#!/usr/bin/python3
""" module for capturing the app configuration """
import argparse
import json
import os
import typing
from dataclasses import asdict, dataclass, field, fields
from typing import Any, Dict, Mapping, Optional

# these variables can be updated in the event that we want to switch to namespaced
# metadata
doc: str = "doc"  # pylint: disable=C0103 # this makes the module a bit easier to read
require: str = "require"
options: str = "options"
parser: str = "parser"
if_empty_use: str = "if_empty_use"

APP_DESCRIPTION: str = "OHDSI Glue"

# The code takes its configuration in four sequential steps:
# 1. Default config values are defined here in the MultiConfig class
# 2. The `config.json` file (if it exists) is loaded and any config
#    values in it will override the defaults (you may override the
#    location of config.json at runtime by changing the
#    JSON_CONFIG_PATH environment variable)
# 3. Environment variables (if they are set) will override any config
#    values set in the previous steps. For example the log_level option
#    will be updated if the LOG_LEVEL environment variable is set
# 4. Command-line arguments allow overriding all previous steps (an
#    argparser is automatically built and run based on the configuration options
#    defined above) For example the log_level option can be updated by
#    giving the --log-level argument


def parse_bool(argument: str) -> bool:
    """parses the given argument string and returns a boolean evaluation"""
    return argument.lower().strip() in ("1", "enable", "on", "true", "y", "yes")


@dataclass
class MultiConfig:
    """dataclass which captures the runtime configuration of the app"""

    # pylint: disable=R0902 # this is a config class

    #
    # HERE BEGINS the portion of the class where configuration options are
    # defined. See: https://docs.python.org/3.7/library/dataclasses.html
    #

    # always specify a default (even if its just ""), this allows the
    # object to be created and subsequently updated with missing values

    log_level: str = field(
        default="DEBUG",
        metadata={
            doc: "how verbosely to log (one of: DEBUG, INFO, WARNING, ERROR)",
            options: ["DEBUG", "INFO", "WARNING", "ERROR"],
        },
    )
    log_dir: str = field(
        default="logs",
        metadata={doc: "directory in which to create run logs"},
    )
    input_dir: str = field(
        default="input",
        metadata={doc: "directory from which to load CSV-format input data files"},
    )
    batch_size: Optional[int] = field(
        default=None,
        metadata={
            doc: (
                "batch size to use during bulk insert, see "
                "https://zillow.github.io/ctds/bulk_insert.html#batch-size"
            )
        },
    )
    atlas_username: str = field(
        default="admin",
        metadata={
            doc: "an admin user which will be created in the basic security database",
        },
    )
    atlas_password: str = field(
        default="",
        metadata={
            doc: "the password associated the atlas_username account",
        },
    )
    db_dialect: str = field(
        default="postgresql",
        metadata={
            doc: "the sql database dialect",
            options: ["postgresql", "sql server"],
        },
    )
    db_server: str = field(
        default="db:1433",
        metadata={doc: "host address of the database to load data into"},
    )
    db_username: str = field(
        default="postgres",
        metadata={doc: "username to use when connecting to the database"},
    )
    db_password: str = field(
        default="",
        repr=False,
        metadata={doc: "password associated with the given db_username"},
    )
    db_database: str = field(
        default="cdm",
        metadata={
            doc: "name of database on the server to write to",
        },
    )
    cdm_db_dialect: str = field(
        default="postgresql",
        metadata={
            doc: "sql database dialect of the OMOP CDM database to connect to WebAPI",
            options: ["postgresql", "sql server"],
        },
    )
    cdm_db_server: str = field(
        default="sourcedb:1433",
        metadata={doc: "host address of the OMOP CDM database to connect to WebAPI"},
    )
    cdm_db_username: str = field(
        default="postgres",
        metadata={doc: "username of the OMOP CDM database to connect to WebAPI"},
    )
    cdm_db_password: str = field(
        default="",
        repr=False,
        metadata={doc: "password of the OMOP CDM database to connect to WebAPI"},
    )
    cdm_db_database: str = field(
        default="cdm",
        metadata={
            doc: "name of of the OMOP CDM database to connect to WebAPI",
        },
    )
    security_db_dialect: str = field(
        default="postgresql",
        metadata={
            doc: "sql database dialect of the WebAPI basic security database",
            options: ["postgresql", "sql server"],
        },
    )
    security_db_server: str = field(
        default="sourcedb:1433",
        metadata={doc: "host address of the WebAPI basic security database"},
    )
    security_db_username: str = field(
        default="postgres",
        metadata={doc: "username of the WebAPI basic security database"},
    )
    security_db_password: str = field(
        default="",
        repr=False,
        metadata={doc: "password of the WebAPI basic security database"},
    )
    security_db_database: str = field(
        default="basic_security",
        metadata={
            doc: "name of of the WebAPI basic security database",
        },
    )
    webapi_addr: str = field(
        default="webapi",
        metadata={
            doc: "the hostname (and optional port) of the webapi instance",
        },
    )
    webapi_tls: bool = field(
        default=True,
        metadata={
            doc: (
                "boolean that determines if http or https should be used to "
                "communicate with webapi"
            ),
            parser: parse_bool,
        },
    )
    webapi_base_path: str = field(
        default="/WebAPI",
        metadata={
            doc: "the path to WebAPI on its host, this is almost always /WebAPI",
        },
    )
    init_concept_hierarchy: bool = field(
        default=True,
        metadata={
            doc: (
                "whether to establish the concept_hierarchy (a cached version of the "
                "OMOP vocabulary specific to the concepts found in your CDM)"
            ),
            parser: parse_bool,
        },
    )
    ohdsi_schema: str = field(
        default="ohdsi",
        metadata={
            doc: (
                "the schema used by webapi to manage its own configuration and other "
                "state"
            ),
        },
    )
    security_schema: str = field(
        default="basic_security",
        metadata={
            doc: "",
        },
    )
    cdm_schema: str = field(
        default="cdm",
        metadata={
            doc: "",
        },
    )
    results_schema: str = field(
        default="results",
        metadata={
            doc: "",
        },
    )
    temp_schema: str = field(
        default="temp",
        metadata={
            doc: "",
        },
    )
    vocab_schema: str = field(
        default="vocabulary",
        metadata={
            doc: "",
        },
    )
    source_name: str = field(
        default="My Cdm",
        metadata={
            doc: (
                "the name of the data source, used by webapi to refer to the data "
                "source"
            ),
        },
    )
    source_cache: bool = field(
        default=True,
        metadata={
            doc: "determines is_cache_enabled when adding a CDM source to WebAPI",
        },
    )
    source_key: Optional[str] = field(
        default=None,
        metadata={
            doc: (
                "a key identifying the data source, used by webapi, if not given it "
                "will be derived from source_name"
            )
        },
    )
    enable_result_init: bool = field(
        default=True,
        metadata={
            doc: (
                "enable setting up the results tables (see: https://github.com"
                "/OHDSI/WebAPI/wiki/CDM-Configuration#results-schema-setup)"
            ),
            parser: parse_bool,
        },
    )
    enable_source_setup: bool = field(
        default=True,
        metadata={
            doc: (
                "enable setting up the WebAPI source & source_daimon tables (see: "
                "https://github.com/OHDSI/WebAPI/wiki/CDM-Configuration"
                "#source-and-source_daimon-table-setup)"
            ),
            parser: parse_bool,
        },
    )
    enable_basic_security: bool = field(
        default=True,
        metadata={
            doc: (
                "enable setting up the basic security schema & table (see: "
                "https://github.com/OHDSI/WebAPI/wiki/Basic-Security-Configuration)"
            ),
            parser: parse_bool,
        },
    )

    #
    # EVERYTHING BELOW this point is for config loading & validation, no
    # additional configuration options are found below.
    #

    def __post_init__(self):
        """load the app configuration from the various sources"""
        json_path = os.environ.get("JSON_CONFIG_PATH", "config.json")
        self.update_from_json(json_path)
        self.update_from_environ()
        self.update_from_args()
        self.validate()

    def update(self, data: Mapping) -> None:
        """
        given a dict or other mapping, update self with the values therein, but
        only update the existing class attributes

        this method is called by all the other update methods
        """
        config_fields = {x.name: x for x in fields(self)}
        for item_name, item_value in data.items():
            # only update attributes that already exist
            if item_name not in config_fields:
                continue
            config_field = config_fields[item_name]
            # if the field has a parser defined, use it; otherwise use its constructor
            field_parser = config_field.metadata.get(parser, None)
            if field_parser is None:
                field_parser = not_optional(config_field.type)
            setattr(self, item_name, field_parser(item_value))

    def update_from_environ(self) -> None:
        """update the settings from values in the environment"""
        self.update({name.lower(): value for name, value in os.environ.items()})

    def update_from_json(
        self, json_path: str, required=False, encoding="utf-8"
    ) -> None:
        """update the settings from values in a json file"""
        if not os.path.isfile(json_path):
            if required:
                raise RuntimeError(
                    f"required json config file {json_path} was not found"
                )
            # no file, no exception to raise = nothing left to do
            return
        with open(json_path, "rt", encoding=encoding) as json_fp:
            json_data = json.load(json_fp)
            self.update(json_data)

    def update_from_args(self) -> None:
        """generates an argument parser and runs it updating the values as needed"""
        argp = argparse.ArgumentParser(description=APP_DESCRIPTION, prog=__package__)
        for config_field in fields(self):
            still_has_default_value = (
                getattr(self, config_field.name) == config_field.default
            )
            if require in config_field.metadata and still_has_default_value:
                argp.add_argument(
                    "--" + config_field.name.replace("_", "-"),
                    dest=config_field.name,
                    help=config_field.metadata[doc],
                    required=True,
                )
            else:
                argp.add_argument(
                    "--" + config_field.name.replace("_", "-"),
                    dest=config_field.name,
                    help=config_field.metadata[doc],
                )

        self.update({k: v for k, v in vars(argp.parse_args()).items() if v is not None})

    def validate(self) -> None:
        """validate the given configuration options"""
        # validate the data (for now just verify against the "options" setting)
        # i.e. does the value loaded match one of the options defined for this
        # configuration option? e.g. self.color in ['red', 'green', 'blue']
        for config_field in fields(self):
            field_name = config_field.name
            field_value = getattr(self, field_name)
            field_options = config_field.metadata.get(options, None)
            field_alternate_value = config_field.metadata.get(if_empty_use, None)
            if field_value == "" and field_alternate_value is not None:
                field_value = getattr(self, field_alternate_value)
                setattr(self, field_name, field_value)
            if field_options is None or field_value in field_options:
                # everything is fine
                continue
            field_option_list = ", ".join([str(x) for x in field_options])
            raise RuntimeError(
                (
                    f"Invalid value ({field_value}) for configuration option: "
                    f"{config_field.name}. It must be one of: {field_option_list}"
                )
            )

    def asdict(self) -> Dict[str, Any]:
        """return a representation of the config as a dictionary"""
        return asdict(self)


def not_optional(field_type: Any) -> Any:
    """
    given a field type, if it is an Optional type, try to return the base type;
    if that can't be handled, return field_type argument unchanged

    for example:
        Optional[int] -> int
    or, more precisely:
        Union[int, NoneType] -> int
    """
    if typing.get_origin(field_type) is typing.Union:
        type_args = typing.get_args(field_type)
        # the following check is a little tricky:
        # "type_args[1] is None" does not work
        # "isinstance(type_args[1], None)" does not work
        # "isinstance(type_args[1], type(None))" does not work
        # "issubclass(type_args[1], None)" does not work
        # "issubclass(type_args[1], type(None))" DOES work, but is that better?
        if len(type_args) == 2 and type_args[1] == type(None):  # noqa: E721
            return type_args[0]
    return field_type
