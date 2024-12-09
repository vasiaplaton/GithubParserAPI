"""
Module: config
This module contains the configuration settings for the application, including
database connection settings. It uses Pydantic for easy
environment variable management and validation.
"""
from settings.settings import Settings

settings = Settings()
