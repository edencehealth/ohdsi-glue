#!/usr/bin/env python3
"""implementation of class for working with postgres and mssql databases"""

# pylint: disable=R0913
import contextlib
import functools
import logging
import re
import string
from importlib import resources
from typing import Any, Dict, Final, List, NamedTuple, Tuple

from .mssql import connect as mssql_connect
from .postgres import connect as pg_connect

sql_dir = resources.files("glue.sql")
logger = logging.getLogger(__name__)

# note: if you change these you have to update table_info and list_tables
identifier_prefix: Final = "ID_"
literal_prefix: Final = "LIT_"


@functools.cache
def sqlfile(filename: str) -> str:
    """
    return the contents of the file in the sql subdir of this package which
    has the given filename
    """
    sql_file = sql_dir.joinpath(filename)
    return sql_file.read_text()


def interpolation_safe(value: str) -> bool:
    """
    return true if the given value is safe to use as a sql identifier or literal
    """
    # unicode word characters: "this includes most characters that can be part of a
    # word in any language, as well as numbers and the underscore"
    if re.match(r"^\w{1,128}$", value):
        return True
    return False


class KeyFormatter(dict):
    """
    dict subclass which handles missing keys by returning the key itself
    (after formatting the key with the given key_format)
    """

    # this class is used by the adjust_paramstyle function

    def __init__(self, key_format: str, *args, **kwargs):
        """
        creates a new instance with the given key_format (a str.format-style
        string format template)
        """
        # https://docs.python.org/3/library/string.html#format-string-syntax
        self.key_format = key_format
        super().__init__(*args, **kwargs)

    def __missing__(self, key) -> str:
        """returns the key itself, formatted by key_format"""
        return self.key_format.format(key)


class ColumnInfo(NamedTuple):
    """Contains information about the structure of a column in a database"""

    position: int
    nullable: bool
    data_type: str
    max_len: int
    precision: int
    charset: str


class MultiDB(contextlib.AbstractContextManager):
    """generic database wrapper"""

    def __init__(
        self,
        dialect: str,
        server: str,
        user: str,
        password: str,
        database: str,
        mssql_timeout: int = 5,
    ):
        self.dialect = dialect
        self.server = server
        self.database = database
        if dialect == "sql server":
            self.cnxn = mssql_connect(
                server=server,
                user=user,
                password=password,
                database=database,
                timeout=mssql_timeout,
            )
            # attempt to change the default database on the connection, this
            # should already be handled by mssql_connect but it may not be
            # working
            self.execute("use {ID_database}", ID_database=database)
        elif dialect == "postgresql":
            self.cnxn = pg_connect(
                server=server, user=user, password=password, database=database
            )
        else:
            raise RuntimeError("Unrecognized database dialect: " + dialect)

    def __exit__(self, *args, **kwargs):
        """close the database connection"""
        return self.cnxn.__exit__(*args, **kwargs)

    def query(self, query: str, **params: Dict[str, Any]) -> Tuple[str, Dict[str, Any]]:
        """
        given a sql query with python str.format-style paramater references,
        adjust the paramater references to use the paramstyle appropriate for
        the DB API dialect;
        additionally: if the given params start with the identifier_prefix or
        the literal_prefix, safety-check those values then interpolate them
        into the query
        returns a query_str, params_dict tuple suitable for passing to the db
        driver
        see: https://www.python.org/dev/peps/pep-0249/#paramstyle
        and: https://docs.python.org/3/library/string.html#format-string-syntax
        """
        # the query:
        #   select * from turtles where (name={turtle})
        # is changed to this when the dialect is postgres:
        #   select * from turtles where (name=%(turtle)s)
        # and this when the dialect is sql server:
        #   select * from turtles where (name=:turtle)

        # sql identifiers and literals get safety-checked and are then
        # string-interpolated into the query; other paramaters are passed to
        # the db driver as proper paramaters
        safe_values: Dict[str, Any] = {}
        for param in tuple(params.keys()):
            if param.startswith(identifier_prefix) or param.startswith(literal_prefix):
                param_value = str(params[param])
                if not interpolation_safe(param_value):
                    raise RuntimeError(
                        f"unsafe value encountered in interpolated param "
                        f"{param}: '{param_value}'"
                    )
                safe_values[param] = param_value
                del params[param]
        if self.dialect == "sql server":
            formatter = KeyFormatter(":{}", **safe_values)
        elif self.dialect == "postgresql":
            formatter = KeyFormatter("%({})s", **safe_values)
        else:
            raise RuntimeError("Unrecognized database dialect: " + self.dialect)

        return string.Formatter().vformat(query, [], formatter), params

    def get_column(self, sql: str, **params) -> List[Any]:
        """
        executes the given sql query, fetches, and returns the results
        if the results contain exactly one column, that column will be returned directly
        e.g. "SELECT name FROM ships" -> ["Rocinante", "Enterprise", "Orion III"]
        ...rather than [["Rocinante"], ["Enterprise"], ["Orion III"]]
        """
        with self.cnxn.cursor() as cursor:
            final_query, filtered_params = self.query(sql, **params)
            logger.debug(
                "get_column: sending query (with %s-params): %s",
                len(filtered_params),
                final_query,
            )
            cursor.execute(final_query, filtered_params)
            self.cnxn.commit()
            columns = len(cursor.description)
            rows = cursor.fetchall()

        if columns != 1:
            raise RuntimeError(
                f"get_column returned a result set with {columns} columns instead of "
                "the expected 1 column"
            )

        return [row[0] for row in rows]

    def get_rows(self, sql: str, **params) -> List[Any]:
        """
        executes the given sql query, fetches, transforms, and returns the results;
        an optional transformer function can be given which will be applied to each
        row of the results before they are returned
        """
        with self.cnxn.cursor() as cursor:
            final_query, filtered_params = self.query(sql, **params)
            logger.debug(
                "get_rows: sending query (with %s-params): %s",
                len(filtered_params),
                final_query,
            )
            cursor.execute(final_query, filtered_params)
            self.cnxn.commit()
            rows = cursor.fetchall()

        return rows

    def execute(self, sql: str, **params) -> None:
        """executes the given sql query on the given connection"""
        with self.cnxn.cursor() as cursor:
            final_query, filtered_params = self.query(sql, **params)
            logger.debug(
                "execute: sending query (with %s-params): %s",
                len(filtered_params),
                final_query,
            )
            cursor.execute(final_query, filtered_params)
            self.cnxn.commit()

    def table_info(self, table_name: str) -> Dict[str, ColumnInfo]:
        """
        queries the inforamtion schema about the given table
        """
        info = self.get_rows(sqlfile("table_info.sql"), table_name=table_name)
        if not info:
            raise RuntimeError(
                f"table_info couldn't query INFORMATION_SCHEMA about table {table_name}"
            )

        return {
            row.COLUMN_NAME: ColumnInfo(
                position=row.ORDINAL_POSITION,
                nullable=row.IS_NULLABLE == "YES",
                data_type=row.DATA_TYPE,
                max_len=row.CHARACTER_MAXIMUM_LENGTH,
                precision=row.NUMERIC_PRECISION,
                charset=row.CHARACTER_SET_NAME,
            )
            for row in info
        }

    def list_schemas(self) -> List[str]:
        """return a list of schemas in the database"""
        return self.get_column(sqlfile("list_schemas.sql"))

    def list_tables(self, schema: str) -> List[str]:
        """return a list of tables in the given schema"""
        return self.get_column(sqlfile("list_tables.sql"), schema=schema)

    @staticmethod
    def sqlfile(filename: str) -> str:
        """
        return the contents of the file in the sql subdir of this package which
        has the given filename
        """
        return sqlfile(filename)
