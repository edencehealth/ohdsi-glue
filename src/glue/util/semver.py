#!/usr/bin/env python3
"""utils for dealing with Semantic Versioning strings"""
import functools
import re
from typing import Any, Final, Tuple

# the following regex was tweaked one on from https://semver.org/
semver: Final = re.compile(
    r"^"
    r"(?:[vVrR])?"
    r"(?P<major>0|[1-9]\d*)\."
    r"(?P<minor>0|[1-9]\d*)\."
    r"(?P<patch>0|[1-9]\d*)"
    r"(?:-"
    r"(?P<prerelease>(?:0|[1-9]\d*|\d*[a-zA-Z-][0-9a-zA-Z-]*)"
    r"(?:\.(?:0|[1-9]\d*|\d*[a-zA-Z-][0-9a-zA-Z-]*))*"
    r"))?"
    r"(?:\+(?P<buildmetadata>[0-9a-zA-Z-]+(?:\.[0-9a-zA-Z-]+)*))?"
    r"$"
)


def split_float(f: float) -> Tuple[int, int]:
    """
    split the integer and fractional part of the given float and return them as
    integers for use in version comparison
    """
    int_part, frac_part = str(f).split(".", 1)
    return int(int_part), int(frac_part)


@functools.total_ordering
class SemVer:
    """class for parsing and comparing semantic versions"""

    major: int = 0
    minor: int = 0
    patch: int = 0
    prerelease: str = ""
    buildmetadata: str = ""
    _input: str = ""

    def __init__(self, semver_string: str) -> None:
        self._input = semver_string
        m = semver.match(semver_string)
        if not m:
            raise ValueError(
                f'the given string "{semver_string}" does not parse as a '
                "semantic version; note: major, minor, and patch values are "
                "required"
            )
        groupdict = m.groupdict()
        for attr in ("major", "minor", "patch", "prerelease", "buildmetadata"):
            if attr in groupdict and groupdict[attr] is not None:
                if attr in ("prerelease", "buildmeta"):
                    # strings
                    setattr(self, attr, groupdict[attr])
                    continue
                # integers
                setattr(self, attr, int(groupdict[attr]))

    def __hash__(self) -> int:
        """support for use in sets and dict keys"""
        # https://docs.python.org/3/reference/datamodel.html#object.__hash__
        return hash(
            (self.major, self.minor, self.patch, self.prerelease, self.buildmetadata)
        )

    def _is_valid_operand(self, other):
        """support for total_ordering"""
        # https://docs.python.org/3/library/functools.html#functools.total_ordering
        return isinstance(other, (self.__class__, float, int))

    def __eq__(self, other: Any) -> bool:
        """return true if self is equal to other"""
        if isinstance(other, self.__class__):
            # major/minor/patch comparison
            return all(
                (
                    self.major == other.major,
                    self.minor == other.minor,
                    self.patch == other.patch,
                )
            )
        if isinstance(other, str):
            return self == self.__class__(other)
        if isinstance(other, float):
            # major/minor comparison
            int_part, frac_part = split_float(other)
            return all(
                (
                    self.major == int_part,
                    self.minor == frac_part,
                )
            )
        if isinstance(other, int):
            # major comparison
            return self.major == other
        raise NotImplementedError(
            f"don't know how to compare "
            f"{self.__class__.__name__} to {other.__class__.__name__}"
        )

    def __lt__(self, other: Any) -> bool:
        """return true if self is less than other"""
        if isinstance(other, self.__class__):
            # major/minor/patch comparison
            for attr in ("major", "minor", "patch"):
                a = getattr(self, attr)
                b = getattr(other, attr)
                if a == b:
                    continue
                return a < b
        if isinstance(other, str):
            return self < self.__class__(other)
        if isinstance(other, float):
            # major/minor comparison
            int_part, frac_part = split_float(other)
            if self.major != int_part:
                return self.major < int_part
            if self.minor != frac_part:
                return self.minor < frac_part
            return False
        if isinstance(other, int):
            # major comparison
            return self.major < other
        raise NotImplementedError(
            f"don't know how to compare "
            f"{self.__class__.__name__} to {other.__class__.__name__}"
        )

    def __repr__(self) -> str:
        return f"{self.major}.{self.minor}.{self.patch}"
