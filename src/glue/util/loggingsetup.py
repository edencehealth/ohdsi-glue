""" sets up default a console logger and file logging for the app """
import datetime
import json
import logging
import os

from .multiconfig import MultiConfig


def from_config(config: MultiConfig) -> logging.Logger:
    """sets up logging for the app and returns the root logger"""
    log_format = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )

    logger = logging.getLogger()
    logger.setLevel(config.log_level)

    # always log to the console in a container context
    console_handler = logging.StreamHandler()
    console_handler.setLevel(config.log_level)
    console_handler.setFormatter(log_format)
    logger.addHandler(console_handler)

    # if config.log_dir is set, we create a run-specific log file in it
    # by default this is set to "logs"
    if config.log_dir:
        # make the log_dir if it doesn't exist
        if not os.path.isdir(config.log_dir):
            os.makedirs(config.log_dir)

        # pylint: disable=C0209
        filename = "glue_{}.log".format(
            datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        )
        file_handler = logging.FileHandler(os.path.join(config.log_dir, filename))
        file_handler.setLevel(logging.DEBUG)  # Set the file logger to maximum verbosity
        file_handler.setFormatter(log_format)
        logger.addHandler(file_handler)

    # write the given muticonfig to the logs (redacting the passwords)
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

    # return the root logger
    logger.name = __package__.split(".", maxsplit=1)[0]
    return logger
