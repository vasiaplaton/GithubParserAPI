"""
Module: config
This module contains the configuration settings for the application, including
GitLab API and database connection settings. It uses Pydantic for easy
environment variable management and validation.
"""

from typing import Optional
from pydantic.v1 import BaseSettings


class Settings(BaseSettings):
    """
    Settings class for application configuration.

    Attributes:
        gitlab_base_url (Optional[str]): Base URL for the GitLab API. Defaults to "https://api.github.com".
        gitlab_token (Optional[str]): Personal Access Token for authenticating with the GitLab API.
        database_url (str): Database connection URL.
    """
    gitlab_base_url: Optional[str] = "https://api.github.com"
    gitlab_token: Optional[str] = None
    database_url: str


settings = Settings()
