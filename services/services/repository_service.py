from typing import List

from asyncpg import Connection

from services.schemas import RepositorySchema


class RepositoryService:
    """
    Service for interacting with repository data in the database, including:
    - Fetching top repositories.
    - Updating top repositories.
    - Recalculating repository rankings.
    """

    def __init__(self, conn: Connection):
        """
        Initialize the RepositoryService with a connection or transaction.

        Args:
            conn (Connection): An asyncpg connection or transaction object.
        """
        self.conn = conn

    async def get_top_repositories(self, sort_by: str) -> List[RepositorySchema]:
        """
        Fetch the top 100 repositories sorted by a specified field.

        Args:
            sort_by (str): Field to sort the repositories by.

        Returns:
            List[RepositorySchema]: List of repository models.
        """
        query = f"""
        SELECT repo, owner, position_cur, position_prev, stars, watchers, forks, open_issues, language
        FROM top100
        ORDER BY {sort_by} DESC
        LIMIT 100;
        """
        rows = await self.conn.fetch(query)
        return [RepositorySchema(**dict(row)) for row in rows]

    async def insert_or_update_records(self, repositories: List[RepositorySchema]):
        """
        Insert or update records directly in the `top100` table.

        Args:
            repositories (List[RepositorySchema]): List of repository models to insert or update.
        """
        query = """
        INSERT INTO top100 (repo, owner, position_cur, position_prev, stars, watchers, forks, open_issues, language)
        VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9)
        ON CONFLICT (repo, owner) DO UPDATE
        SET stars = EXCLUDED.stars,
            forks = EXCLUDED.forks,
            open_issues = EXCLUDED.open_issues,
            watchers = EXCLUDED.watchers,
            language = EXCLUDED.language;
        """
        await self.conn.executemany(
            query,
            [
                (
                    repo.repo,
                    repo.owner,
                    repo.position_cur,
                    repo.position_prev,
                    repo.stars,
                    repo.watchers,
                    repo.forks,
                    repo.open_issues,
                    repo.language,
                )
                for repo in repositories
            ],
        )

    async def recalculate_positions(self):
        """
        Recalculate `position_cur` and `position_prev` for the top 100 repositories.
        """
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
        await self.conn.execute(query)

    async def update_top_repositories(self, repositories: List[RepositorySchema]):
        """
        Updates the top 100 repositories in the database:
        1. Insert or update all records in `top100`.
        2. Recalculate `position_cur` and `position_prev` based on stars.

        Args:
            repositories (List[RepositorySchema]): List of repository models to update.
        """
        await self.insert_or_update_records(repositories)
        await self.recalculate_positions()
