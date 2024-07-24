""" sets up default a console logger and file logging for the app """

import logging

from baselog import BaseLog

from ..config import GlueConfig


def from_config(config: GlueConfig, prog: str) -> logging.Logger:
    """sets up logging for the app and returns the root logger"""
    base_pkg = __package__.partition(".")[0]

    logger = BaseLog(
        base_pkg,
        log_dir=config.log_dir,
        console_log_level=config.log_level,
        file_log_level=config.log_level,
    )
    config.logcfg(
        logger.root_logger.getChild("startup"),
        heading=f"Starting {prog} with config:",
        item_prefix="",
    )
    return logger
