"""Module with all needed FastAPI dependencies"""
import asyncpg

from parser.config import settings


async def get_pool() -> asyncpg.Pool:
    """
    Creates and returns a database connection pool.

    Uses the DATABASE_URL from settings for connection configuration.
    The function is cached to ensure a single pool is used across the application.

    Returns:
        asyncpg.Pool: A pool of database connections.
    """
    return await asyncpg.create_pool(
        dsn=settings.database_url,
        min_size=1,
        max_size=5,
        max_inactive_connection_lifetime=300,  # Close idle connections after 5 minutes
    )
