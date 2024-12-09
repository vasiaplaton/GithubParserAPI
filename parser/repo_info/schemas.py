"""
Module: schemas
This module defines the data models used in the application for repositories and commit activity.

Models:
1. `RepositoryModel`: Represents the metadata for a repository.
2. `CommitActivityModel`: Represents commit activity data for a repository on a specific date.
"""

from typing import List, Optional
from datetime import date
from pydantic import BaseModel

__all__ = ('RepositoryModel', 'CommitActivityModel')


class RepositoryModel(BaseModel):
    """
    Represents the metadata for a repository.

    Attributes:
        name (str): The name of the repository.
        owner (str): The owner of the repository.
        stars (int): The number of stars the repository has.
        forks (int): The number of forks for the repository.
        issues (int): The number of open issues in the repository.
        language (Optional[str]): The primary programming language of the repository, if available.
    """
    name: str
    owner: str
    stars: int
    forks: int
    issues: int
    watchers: int
    language: Optional[str] = None


class CommitActivityModel(BaseModel):
    """
    Represents commit activity data for a repository on a specific date.

    Attributes:
        date (date): The date of the commit activity.
        commits (int): The total number of commits made on the specified date.
        authors (List[str]): A list of authors who contributed commits on the specified date.
    """
    date: date
    commits: int
    authors: List[str]
