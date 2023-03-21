#!/usr/bin/env python3
""" ohdsi_glue entrypoint """
# stdlib imports
import json
import os
import sys
import traceback
from typing import Final

# local imports
from .util import glue, loggingsetup, multiconfig

PROG_TAG: Final = os.environ.get("GIT_TAG", "dev")
PROG_COMMIT: Final = os.environ.get("GIT_COMMIT", "N/A")
PROG: Final = f"{__package__} {PROG_TAG} (commit {PROG_COMMIT})"


def main() -> None:
    """
    load configuration, setup logging, setup the database, start the load
    """
    # load config and process command-line args
    config = multiconfig.MultiConfig()
    if config.source_key is None:
        config.source_key = glue.derived_source_key(config)

    # setup logging
    logger = loggingsetup.from_config(config)

    # write the current configuration to the logs (but redact the passwords)
    logger.info(
        "Starting %s with config: %s",
        PROG,
        json.dumps(
            {
                k: (v if "password" not in k else "--PASSWORD REDACTED--")
                for k, v in config.asdict().items()
            },
            indent=2,
        ),
    )

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
