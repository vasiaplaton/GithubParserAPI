from datetime import datetime
from typing import List, Any

import httpx

from parser.repository_info import RepositoryInfoGetter
from schemas import RepositoryModel, CommitActivityModel


class GitlabInfoGetter(RepositoryInfoGetter):
    def __init__(self, base_url: str):
        self.base_url = base_url

    async def get_top_repositories(self, limit: int = 100) -> List[RepositoryModel]:
        url = f"{self.base_url}/projects"
        params = {
            "order_by": "star_count",
            "sort": "desc",
            "per_page": limit,
        }
        async with httpx.AsyncClient() as client:
            response = await client.get(url, params=params)
            response.raise_for_status()  # Raise an error for HTTP 4xx/5xx
            data = response.json()
        return [
            RepositoryModel(
                name=p["path_with_namespace"],
                owner=p["namespace"]["full_path"],
                stars=p["star_count"],
                forks=p["forks_count"],
                issues=p["open_issues_count"],
                language=p.get("programming_language")
            )
            for p in data
        ]

    async def get_repository_activity(self, owner: str, repo: str, since: datetime, until: datetime) \
            -> List[CommitActivityModel]:
        project_id = f"{owner}%2F{repo}"
        url = f"{self.base_url}/projects/{project_id}/repository/commits"
        params = {
            "since": f"{since.isoformat()}Z",
            "until": f"{until.isoformat()}Z",
            "per_page": 100,
        }
        async with httpx.AsyncClient() as client:
            response = await client.get(url, params=params)
            response.raise_for_status()  # Raise an error for HTTP 4xx/5xx
            data = response.json()

        return self._map_commits(data)

    @staticmethod
    def _map_commits(data: dict[Any]) -> List[CommitActivityModel]:
        commits_map = {}
        for c in data:
            commit_date = c["committed_date"][:10]  # Extract YYYY-MM-DD
            author = c["author_name"]
            commits_map.setdefault(commit_date, set()).add(author)
        return [
            CommitActivityModel(
                date=datetime.strptime(date, "%Y-%m-%d").date(),
                commits=len(authors),
                authors=list(authors),
            )
            for date, authors in commits_map.items()
        ]
