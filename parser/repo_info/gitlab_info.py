"""
Module: gitlab_info
This module implements a GitLab API client for fetching repository and activity data.
"""
import asyncio
from datetime import datetime
from typing import List, Dict, Optional
from urllib.parse import urlparse, parse_qs
import httpx

from logs.project_log import main_logger
from parser.repo_info.repository_info import RepositoryInfoGetter
from parser.repo_info.schemas import RepositoryModel, CommitActivityModel

__all__ = ('GitlabInfoGetter', )


class GitlabInfoGetter(RepositoryInfoGetter):
    """
    GitLab API client for fetching repository information and commit activity.

    Attributes:
        base_url (str): Base URL for the GitLab API.
        headers (dict): Headers used for authenticating requests.
    """

    def __init__(self, base_url: str, token: Optional[str] = None):
        """
        Initializes the GitLab API client.

        Args:
            base_url (str): Base URL for the GitLab API.
            token (Optional[str]): Authentication token for the API.
        """
        self.headers = {}
        if token:
            self.headers = {
                "Authorization": f"Bearer {token}",
                "X-GitHub-Api-Version": "2022-11-28"
            }
        self.base_url = base_url
        main_logger.debug("GitlabInfoGetter initialized with base_url=%s", self.base_url)

    async def get_top_repositories(self, limit: int = 100) -> List[RepositoryModel]:
        """
        Fetches the top repositories by star count.

        Args:
            limit (int): The maximum number of repositories to fetch. Defaults to 100.

        Returns:
            List[RepositoryModel]: A list of repository models representing the top repositories.
        """
        url = f"{self.base_url}/search/repositories"
        params = {
            "q": "stars:>0",
            "sort": "stars",
            "order": "desc",
            "per_page": limit,
        }
        main_logger.debug("Fetching top repositories from %s with params %s", url, params)

        async with httpx.AsyncClient() as client:
            response = await client.get(url, params=params, headers=self.headers)
            response.raise_for_status()  # Raise an error for HTTP 4xx/5xx
            data = response.json()

        main_logger.debug("Fetched %d repositories", len(data.get("items", [])))

        return [
            RepositoryModel(
                name=repo["name"],
                owner=repo["owner"]["login"],
                stars=repo["stargazers_count"],
                forks=repo["forks_count"],
                issues=repo["open_issues_count"],
                language=repo.get("language")
            )
            for repo in data.get("items", [])
        ]

    async def get_repository_activity(
            self, owner: str, repo: str, since: datetime, until: datetime
    ) -> List[Dict]:
        """
        Fetch commit activity for a repository from the GitHub API.

        Args:
            owner (str): The owner of the repository.
            repo (str): The repository name.
            since (datetime): Start date for fetching commits.
            until (datetime): End date for fetching commits.

        Returns:
            List[Dict]: List of activity records, grouped by date.
        """
        url = f"{self.base_url}/repos/{owner}/{repo}/commits"
        params = {
            "since": since.isoformat() + "Z",  # ISO format with UTC timezone
            "until": until.isoformat() + "Z",
            "per_page": 100,  # Max allowed
        }
        main_logger.debug("Fetching activity for %s/%s from %s to %s", owner, repo, since, until)

        all_commits = []
        now_page = 0
        amount_pages = -1
        async with httpx.AsyncClient() as client:
            while now_page <= amount_pages or amount_pages == -1:
                params["page"] = now_page
                main_logger.debug("Making request to %s with params %s", url, params)
                response = await client.get(url, params=params, headers=self.headers)
                response.raise_for_status()
                commits = response.json()
                all_commits.extend(commits)

                main_logger.debug("Fetched %d commits, total so far: %d", len(commits), len(all_commits))

                # Check for pagination
                if amount_pages == -1:
                    link_headers = response.headers.get("Link")
                    amount_pages = self._get_last_page_num(link_headers)
                    main_logger.debug("Found last page as %s", amount_pages)

                now_page += 1
                await asyncio.sleep(0.5)

        main_logger.debug("Parsing %d commits into CommitActivityModel", len(all_commits))
        return self._parse_activity(all_commits)

    @staticmethod
    def _get_last_page_num(link_header: str) -> int:
        """
        Parses the 'Link' header to extract the last page number.

        Args:
            link_header (str): The HTTP Link header containing pagination URLs.

        Returns:
            int: The last page number, or 1 if no 'rel="last"' link is found.
        """
        if not link_header:
            return 1  # Default to 1 if no Link header is present

        links = link_header.split(",")
        for link in links:
            if 'rel="last"' in link:
                # Extract the URL for 'rel="last"'
                url = link.split(";")[0].strip("<> ")
                # Parse the page parameter from the URL
                parsed_url = urlparse(url)
                query_params = parse_qs(parsed_url.query)
                return int(query_params.get("page", [1])[0])  # Default to 1 if 'page' is missing

        return 1  # Default to 1 if 'rel="last"' is not found

    @staticmethod
    def _parse_activity(raw_data: List[Dict]) -> List[CommitActivityModel]:
        """
        Convert raw JSON data from GitHub's commit API to CommitActivityModel.

        Args:
            raw_data (List[Dict]): List of raw commit data from the GitHub API.

        Returns:
            List[CommitActivityModel]: List of commit activity models grouped by date.
        """
        activity_map = {}

        for commit in raw_data:
            # Extract date and author
            commit_date = commit["commit"]["author"]["date"][:10]  # YYYY-MM-DD
            author = commit["commit"]["author"]["name"]

            # Initialize or update the activity map
            if commit_date not in activity_map:
                activity_map[commit_date] = {"commits": 0, "authors": set()}
            activity_map[commit_date]["commits"] += 1
            activity_map[commit_date]["authors"].add(author)

        # Convert activity_map to a list of CommitActivityModel
        return [
            CommitActivityModel(
                date=datetime.strptime(date, "%Y-%m-%d").date(),
                commits=details["commits"],
                authors=list(details["authors"]),
            )
            for date, details in activity_map.items()
        ]
