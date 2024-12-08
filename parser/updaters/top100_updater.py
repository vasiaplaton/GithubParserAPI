"""
Module: top100_updater
This module defines the `Top100Updater` class, which handles the update of the top 100 repositories in the database.

The updater ensures the database reflects the latest information about the top repositories, including:
1. Inserting or updating repository records with their details.
2. Recalculating repository rankings based on the number of stars.
"""
from typing import List
from asyncpg import Pool, Connection

from parser.repo_info.schemas import RepositoryModel


class Top100Updater:
    """
    Handles the update of the top 100 repositories in the database.
    """

    def __init__(self, pool: Pool):
        self.pool = pool

    @staticmethod
    async def _insert_or_update_records(conn: Connection, repositories: List[RepositoryModel]):
        """
        Insert or update records directly in the `top100` table.
        """
        query = """
        INSERT INTO top100 (repo, owner, position_cur, position_prev, stars, watchers, forks, open_issues, language)
        VALUES ($1, $2, $3, $4, $5, 0, $6, $7, $8)
        ON CONFLICT (repo, owner) DO UPDATE
        SET stars = EXCLUDED.stars,
            forks = EXCLUDED.forks,
            open_issues = EXCLUDED.open_issues,
            language = EXCLUDED.language;
        """
        await conn.executemany(
            query,
            [
                (
                    repo.name,
                    repo.owner,
                    0,  # Temporary placeholder for position_cur
                    0,  # Temporary placeholder for position_prev
                    repo.stars,
                    repo.forks,
                    repo.issues,
                    repo.language,
                )
                for repo in repositories
            ],
        )

    @staticmethod
    async def _recalculate_positions(conn: Connection):
        """
        Recalculate `position_cur` and `position_prev` for the top 100 repositories.
        """
        # Use a CTE to calculate positions based on stars
        query = """
        WITH ranked_repos AS (
            SELECT repo, owner, stars,
                   ROW_NUMBER() OVER (ORDER BY stars DESC) AS new_position
            FROM top100
        )
        UPDATE top100
        SET position_prev = COALESCE(position_cur, 0),
            position_cur = ranked_repos.new_position
        FROM ranked_repos
        WHERE top100.repo = ranked_repos.repo
          AND top100.owner = ranked_repos.owner;
        """
        await conn.execute(query)

    async def update_top_100(self, repositories: List[RepositoryModel]):
        """
        Updates the top 100 repositories in the database:
        1. Insert or update all records in `top100`.
        2. Recalculate `position_cur` and `position_prev` based on stars.
        """
        async with self.pool.acquire() as conn:
            async with conn.transaction():
                # Insert or update all records
                await self._insert_or_update_records(conn, repositories)
                # Recalculate positions
                await self._recalculate_positions(conn)
