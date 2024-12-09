"""
Module: config
This module contains the configuration settings for the application, including
GitLab API and database connection settings. It uses Pydantic for easy
environment variable management and validation.
"""

from typing import Optional
from pydantic.v1 import BaseSettings

from settings.settings import Settings


class ParserSettings(Settings):
    """
    Settings class for application configuration.

    Attributes:
        github_base_url (Optional[str]): Base URL for the GitHub API. Defaults to "https://api.github.com".
        github_token (Optional[str]): Personal Access Token for authenticating with the GitHub API.
    """
    github_base_url: Optional[str] = "https://api.github.com"
    github_token: Optional[str] = None


settings = ParserSettings()
