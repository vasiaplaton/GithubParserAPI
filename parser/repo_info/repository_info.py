"""
Module: repository_info
This module defines the abstract base class for fetching repository information and activity data.
It specifies the interface that any concrete implementation must follow.
"""

import abc
from datetime import datetime
from typing import List
from parser.repo_info.schemas import RepositoryModel, CommitActivityModel

__all__ = ('RepositoryInfoGetter', )


class RepositoryInfoGetter(abc.ABC):
    """
    Abstract base class for repository information fetchers.

    Defines the interface for fetching repository details and activity data.
    Concrete implementations must provide the methods defined here.
    """

    @abc.abstractmethod
    async def get_top_repositories(self, limit: int = 100) -> List[RepositoryModel]:
        """
        Fetches the top repositories by star count.

        Args:
            limit (int): The maximum number of repositories to fetch. Defaults to 100.

        Returns:
            List[RepositoryModel]: A list of repository models representing the top repositories.
        """

    @abc.abstractmethod
    async def get_repository_activity(self, owner: str, repo: str, since: datetime, until: datetime) \
            -> List[CommitActivityModel]:
        """
        Fetches activity (commits and authors) for a specific repository within a given time range.

        Args:
            owner (str): The owner of the repository.
            repo (str): The name of the repository.
            since (datetime): The start date for fetching activity.
            until (datetime): The end date for fetching activity.

        Returns:
            List[CommitActivityModel]: A list of commit activity models containing the activity data.
        """
