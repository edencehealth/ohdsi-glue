#!/usr/bin/env python3
"""primary functionality for gluing various ohdsi bits together"""

# pylint: disable=R0913
import logging
from typing import Any

from . import webapi
from .config import GlueConfig
from .operations import (
    init_cem_results_schema,
    init_concept_count,
    init_results_schema,
    init_sources,
    set_basic_security,
)

logger = logging.getLogger(__name__)


def glue_it(config: GlueConfig) -> Any:
    """
    connect to the database, create the results schema, tell webapi how to connect to
    the cdm source
    """
    if config.enable_basic_security:
        set_basic_security.run(config)

    api = webapi.WebAPIClient(config)

    if config.enable_result_init:
        init_results_schema.run(config, api)

    if config.enable_cem_results_init:
        init_cem_results_schema.run(config, api)

    if config.enable_concept_count_init:
        init_concept_count.run(config, api)

    if config.enable_source_setup:
        init_sources.run(config, api)

    logger.info("done")
