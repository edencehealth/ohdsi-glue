# OHDSI Glue

OHDSI Glue is a container designed specifically to facilitate the setup and ongoing maintenance of OHDSI & EHDEN tool deployments, including [Atlas](https://github.com/OHDSI/Atlas), [WebAPI](https://github.com/OHDSI/WebAPI), [Achilles](https://github.com/OHDSI/Achilles), [DataQualityDashboard](https://github.com/OHDSI/DataQualityDashboard), [CDMInspection](https://github.com/ehden/CDMInspection), [CatalogueExport](https://github.com/ehden/CatalogueExport), among others. The primary function of OHDSI Glue is to simplify the configuration process for WebAPI. It serves as a practical tool for users of the OHDSI & EHDEN suite, aiming to streamline operations and reduce manual intervention in maintaining the deployments.

## usage

- GitHub Repo: <https://github.com/edencehealth/ohdsi-glue>
- Docker Hub Repo: <https://hub.docker.com/r/edence/ohdsi-glue>

The container produces the following help text when invoked with the `-h` or `--help` arguments:

```
usage: glue [-h] [--version] [--log-level {DEBUG,INFO,WARNING,ERROR}]
            [--log-dir LOG_DIR] [--input-dir INPUT_DIR]
            [--batch-size BATCH_SIZE] [--atlas-username ATLAS_USERNAME]
            [--atlas-password ATLAS_PASSWORD]
            [--db-dialect {postgresql,sql server}] [--db-server DB_SERVER]
            [--db-username DB_USERNAME] [--db-password DB_PASSWORD]
            [--db-database DB_DATABASE]
            [--cdm-db-dialect {postgresql,sql server}]
            [--cdm-db-server CDM_DB_SERVER]
            [--cdm-db-username CDM_DB_USERNAME]
            [--cdm-db-password CDM_DB_PASSWORD]
            [--cdm-db-database CDM_DB_DATABASE]
            [--security-db-dialect {postgresql,sql server}]
            [--security-db-server SECURITY_DB_SERVER]
            [--security-db-username SECURITY_DB_USERNAME]
            [--security-db-password SECURITY_DB_PASSWORD]
            [--security-db-database SECURITY_DB_DATABASE]
            [--webapi-addr WEBAPI_ADDR] [--webapi-tls | --no-webapi-tls]
            [--webapi-base-path WEBAPI_BASE_PATH]
            [--init-concept-hierarchy | --no-init-concept-hierarchy]
            [--ohdsi-schema OHDSI_SCHEMA] [--security-schema SECURITY_SCHEMA]
            [--cdm-schema CDM_SCHEMA] [--cem-schema CEM_SCHEMA]
            [--results-schema RESULTS_SCHEMA] [--temp-schema TEMP_SCHEMA]
            [--vocab-schema VOCAB_SCHEMA] [--source-name SOURCE_NAME]
            [--source-cache | --no-source-cache] [--source-key SOURCE_KEY]
            [--enable-cem-results-init | --no-enable-cem-results-init]
            [--enable-concept-count-init | --no-enable-concept-count-init]
            [--enable-result-init | --no-enable-result-init]
            [--enable-source-setup | --no-enable-source-setup]
            [--enable-basic-security | --no-enable-basic-security]
            [--update-passwords | --no-update-passwords]
            [--bulk-user-file BULK_USER_FILE] [--db-timeout DB_TIMEOUT]

Utility for working with OHDSI WebAPI and related apps

options:
  -h, --help            show this help message and exit
  --version             show program's version number and exit
  --log-level {DEBUG,INFO,WARNING,ERROR}
                        how verbosely to log (one of: DEBUG, INFO, WARNING,
                        ERROR) (default: 'DEBUG')
  --log-dir LOG_DIR     directory in which to create run logs (default:
                        'logs')
  --input-dir INPUT_DIR
                        directory from which to load CSV-format input data
                        files (default: 'input')
  --batch-size BATCH_SIZE
                        batch size to use during bulk insert, see
                        https://zillow.github.io/ctds/bulk_insert.html#batch-
                        size (default: None)
  --atlas-username ATLAS_USERNAME
                        an admin user which will be created in the basic
                        security database (default: 'admin')
  --atlas-password ATLAS_PASSWORD
                        the password associated the atlas_username account
                        (default: '')
  --db-dialect {postgresql,sql server}
                        the sql database dialect (default: 'postgresql')
  --db-server DB_SERVER
                        host address of the database to load data into
                        (default: 'db:1433')
  --db-username DB_USERNAME
                        username to use when connecting to the database
                        (default: 'postgres')
  --db-password DB_PASSWORD
                        password associated with the given db_username
                        (default: '')
  --db-database DB_DATABASE
                        name of database on the server to write to (default:
                        'cdm')
  --cdm-db-dialect {postgresql,sql server}
                        sql database dialect of the OMOP CDM database to
                        connect to WebAPI (default: 'postgresql')
  --cdm-db-server CDM_DB_SERVER
                        host address of the OMOP CDM database to connect to
                        WebAPI (default: 'sourcedb:1433')
  --cdm-db-username CDM_DB_USERNAME
                        username of the OMOP CDM database to connect to WebAPI
                        (default: 'postgres')
  --cdm-db-password CDM_DB_PASSWORD
                        password of the OMOP CDM database to connect to WebAPI
                        (default: '')
  --cdm-db-database CDM_DB_DATABASE
                        name of of the OMOP CDM database to connect to WebAPI
                        (default: 'cdm')
  --security-db-dialect {postgresql,sql server}
                        sql database dialect of the WebAPI basic security
                        database (default: 'postgresql')
  --security-db-server SECURITY_DB_SERVER
                        host address of the WebAPI basic security database
                        (default: 'sourcedb:1433')
  --security-db-username SECURITY_DB_USERNAME
                        username of the WebAPI basic security database
                        (default: 'postgres')
  --security-db-password SECURITY_DB_PASSWORD
                        password of the WebAPI basic security database
                        (default: '')
  --security-db-database SECURITY_DB_DATABASE
                        name of of the WebAPI basic security database
                        (default: 'basic_security')
  --webapi-addr WEBAPI_ADDR
                        the hostname (and optional port) of the webapi
                        instance (default: 'webapi')
  --webapi-tls, --no-webapi-tls
                        boolean that determines if http or https should be
                        used to communicate with webapi (default: True)
  --webapi-base-path WEBAPI_BASE_PATH
                        the path to WebAPI on its host, this is almost always
                        /WebAPI (default: '/WebAPI')
  --init-concept-hierarchy, --no-init-concept-hierarchy
                        whether to establish the concept_hierarchy (a cached
                        version of the OMOP vocabulary specific to the
                        concepts found in your CDM) (default: True)
  --ohdsi-schema OHDSI_SCHEMA
                        the schema used by webapi to manage its own
                        configuration and other state (default: 'ohdsi')
  --security-schema SECURITY_SCHEMA
                        (default: 'basic_security')
  --cdm-schema CDM_SCHEMA
                        (default: 'cdm')
  --cem-schema CEM_SCHEMA
                        Common Evidence Model ("CEM") results schema (default:
                        'cemresults')
  --results-schema RESULTS_SCHEMA
                        (default: 'results')
  --temp-schema TEMP_SCHEMA
                        (default: 'temp')
  --vocab-schema VOCAB_SCHEMA
                        (default: 'vocabulary')
  --source-name SOURCE_NAME
                        the name of the data source, used by webapi to refer
                        to the data source (default: 'My Cdm')
  --source-cache, --no-source-cache
                        determines is_cache_enabled when adding a CDM source
                        to WebAPI (default: True)
  --source-key SOURCE_KEY
                        a key identifying the data source, used by webapi, if
                        not given it will be derived from source_name
                        (default: None)
  --enable-cem-results-init, --no-enable-cem-results-init
                        enable creating the Common Evidence Model results
                        schema (default: False)
  --enable-concept-count-init, --no-enable-concept-count-init
                        enable creating the concept count table(s) (see:
                        https://github.com/OHDSI/WebAPI/wiki/CDM-
                        Configuration#concept-count-tables)NOTE: this assumes
                        you have already run achilles (default: False)
  --enable-result-init, --no-enable-result-init
                        enable setting up the results tables (see:
                        https://github.com/OHDSI/WebAPI/wiki/CDM-
                        Configuration#results-schema-setup) (default: True)
  --enable-source-setup, --no-enable-source-setup
                        enable setting up the WebAPI source & source_daimon
                        tables (see: https://github.com/OHDSI/WebAPI/wiki/CDM-
                        Configuration#source-and-source_daimon-table-setup)
                        (default: True)
  --enable-basic-security, --no-enable-basic-security
                        enable setting up the basic security schema & table
                        (see: https://github.com/OHDSI/WebAPI/wiki/Basic-
                        Security-Configuration) (default: True)
  --update-passwords, --no-update-passwords
                        enable glue to update the password for existing atlas
                        users when verifying the basic security configuration
                        (default: False)
  --bulk-user-file BULK_USER_FILE
                        create/update user accounts from a csv file; requires
                        these headings:
                        username,password,firstname,middlename,lastname
                        (default: None)
  --db-timeout DB_TIMEOUT
                        timeout for database requests, in seconds (default:
                        3600)

```

## resources

- [WebAPI CDM configuration docs](https://github.com/OHDSI/WebAPI/wiki/CDM-Configuration) - documentation for most of the tasks we're trying to accomplish
- [WebAPI git trunk's pom.xml](https://github.com/OHDSI/WebAPI/blob/master/pom.xml) - useful resource to find settings that need setting
- [cTDS documentation](https://zillow.github.io/ctds/index.html) - docs for our SQL Server database library
- [psycopg documentation](https://www.psycopg.org/docs/index.html) - docs for our PostgreSQL database library
- [PEP 249 -- Python Database API Specification v2.0](https://www.python.org/dev/peps/pep-0249/)
