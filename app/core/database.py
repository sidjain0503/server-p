"""
Database Layer - Async PostgreSQL Connection Management

This module provides:
- Async database connection with connection pooling
- Session management with proper cleanup
- Database health checks
- Transaction management
- Connection utilities
"""

import logging
from contextlib import asynccontextmanager
from typing import AsyncGenerator, Optional

from sqlalchemy import text, MetaData, event
from sqlalchemy.ext.asyncio import (
    AsyncSession,
    AsyncEngine,
    create_async_engine,
    async_sessionmaker,
)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.pool import QueuePool
from sqlalchemy.exc import SQLAlchemyError

from app.core.config import settings

# Configure logging
logger = logging.getLogger(__name__)

# =============================================================================
# Database Base Model
# =============================================================================
# Create the base class for all our models
Base = declarative_base()

# Metadata object for schema introspection
metadata = MetaData()


# =============================================================================
# Database Engine and Session Management
# =============================================================================
class DatabaseManager:
    """
    Manages database connections, sessions, and lifecycle.
    This is a singleton that handles all database operations.
    """
    
    def __init__(self):
        self._engine: Optional[AsyncEngine] = None
        self._session_factory: Optional[async_sessionmaker] = None
        self._is_connected: bool = False
    
    def create_engine(self) -> AsyncEngine:
        """
        Create and configure the async database engine.
        """
        if self._engine is not None:
            return self._engine
        
        # Get database configuration
        db_config = settings.get_database_config()
        
        # Create the async engine with connection pooling
        self._engine = create_async_engine(
            db_config["url"],
            echo=db_config["echo"],  # SQL logging
            pool_size=db_config["pool_size"],
            max_overflow=db_config["max_overflow"],
            pool_timeout=db_config["pool_timeout"],
            pool_pre_ping=True,  # Validate connections before use
            poolclass=QueuePool,
            # Additional async-specific settings
            future=True,  # Use SQLAlchemy 2.0 style
        )
        
        # Add event listeners for connection lifecycle
        self._setup_engine_events()
        
        logger.info(f"Created database engine with pool_size={db_config['pool_size']}")
        return self._engine
    
    def _setup_engine_events(self):
        """Setup event listeners for database connection monitoring."""
        
        @event.listens_for(self._engine.sync_engine, "connect")
        def on_connect(dbapi_connection, connection_record):
            """Called when a new database connection is created."""
            logger.debug("New database connection established")
        
        @event.listens_for(self._engine.sync_engine, "close")
        def on_close(dbapi_connection, connection_record):
            """Called when a database connection is closed."""
            logger.debug("Database connection closed")
        
        @event.listens_for(self._engine.sync_engine, "invalidate")
        def on_invalidate(dbapi_connection, connection_record, exception):
            """Called when a connection is invalidated."""
            logger.warning(f"Database connection invalidated: {exception}")
    
    def create_session_factory(self) -> async_sessionmaker:
        """
        Create the session factory for database sessions.
        """
        if self._session_factory is not None:
            return self._session_factory
        
        # Ensure engine exists
        if self._engine is None:
            self.create_engine()
        
        # Create session factory
        self._session_factory = async_sessionmaker(
            bind=self._engine,
            class_=AsyncSession,
            expire_on_commit=False,  # Keep objects accessible after commit
            autoflush=True,  # Auto-flush before queries
            autocommit=False,  # Manual transaction control
        )
        
        logger.info("Created database session factory")
        return self._session_factory
    
    async def connect(self) -> None:
        """
        Initialize database connection and verify connectivity.
        """
        try:
            # Create engine and session factory
            self.create_engine()
            self.create_session_factory()
            
            # Test the connection
            await self.health_check()
            
            self._is_connected = True
            logger.info("Successfully connected to database")
            
        except Exception as e:
            logger.error(f"Failed to connect to database: {e}")
            raise
    
    async def disconnect(self) -> None:
        """
        Close database connections and cleanup resources.
        """
        try:
            if self._engine:
                await self._engine.dispose()
                logger.info("Database engine disposed")
            
            self._engine = None
            self._session_factory = None
            self._is_connected = False
            
        except Exception as e:
            logger.error(f"Error during database disconnect: {e}")
            raise
    
    async def health_check(self) -> bool:
        """
        Check database connectivity and health.
        
        Returns:
            bool: True if database is healthy, False otherwise
        """
        try:
            if not self._engine:
                return False
            
            # Test connection with a simple query
            async with self._engine.begin() as conn:
                result = await conn.execute(text("SELECT 1"))
                result.fetchone()
            
            return True
            
        except Exception as e:
            logger.error(f"Database health check failed: {e}")
            return False
    
    @property
    def is_connected(self) -> bool:
        """Check if database is connected."""
        return self._is_connected
    
    @property
    def engine(self) -> AsyncEngine:
        """Get the database engine."""
        if self._engine is None:
            raise RuntimeError("Database engine not initialized. Call connect() first.")
        return self._engine
    
    @property
    def session_factory(self) -> async_sessionmaker:
        """Get the session factory."""
        if self._session_factory is None:
            raise RuntimeError("Database session factory not initialized. Call connect() first.")
        return self._session_factory


# =============================================================================
# Global Database Manager Instance
# =============================================================================
db_manager = DatabaseManager()


# =============================================================================
# Session Dependencies and Context Managers
# =============================================================================
async def get_db_session() -> AsyncGenerator[AsyncSession, None]:
    """
    FastAPI dependency to get a database session.
    
    This ensures proper session lifecycle management:
    - Creates a new session for each request
    - Automatically commits on success
    - Rolls back on errors
    - Always closes the session
    """
    session = db_manager.session_factory()
    try:
        yield session
        await session.commit()
    except SQLAlchemyError as e:
        await session.rollback()
        logger.error(f"Database session error: {e}")
        raise
    except Exception as e:
        await session.rollback()
        logger.error(f"Unexpected error in database session: {e}", exc_info=True)
        raise
    finally:
        await session.close()


@asynccontextmanager
async def get_db_transaction() -> AsyncGenerator[AsyncSession, None]:
    """
    Context manager for database transactions.
    
    Usage:
        async with get_db_transaction() as session:
            # Your database operations here
            user = User(name="John")
            session.add(user)
            # Transaction is automatically committed or rolled back
    """
    session = db_manager.session_factory()
    try:
        async with session.begin():
            yield session
    except Exception:
        # Rollback is handled by session.begin() context manager
        raise
    finally:
        await session.close()


# =============================================================================
# Database Utilities
# =============================================================================
async def create_all_tables() -> None:
    """
    Create all database tables defined in models.
    
    Note: In production, use Alembic migrations instead.
    """
    try:
        async with db_manager.engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
        logger.info("Successfully created all database tables")
    except Exception as e:
        logger.error(f"Failed to create database tables: {e}")
        raise


async def drop_all_tables() -> None:
    """
    Drop all database tables.
    
    WARNING: This will delete all data!
    Only use in development/testing.
    """
    if settings.is_production:
        raise RuntimeError("Cannot drop tables in production environment")
    
    try:
        async with db_manager.engine.begin() as conn:
            await conn.run_sync(Base.metadata.drop_all)
        logger.warning("All database tables dropped")
    except Exception as e:
        logger.error(f"Failed to drop database tables: {e}")
        raise


async def get_database_info() -> dict:
    """
    Get database information and statistics.
    
    Returns:
        dict: Database information including version, connections, etc.
    """
    try:
        async with db_manager.engine.begin() as conn:
            # Get PostgreSQL version
            version_result = await conn.execute(text("SELECT version()"))
            version = version_result.scalar()
            
            # Get current database name
            db_result = await conn.execute(text("SELECT current_database()"))
            current_db = db_result.scalar()
            
            # Get connection count
            conn_result = await conn.execute(text(
                "SELECT count(*) FROM pg_stat_activity WHERE state = 'active'"
            ))
            active_connections = conn_result.scalar()
            
            return {
                "version": version,
                "database": current_db,
                "active_connections": active_connections,
                "pool_size": settings.DATABASE_POOL_SIZE,
                "max_overflow": settings.DATABASE_MAX_OVERFLOW,
                "is_connected": db_manager.is_connected,
            }
    except Exception as e:
        logger.error(f"Failed to get database info: {e}")
        return {"error": str(e)}


# =============================================================================
# Startup and Shutdown Events
# =============================================================================
async def init_database() -> None:
    """
    Initialize database connection.
    Called during application startup.
    """
    logger.info("Initializing database connection...")
    await db_manager.connect()
    
    # In development, optionally create tables
    if settings.is_development and settings.DEV_RESET_DB:
        logger.warning("Development mode: Recreating database tables")
        await drop_all_tables()
        await create_all_tables()
    elif settings.is_development:
        await create_all_tables()


async def close_database() -> None:
    """
    Close database connection.
    Called during application shutdown.
    """
    logger.info("Closing database connection...")
    await db_manager.disconnect()


# =============================================================================
# Database Health Check Endpoint Data
# =============================================================================
async def get_health_status() -> dict:
    """
    Get comprehensive database health status.
    Used by health check endpoints.
    """
    is_healthy = await db_manager.health_check()
    db_info = await get_database_info() if is_healthy else {}
    
    return {
        "status": "healthy" if is_healthy else "unhealthy",
        "connected": db_manager.is_connected,
        "details": db_info
    } 