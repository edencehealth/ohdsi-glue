# OHDSI Glue

a utility container for configuring WebAPI

This container is currently able to connect CDM sources to WebAPI, however unfortunately webapi does not currently build the security contexts for the added sources until it has been restarted.

## resources

* [WebAPI CDM configuration docs](https://github.com/OHDSI/WebAPI/wiki/CDM-Configuration) - documentation for most of the tasks we're trying to accomplish
* [WebAPI git trunk's pom.xml](https://github.com/OHDSI/WebAPI/blob/master/pom.xml) - useful resource to find settings that need setting
* [cTDS documentation](https://zillow.github.io/ctds/index.html) - docs for our SQL Server database library
* [psycopg documentation](https://www.psycopg.org/docs/index.html) - docs for our PostgreSQL database library
* [PEP 249 -- Python Database API Specification v2.0](https://www.python.org/dev/peps/pep-0249/)
