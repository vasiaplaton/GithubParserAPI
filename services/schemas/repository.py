from pydantic import BaseModel
from typing import Optional

__all__ = ('RepositorySchema',)


class RepositorySchema(BaseModel):
    """
    Represents a repository in the top 100 list.
    """
    repo: str
    owner: str
    position_cur: int
    position_prev: int
    stars: int
    watchers: int
    forks: int
    open_issues: int
    language: Optional[str] = None
