""" helpers related to files in csv format"""
import csv
import logging
import re
from typing import List, NamedTuple, Type, TypeVar

logger = logging.getLogger(__name__)

T = TypeVar("T", bound=NamedTuple)


def is_empty(data: str) -> bool:
    """return true if the given data is empty or purely whitespace"""
    return bool(re.match(r"^\s*$", data))


def load_typed_csv(
    path: str,
    rowclass: Type[T],
    dialect: Type[csv.unix_dialect] = csv.unix_dialect,
) -> List[T]:
    """load the csv file at the given path into named tuples of the given class"""
    result: List[T] = []
    converters = list(rowclass.__annotations__.values())
    fields = list(rowclass._fields)
    field_count = len(fields)

    with open(path, "rt", newline="", encoding="utf-8", errors="strict") as csvfh:
        csvfile = csv.reader(csvfh, dialect=dialect)
        for i, row in enumerate(csvfile):
            if i == 0:
                if row != fields:
                    logger.error(
                        (
                            "in %s: header row has unexpected columns; "
                            "have: %s; "
                            "want: %s; "
                            "skipping"
                        ),
                        path,
                        row,
                        fields,
                    )
                    return result
                continue
            if (row_fieldcount := len(row)) != field_count:
                logger.warning(
                    (
                        "in %s: row %s: unexpected column count; "
                        "have: %s; "
                        "want: %s; "
                        "skipping"
                    ),
                    path,
                    i,
                    row_fieldcount,
                    field_count,
                )
                continue
            if all((is_empty(field) for field in row)):
                logger.warning("in %s: row %s: completely empty row; skipping", path, i)
                continue
            result.append(rowclass(*(converters[i](val) for i, val in enumerate(row))))
    return result
