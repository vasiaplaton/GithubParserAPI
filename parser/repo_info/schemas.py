from pydantic import BaseModel
from typing import List, Optional
from datetime import date

__all__ = ('RepositoryModel', 'CommitActivityModel')


class RepositoryModel(BaseModel):
    name: str
    owner: str
    stars: int
    forks: int
    issues: int
    language: Optional[str] = None


class CommitActivityModel(BaseModel):
    date: date
    commits: int
    authors: List[str]
