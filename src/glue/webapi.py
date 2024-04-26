#!/usr/bin/env/python3
""" interactions with OHDSI WebAPI, over its web API """
# pylint: disable=R0903
import logging
from typing import Any, Dict, Optional, Union

import requests

from .config import GlueConfig
from .semver import SemVer

logger = logging.getLogger(__name__)

# having access to the cleartext password is not good, but we need to be able
# to make requests to webapi (the web service) and that will require that we
# sign-in to get a short term bearer token.

# the user can deploy with glue then rotate the password to something else
# (scuttling glue's webapi methods but securing the server against cleartext
# password exfiltration)

# https://docs.python-requests.org/en/latest/user/authentication/#new-forms-of-authentication


class BearerAuth(requests.auth.AuthBase):
    """
    provides bearer authentication for requests, see python-requests.org link
    above
    """

    def __init__(self, token: str):
        self.token = token

    def __call__(self, r):
        r.headers["authorization"] = "Bearer " + self.token
        return r


class WebAPIClient:
    """class for communicating with webapi (as a web api)"""

    version: Optional[SemVer]
    info: Dict[str, Any]
    username: Optional[str]
    password: Optional[str]

    def __init__(
        self,
        config: GlueConfig,
        username: Optional[str] = None,
        password: Optional[str] = None,
    ):
        self.config = config
        self.auth = None

        if username:
            self.username = username
        elif config.atlas_username:
            self.username = config.atlas_username

        if password:
            self.password = password
        elif config.atlas_password:
            self.password = config.atlas_password

        if self.username and self.password:
            self.login()

    def login(self):
        """sign-in to webapi using the DB auth endpoint"""
        response = self.post(
            "user/login/db",
            data={
                "login": self.username,
                "password": self.password,
            },
        )
        response.raise_for_status()
        self.auth = BearerAuth(response.headers["Bearer"])
        self.info = self.get_info()
        self.version = SemVer(str(self.info["version"]))

    def path_url(self, path: str) -> str:
        """return the full url for the given webapi path"""
        scheme = "https" if self.config.webapi_tls else "http"
        webapi_base_path = self.config.webapi_base_path.strip("/")
        stripped_path = path.lstrip("/")
        webapi_addr = self.config.webapi_addr
        return f"{scheme}://{webapi_addr}/{webapi_base_path}/{stripped_path}"

    def post(self, path: str, *args, **kwargs):
        """make POST request to webapi"""
        url = self.path_url(path)
        logger.debug("webapi_post to %s", url)
        if self.auth:
            kwargs["auth"] = self.auth
        return requests.post(url, *args, timeout=60.0, **kwargs)

    def get(self, path: str, *args, **kwargs):
        """make a GET request to webapi"""
        url = self.path_url(path)
        logger.debug("webapi_get %s", url)
        if self.auth:
            kwargs["auth"] = self.auth
        return requests.get(url, *args, timeout=60.0, **kwargs)

    def source_refresh(self):
        """
        asks webapi to reload the available data sources from its source and
        source_daimon tables
        """
        logger.debug("sending source refresh request")
        self.get("/source/refresh").raise_for_status()

    def get_results_ddl(self):
        """
        get SQL code which can be used to establish the results schema
        """
        params = {
            "dialect": self.config.cdm_db_dialect,
            "schema": self.config.results_schema,
            "vocabSchema": self.config.vocab_schema,
            "tempSchema": self.config.temp_schema,
            "initConceptHierarchy": (
                "true" if self.config.init_concept_hierarchy else "false"
            ),
        }
        result = self.get("/ddl/results", params=params)
        result.raise_for_status()
        return result.text

    def get_achilles_ddl(self):
        """
        get SQL code which can be used to (as of WebAPI v2.13) create the
        concept count tables in the CDM DB

        From <https://github.com/OHDSI/WebAPI/wiki/CDM-Configuration>:
        > This DDL assumes you have run Achilles and it will use those tables
        to create the concept count table that is used to power the vocabulary
        search
        """
        params = {
            "dialect": self.config.cdm_db_dialect,
            "schema": self.config.results_schema,
            "vocabSchema": self.config.vocab_schema,
        }
        result = self.get("/ddl/achilles", params=params)
        result.raise_for_status()
        return result.text

    def get_cem_results_ddl(self):
        """
        Get DDL used to establish the Common Evidence Model results schema in
        the CDMDB
        """
        params = {
            "dialect": self.config.cdm_db_dialect,
            "schema": self.config.cem_results_schema,
            "vocabSchema": self.config.vocab_schema,
        }
        result = self.get("/ddl/cemresults", params=params)
        result.raise_for_status()
        return result.text

    def get_info(self) -> Dict[str, Union[str, int, float]]:
        """ask for webapi instance information"""
        return self.get("info").json()
