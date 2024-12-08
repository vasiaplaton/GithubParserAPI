import abc
from datetime import datetime
from typing import List
from schemas import RepositoryModel, CommitActivityModel


class RepositoryInfoGetter(abc.ABC):
    @abc.abstractmethod
    async def get_top_repositories(self, limit: int = 100) -> List[RepositoryModel]:
        pass

    @abc.abstractmethod
    async def get_repository_activity(self, owner: str, repo: str, since: datetime, until: datetime) \
            -> List[CommitActivityModel]:
        pass
