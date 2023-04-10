#!/usr/bin/env python3
""" ohdsi_glue entrypoint """
# stdlib imports
import os
import sys
import traceback
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
    logger = loggingsetup.from_config(config, PROG)

    try:
        glue.glue_it(config)
    except KeyboardInterrupt:
        print("\n")
        logger.warning("KeyboardInterrupt detected, exiting.")

    except Exception as uncaught_exception:  # pylint: disable=W0718
        logger.fatal("UNCAUGHT EXCEPTION: %s", str(uncaught_exception).strip())
        logger.fatal("TRACEBACK: %s", traceback.format_exc())
        sys.exit(1)


if __name__ == "__main__":
    main()
