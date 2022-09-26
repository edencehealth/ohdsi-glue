#!/usr/bin/env python3
""" ohdsi_glue entrypoint """
# stdlib imports
import json
import traceback

# local imports
from util import loggingsetup, multiconfig, glue


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
        "Starting with config: %s",
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
    except Exception as uncaught_exception:  # noqa: E722
        logger.critical("Uncaught exception: %s", traceback.format_exc())
        raise uncaught_exception from None  # log exceptions then permit them to continue


if __name__ == "__main__":
    main()
