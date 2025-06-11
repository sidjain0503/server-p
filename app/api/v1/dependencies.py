"""
Common API dependencies for v1 endpoints

This module contains reusable dependencies for API endpoints like
pagination, authentication, database sessions, etc.
"""

from typing import Optional, Annotated
from fastapi import Depends, Query, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_db_session
from app.meta_engine.orchestrator import get_meta_engine
from pydantic import BaseModel, Field


class PaginationParams(BaseModel):
    """Standard pagination parameters"""
    skip: int = Field(0, ge=0, description="Number of records to skip")
    limit: int = Field(10, ge=1, le=100, description="Maximum number of records to return")


class SearchParams(BaseModel):
    """Standard search parameters"""
    search: Optional[str] = Field(None, description="Search term")
    sort_by: Optional[str] = Field(None, description="Field to sort by")
    sort_order: Optional[str] = Field("asc", pattern="^(asc|desc)$", description="Sort order")


def get_pagination_params(
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(10, ge=1, le=100, description="Maximum number of records to return")
) -> PaginationParams:
    """Get pagination parameters from query string"""
    return PaginationParams(skip=skip, limit=limit)


def get_search_params(
    search: Optional[str] = Query(None, description="Search term"),
    sort_by: Optional[str] = Query(None, description="Field to sort by"),
    sort_order: str = Query("asc", pattern="^(asc|desc)$", description="Sort order")
) -> SearchParams:
    """Get search parameters from query string"""
    return SearchParams(search=search, sort_by=sort_by, sort_order=sort_order)


async def get_db() -> AsyncSession:
    """Get database session dependency"""
    async for session in get_db_session():
        yield session


def get_crud_service(schema_name: str):
    """Get CRUD service for a specific schema"""
    def _get_crud_service():
        meta_engine = get_meta_engine()
        crud_service = meta_engine.get_crud_service(schema_name)
        if not crud_service:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Schema '{schema_name}' not found"
            )
        return crud_service
    return _get_crud_service


# Type aliases for common dependencies
DatabaseSession = Annotated[AsyncSession, Depends(get_db)]
PaginationDep = Annotated[PaginationParams, Depends(get_pagination_params)]
SearchDep = Annotated[SearchParams, Depends(get_search_params)] 