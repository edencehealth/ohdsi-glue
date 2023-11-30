#!/usr/bin/env python3
""" ohdsi_glue entrypoint """
import os
from typing import Final

from .config import GlueConfig
from .process import glue_it
from .util import loggingsetup
from .webapi_db import derived_source_key

PROG_TAG: Final = os.environ.get("GIT_TAG", "dev")
PROG_COMMIT: Final = os.environ.get("GIT_COMMIT", "N/A")
PROG: Final = f"{__package__}"
VERSION: Final = f"{PROG_TAG} (commit {PROG_COMMIT})"


def main() -> None:
    """
    load configuration, setup logging, setup the database, start the load
    """
    # load config and process command-line args
    config = GlueConfig(
        prog=PROG,
        prog_description="Utility for working with OHDSI WebAPI and related apps",
        version=VERSION,
    )
    # some final configuration stuff
    if config.source_key is None:
        config.source_key = derived_source_key(config)

    # setup logging
    loggingsetup.from_config(config, f"{PROG} {VERSION}")

    # do the things
    glue_it(config)


if __name__ == "__main__":
    main()
