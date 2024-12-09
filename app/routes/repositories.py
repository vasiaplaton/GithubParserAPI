"""Module with repos router"""
import traceback
from datetime import datetime

from asyncpg import Pool
from fastapi import APIRouter, Query, HTTPException, Depends
from typing import Optional

from app.dependencies import get_pool
from logs.project_log import main_logger
from services.schemas import RepositorySchema, ActivitySchema
from services.services.activity_service import ActivityService
from services.services.repository_service import RepositoryService

router = APIRouter(prefix="/repos")


@router.get("/top100", response_model=list[RepositorySchema])
async def get_top_repositories(
        sort_by: Optional[str] = Query("stars", enum=["stars", "forks", "open_issues", "watchers"]),
        pool: Pool = Depends(get_pool),
):
    """
    Fetch the top 100 repositories, sorted by the specified field.

    Args:
        sort_by (str): Field to sort the repositories by. Default is 'stars'.
        pool (Pool): Dependency-injected service for pool.

    Returns:
        List[RepositoryModel]: List of top repositories.
    """
    try:
        main_logger.info("Fetching top repositories sorted by %s.", sort_by)
        async with pool.acquire() as conn:
            return await RepositoryService(conn).get_top_repositories(sort_by)
    except Exception as e:
        main_logger.error("Error fetching repositories: %s", traceback.format_exc())
        raise HTTPException(status_code=500, detail="Internal server error") from e


@router.get("/{owner}/{repo}/activity", response_model=list[ActivitySchema])
async def get_repository_activity(
        owner: str,
        repo: str,
        since: Optional[datetime] = Query(None, description="Start date for activity (inclusive)."),
        until: Optional[datetime] = Query(None, description="End date for activity (inclusive)."),
        pool: Pool = Depends(get_pool),
):
    """
    Fetch activity data for a specific repository within a specified time range.

    Args:
        owner (str): Repository owner.
        repo (str): Repository name.
        since (Optional[datetime]): Start date for activity. Default is None.
        until (Optional[datetime]): End date for activity. Default is None.
        pool (Pool): Dependency-injected connection pool.

    Returns:
        List[CommitActivitySchema]: List of commit activity records.
    """
    try:
        main_logger.info("Fetching activity for %s/%s from %s to %s.", owner, repo, since, until)
        async with pool.acquire() as conn:
            return await ActivityService(conn).get_activity(repo, owner, since, until)
    except Exception as e:
        main_logger.error("Error fetching activity for %s/%s: %s", owner, repo, traceback.format_exc())
        raise HTTPException(status_code=500, detail="Internal server error") from e
