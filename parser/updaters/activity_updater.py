"""
Module: activity_updater
This module defines the `ActivityUpdater` class, which manages the insertion, updating, and
retrieval of repository activity records in the database.

The updater provides functionality to:
1. Insert or update commit activity for a specific repository.
2. Retrieve the last recorded activity date for a repository to minimize redundant API calls.
"""

from datetime import datetime
from typing import List

from asyncpg import Pool, Connection

from parser.repo_info.schemas import CommitActivityModel


class ActivityUpdater:
    """
    Handles updating repository activity records in the database.
    """

    def __init__(self, pool: Pool):
        self.pool = pool

    async def _insert_or_update_activity(self, conn: Connection, activities: List[CommitActivityModel], repo, owner):
        """
        Insert or update activity records in the database.

        Args:
            conn (Connection): Database connection.
            activities (List[CommitActivityModel]): List of activity records to insert or update.
        """
        query = """
        INSERT INTO activity (date, repo, owner, commits, authors)
        VALUES ($1, $2, $3, $4, $5)
        ON CONFLICT (date, repo, owner) DO UPDATE
        SET commits = EXCLUDED.commits,
            authors = EXCLUDED.authors;
        """
        await conn.executemany(
            query,
            [
                (
                    activity.date,
                    repo,
                    owner,
                    activity.commits,
                    activity.authors,
                )
                for activity in activities
            ],
        )

    async def update_activity(self, repo: str, owner: str, activities: List[CommitActivityModel]):
        """
        Updates activity records for a specific repository.

        Args:
            repo (str): Repository name.
            owner (str): Repository owner.
            activities (List[CommitActivityModel]): List of activity records.
        """
        async with self.pool.acquire() as conn:
            async with conn.transaction():
                await self._insert_or_update_activity(conn, activities, repo, owner)

    async def get_last_activity_date(self, repo: str, owner: str) -> datetime:
        """
        Get the most recent activity date for a repository.

        Args:
            conn (Connection): Database connection.
            repo (str): Repository name.
            owner (str): Repository owner.

        Returns:
            datetime: The most recent activity date, or None if no records exist.
        """
        async with self.pool.acquire() as conn:
            async with conn.transaction():
                query = """
                SELECT MAX(date)
                FROM activity
                WHERE repo = $1 AND owner = $2;
                """
                result = await conn.fetchval(query, repo, owner)
                return result
