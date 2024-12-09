from datetime import date

from pydantic import BaseModel

__all__ = ('ActivitySchema', )


class ActivitySchema(BaseModel):
    date: date
    commits: int
    authors: list[str]
