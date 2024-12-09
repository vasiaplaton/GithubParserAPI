"""
Main module for running the repository parser application.

This script updates the top 100 repositories and their activity information in the database.
"""

import asyncio
import datetime

import asyncpg

from parser.config import settings
from parser.repo_info import RepositoryInfoGetter, GitlabInfoGetter
from logs.project_log import main_logger
from services.schemas import RepositorySchema, ActivitySchema
from services.services.activity_service import ActivityService
from services.services.repository_service import RepositoryService


async def initialize_github_client() -> RepositoryInfoGetter:
    """
    Initializes the GitHub repository fetcher.

    Returns:
        RepositoryInfoGetter: The initialized GitHub client.
    """
    main_logger.info("Initializing GitHub repository fetcher...")
    return GitlabInfoGetter(settings.github_base_url, settings.github_token)


async def update_top_repositories(pool: asyncpg.Pool, github: RepositoryInfoGetter):
    """
    Updates the top 100 repositories in the database.

    Args:
        pool (asyncpg.Pool): Database connection pool.
        github (RepositoryInfoGetter): The GitHub repository fetcher.
    """
    main_logger.info("Fetching top 100 repositories...")
    repositories = await github.get_top_repositories(limit=100)

    repositories_db = [
        RepositorySchema(
            repo=repo.name,
            owner=repo.owner,
            position_cur=0,
            position_prev=0,
            stars=repo.stars,
            watchers=repo.watchers,
            forks=repo.forks,
            open_issues=repo.issues,
            language=repo.language,
        )
        for repo in repositories
    ]

    async with pool.acquire() as conn:
        async with conn.transaction():
            await RepositoryService(conn).update_top_repositories(repositories_db)

    main_logger.info("Top 100 repositories updated.")


async def update_repository_activity(pool: asyncpg.Pool, github: RepositoryInfoGetter, repositories: list):
    """
    Updates activity information for each repository in the database.

    Args:
        pool (asyncpg.Pool): Database connection pool.
        github (RepositoryInfoGetter): The GitHub repository fetcher.
        repositories (list): List of repository objects.
    """
    for repo in repositories:
        async with pool.acquire() as conn:
            async with conn.transaction():
                main_logger.debug("Processing repository: %s/%s", repo.owner, repo.name)

                # Fetch last activity date
                since = await ActivityService(conn).get_last_activity_date(repo.name, repo.owner)
                if since is None:
                    main_logger.info("No activity found for %s/%s. Fetching last 30 days.", repo.owner, repo.name)
                    since = datetime.datetime.now() - datetime.timedelta(days=30)

                # Fetch activity from GitHub
                to = datetime.datetime.now()
                activity = await github.get_repository_activity(repo=repo.name, owner=repo.owner, since=since, until=to)

                activity_db = [
                    ActivitySchema(date=act.date, commits=act.commits, authors=act.authors)
                    for act in activity
                ]

                # Insert or update activity in the database
                await ActivityService(conn).insert_or_update_activity(
                    repo=repo.name, owner=repo.owner, activities=activity_db
                )

                main_logger.info("Updated activity for %s/%s from %s to %s.", repo.owner, repo.name, since, to)

                # Throttle requests to avoid hitting API limits
                await asyncio.sleep(1)


async def main():
    """
    Main entry point for the repository parser application.
    Establishes a database connection pool, updates the top 100 repositories,
    and updates activity information for each repository.
    """
    main_logger.info("Starting the application...")
    pool = await asyncpg.create_pool(settings.database_url, min_size=1, max_size=5)
    main_logger.info("Database connection pool established.")

    try:
        github = await initialize_github_client()

        # Update top repositories
        await update_top_repositories(pool, github)

        # Fetch repositories again to ensure activity updates match current data
        repositories = await github.get_top_repositories(limit=100)

        # Update repository activity
        await update_repository_activity(pool, github, repositories)

    except Exception:
        main_logger.error("An error occurred", exc_info=True)
    finally:
        await pool.close()
        main_logger.info("Database connection pool closed.")
        main_logger.info("Application finished.")


if __name__ == '__main__':
    asyncio.run(main())
