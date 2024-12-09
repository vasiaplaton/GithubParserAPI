from datetime import datetime
from typing import List, Optional, Any
from asyncpg import Connection

from services.schemas import ActivitySchema


class ActivityService:
    """
    Service for managing repository activity records in the database, including:
    - Fetching activity data for a repository.
    - Inserting or updating activity data.
    - Retrieving the last activity date for a repository.
    """

    def __init__(self, conn: Connection):
        """
        Initialize the ActivityService with a database connection or transaction.

        Args:
            conn (Connection): An asyncpg connection or transaction object.
        """
        self.conn = conn

    @staticmethod
    def build_conditions(conditions: list[tuple[str, str, Any]]):
        q = ""
        if conditions:
            q += "WHERE "
            q += " AND ".join([f"{data[0]} {data[1]} ${i+1}" for i, data in enumerate(conditions)])

        return q

    async def get_activity(
            self, repo: str, owner: str, since: Optional[datetime] = None, until: Optional[datetime] = None
    ) -> List[ActivitySchema]:
        """
        Fetch activity data for a repository within a specified time range.

        Args:
            repo (str): Repository name.
            owner (str): Repository owner.
            since (Optional[datetime]): Start date for fetching activity. If None, fetch all.
            until (Optional[datetime]): End date for fetching activity. If None, fetch all.

        Returns:
            List[ActivitySchema]: A list of commit activity records.
        """
        conditions = [("repo", "=", repo), ("owner", "=", owner)]
        if since:
            conditions.append(("date", ">=", since.date()))
        if until:
            conditions.append(("date", "<=", until.date()))

        query = """
        SELECT date, commits, authors
        FROM activity 
        """
        query += self.build_conditions(conditions)
        query += " ORDER BY date ASC;"
        print(query)
        values = [r for _, _, r in conditions]
        rows = await self.conn.fetch(query, *values)
        return [ActivitySchema(**dict(row)) for row in rows]

    async def insert_or_update_activity(
        self, activities: List[ActivitySchema], repo: str, owner: str
    ):
        """
        Insert or update activity data for a repository.

        Args:
            activities (List[CommitActivitySchema]): List of activity data to insert or update.
            repo (str): Repository name.
            owner (str): Repository owner.
        """
        query = """
        INSERT INTO activity (date, repo, owner, commits, authors)
        VALUES ($1, $2, $3, $4, $5)
        ON CONFLICT (date, repo, owner) DO UPDATE
        SET commits = EXCLUDED.commits,
            authors = EXCLUDED.authors;
        """
        await self.conn.executemany(
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

    async def get_last_activity_date(self, repo: str, owner: str) -> datetime:
        """
        Fetch the most recent activity date for a repository.

        Args:
            repo (str): Repository name.
            owner (str): Repository owner.

        Returns:
            datetime: The most recent activity date, or None if no records exist.
        """
        query = """
        SELECT MAX(date)
        FROM activity
        WHERE repo = $1 AND owner = $2;
        """
        result = await self.conn.fetchval(query, repo, owner)
        return result
