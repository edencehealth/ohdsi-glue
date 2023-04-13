#!/usr/bin/env python3
""" ohdsi_glue entrypoint """
# stdlib imports
import os
from typing import Final

# local imports
from .util import glue, loggingsetup
from .util.glueconfig import GlueConfig

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
    if config.source_key is None:
        config.source_key = glue.derived_source_key(config)

    # setup logging
    loggingsetup.from_config(config, f"{PROG} {VERSION}")

    # do the thing
    glue.glue_it(config)


if __name__ == "__main__":
    main()
