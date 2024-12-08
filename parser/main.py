"""
Main module for running the repository parser application.

This script updates the top 100 repositories and their activity information in the database.
"""

import asyncio
import datetime

import asyncpg

from parser.config import settings
from parser.repo_info import RepositoryInfoGetter, GitlabInfoGetter
from parser.updaters.activity_updater import ActivityUpdater
from parser.updaters.top100_updater import Top100Updater
from logs.project_log import main_logger


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
        github: RepositoryInfoGetter = GitlabInfoGetter(settings.gitlab_base_url, settings.gitlab_token)
        main_logger.info("GitHub repository fetcher initialized.")

        # Update top 100 repositories
        main_logger.info("Fetching top 100 repositories...")
        repositories = await github.get_top_repositories(limit=100)
        await Top100Updater(pool).update_top_100(repositories)
        main_logger.info("Top 100 repositories updated.")

        # Update activity for each repository
        activity_service = ActivityUpdater(pool)
        for repo in repositories:
            main_logger.debug("Processing repository: %s/%s", repo.owner, repo.name)
            since = await activity_service.get_last_activity_date(repo.name, repo.owner)
            if since is None:
                main_logger.info("No activity found for %s/%s. Fetching last 30 days.", repo.owner, repo.name)
                since = datetime.datetime.now() - datetime.timedelta(days=30)

            to = datetime.datetime.now()
            activity = await github.get_repository_activity(repo=repo.name, owner=repo.owner, since=since, until=to)
            await activity_service.update_activity(repo=repo.name, owner=repo.owner, activities=activity)
            main_logger.info("Updated activity for %s/%s from %s to %s.", repo.owner, repo.name, since, to)
            await asyncio.sleep(1)

    # I want to catch and log error, but I had nothing to do, so pylint: disable=broad-exception-caught
    except Exception:
        main_logger.error("An error occurred", exc_info=True)
    finally:
        await pool.close()
        main_logger.info("Database connection pool closed.")
        main_logger.info("Application finished.")


if __name__ == '__main__':
    asyncio.run(main())
