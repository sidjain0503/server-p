"""
InscribeVerse Meta-System FastAPI Application

This is the main application entry point that brings together:
- Configuration management
- Database connections
- API routes
- Middleware
- Error handling
- Health checks
- Auto-documentation
"""

import logging
import time
from contextlib import asynccontextmanager
from typing import Dict, Any

from fastapi import FastAPI, Request, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException
from starlette.middleware.base import BaseHTTPMiddleware

# Core imports
from app import __version__, __title__, __description__, __author__
from app.core.config import settings, get_settings
from app.core.database import (
    init_database, 
    close_database, 
    get_health_status,
    get_database_info
)

# Add meta-engine import
from app.meta_engine.orchestrator import register_all_meta_routes, get_meta_engine
from app.meta_engine.demo import create_demo_schemas

# API imports - NEW: Using organized API structure
from app.api.v1 import api_router as api_v1_router

# Meta-engine imports
from app.meta_engine.orchestrator import get_meta_engine
from app.models.schemas.registry import register_all_schemas

# Configure logging
logging.basicConfig(
    level=getattr(logging, settings.LOG_LEVEL),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


# =============================================================================
# Custom Middleware
# =============================================================================
class ProcessTimeMiddleware(BaseHTTPMiddleware):
    """Middleware to add processing time header to responses."""
    
    async def dispatch(self, request: Request, call_next):
        start_time = time.time()
        response = await call_next(request)
        process_time = time.time() - start_time
        response.headers["X-Process-Time"] = str(process_time)
        return response


class LoggingMiddleware(BaseHTTPMiddleware):
    """Middleware to log all requests."""
    
    async def dispatch(self, request: Request, call_next):
        start_time = time.time()
        
        # Log request
        logger.info(f"Request: {request.method} {request.url}")
        
        response = await call_next(request)
        
        # Log response
        process_time = time.time() - start_time
        logger.info(
            f"Response: {response.status_code} - "
            f"Time: {process_time:.4f}s - "
            f"Path: {request.url.path}"
        )
        
        return response


class RequestResponseLoggerMiddleware(BaseHTTPMiddleware):
    """Middleware to log requests and responses."""
    
    async def dispatch(self, request: Request, call_next):
        start_time = time.time()
        
        # Log request
        logger.info(f"📥 {request.method} {request.url}")
        
        response = await call_next(request)
        
        # Log response
        process_time = time.time() - start_time
        logger.info(
            f"📤 {response.status_code} - {process_time:.3f}s - {request.url.path}"
        )
        
        return response


class RateLimitMiddleware(BaseHTTPMiddleware):
    """Simple rate limiting middleware."""
    
    def __init__(self, app, calls: int = 100, period: int = 60):
        super().__init__(app)
        self.calls = calls
        self.period = period
        self.clients = {}
    
    async def dispatch(self, request: Request, call_next):
        # Simple rate limiting (in production, use Redis)
        client_ip = request.client.host
        current_time = time.time()
        
        # Clean old entries
        self.clients = {
            ip: requests for ip, requests in self.clients.items()
            if any(req_time > current_time - self.period for req_time in requests)
        }
        
        # Check rate limit
        if client_ip in self.clients:
            recent_requests = [
                req_time for req_time in self.clients[client_ip]
                if req_time > current_time - self.period
            ]
            if len(recent_requests) >= self.calls:
                return JSONResponse(
                    status_code=429,
                    content={"detail": "Rate limit exceeded"}
                )
            self.clients[client_ip] = recent_requests + [current_time]
        else:
            self.clients[client_ip] = [current_time]
        
        return await call_next(request)


# =============================================================================
# Application Lifecycle Management
# =============================================================================
@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Application lifespan manager.
    Handles startup and shutdown events.
    """
    # Startup
    logger.info(f"Starting {settings.APP_NAME} v{settings.APP_VERSION}")
    logger.info(f"Environment: {settings.ENVIRONMENT}")
    logger.info(f"Debug mode: {settings.DEBUG}")
    
    try:
        # Initialize database
        await init_database()
        logger.info("✅ Database initialized successfully")
        
        # Register all schemas with meta-engine
        logger.info("🎯 Registering schemas with meta-engine...")
        register_all_schemas()
        logger.info("✅ Schemas registered successfully")
        
        # Register meta-engine auto-generated routes after schemas are available
        logger.info("🔗 Registering auto-generated CRUD routes...")
        register_meta_engine_routes(app)
        
        # TODO: Initialize other services (Redis, Celery, etc.)
        
        logger.info("🚀 Application startup complete")
        
    except Exception as e:
        logger.error(f"❌ Startup failed: {e}")
        raise
    
    yield  # Application runs here
    
    # Shutdown
    logger.info("Shutting down application...")
    
    try:
        # Close database connections
        await close_database()
        logger.info("✅ Database connections closed")
        
        # TODO: Cleanup other services
        
        logger.info("👋 Application shutdown complete")
        
    except Exception as e:
        logger.error(f"❌ Shutdown error: {e}")


# =============================================================================
# FastAPI Application Instance
# =============================================================================
def create_application() -> FastAPI:
    """
    Application factory function.
    Creates and configures the FastAPI application.
    """
    
    app = FastAPI(
        title=settings.APP_NAME,
        version=settings.APP_VERSION,
        description="InscribeVerse - AI-Powered Meta-Engine Platform",
        openapi_url=settings.OPENAPI_URL if settings.DEBUG else None,
        docs_url=settings.DOCS_URL if settings.DEBUG else None,
        redoc_url=settings.REDOC_URL if settings.DEBUG else None,
        lifespan=lifespan,  # Use the lifespan context manager
    )
    
    # Configure CORS
    cors_config = settings.get_cors_config()
    app.add_middleware(
        CORSMiddleware,
        allow_origins=cors_config["allow_origins"],
        allow_credentials=cors_config["allow_credentials"],
        allow_methods=cors_config["allow_methods"],
        allow_headers=cors_config["allow_headers"],
    )
    
    # Add custom middleware
    app.add_middleware(RequestResponseLoggerMiddleware)
    app.add_middleware(RateLimitMiddleware, calls=100, period=60)
    
    # Register routes
    register_routes(app)
    
    return app


def setup_middleware(app: FastAPI) -> None:
    """Configure all middleware for the application."""
    
    # Security middleware
    if not settings.DEBUG:
        app.add_middleware(
            TrustedHostMiddleware, 
            allowed_hosts=["localhost", "127.0.0.1", "*.inscribeverse.com"]
        )
    
    # CORS middleware
    cors_config = settings.get_cors_config()
    app.add_middleware(
        CORSMiddleware,
        allow_origins=cors_config["allow_origins"],
        allow_credentials=cors_config["allow_credentials"],
        allow_methods=cors_config["allow_methods"],
        allow_headers=cors_config["allow_headers"],
    )
    
    # Custom middleware
    app.add_middleware(ProcessTimeMiddleware)
    
    if settings.DEBUG:
        app.add_middleware(LoggingMiddleware)


def setup_exception_handlers(app: FastAPI) -> None:
    """Configure custom exception handlers."""
    
    @app.exception_handler(StarletteHTTPException)
    async def http_exception_handler(request: Request, exc: StarletteHTTPException):
        """Handle HTTP exceptions with consistent error format."""
        return JSONResponse(
            status_code=exc.status_code,
            content={
                "error": True,
                "message": exc.detail,
                "status_code": exc.status_code,
                "path": request.url.path,
                "timestamp": time.time(),
            }
        )
    
    @app.exception_handler(RequestValidationError)
    async def validation_exception_handler(request: Request, exc: RequestValidationError):
        """Handle request validation errors."""
        return JSONResponse(
            status_code=422,
            content={
                "error": True,
                "message": "Validation error",
                "details": exc.errors(),
                "status_code": 422,
                "path": request.url.path,
                "timestamp": time.time(),
            }
        )
    
    @app.exception_handler(Exception)
    async def general_exception_handler(request: Request, exc: Exception):
        """Handle unexpected exceptions."""
        logger.error(f"Unhandled exception: {exc}", exc_info=True)
        
        if settings.DEBUG:
            # In debug mode, show the actual error
            return JSONResponse(
                status_code=500,
                content={
                    "error": True,
                    "message": str(exc),
                    "type": type(exc).__name__,
                    "status_code": 500,
                    "path": request.url.path,
                    "timestamp": time.time(),
                }
            )
        else:
            # In production, hide internal errors
            return JSONResponse(
                status_code=500,
                content={
                    "error": True,
                    "message": "Internal server error",
                    "status_code": 500,
                    "path": request.url.path,
                    "timestamp": time.time(),
                }
            )


def register_routes(app: FastAPI) -> None:
    """Register all application routes."""
    
    @app.get("/", tags=["Root"])
    async def root():
        """Root endpoint with system information."""
        return {
            "message": "Welcome to InscribeVerse Meta-Engine Platform! 🚀",
            "app": settings.APP_NAME,
            "version": settings.APP_VERSION,
            "docs": "/docs",
            "health": "/health",
            "api": {
                "v1": "/api/v1/",
                "docs": "/docs",
                "schemas": ["products", "customers", "tasks"]
            },
            "meta_engine": "Active - Schema-driven API generation",
            "features": [
                "Dynamic API Generation",
                "Schema-to-API Transformation", 
                "Enterprise CRUD Operations",
                "Auto-documentation",
                "Type-safe Validation",
                "Organized API Structure"
            ]
        }
    
    @app.get("/health", tags=["Health"])
    async def health_check():
        """Health check endpoint with detailed system status."""
        try:
            # Get meta-engine status
            meta_engine = get_meta_engine()
            stats = meta_engine.get_system_stats()
            
            return {
                "status": "healthy",
                "timestamp": time.time(),
                "app": settings.APP_NAME,
                "version": settings.APP_VERSION,
                "environment": settings.ENVIRONMENT,
                "meta_engine": {
                    "status": "active",
                    "registered_schemas": stats.get("registered_schemas", 0),
                    "total_endpoints": stats.get("total_endpoints", 0),
                    "available_schemas": stats.get("schemas", [])
                },
                "api": {
                    "version": "v1",
                    "base_url": "/api/v1/"
                }
            }
        except Exception as e:
            return {
                "status": "healthy",
                "timestamp": time.time(),
                "app": settings.APP_NAME,
                "version": settings.APP_VERSION,
                "environment": settings.ENVIRONMENT,
                "meta_engine": {
                    "status": "error",
                    "error": str(e)
                }
            }
    
    # Include API v1 routes (custom business logic)
    app.include_router(api_v1_router, prefix="/api/v1")


def register_meta_engine_routes(app: FastAPI):
    """Register auto-generated CRUD routes from meta-engine."""
    try:
        meta_engine = get_meta_engine()
        
        # Define consistent tag mapping (schema_name -> plural_tag)
        tag_mapping = {
            # Business domain schemas
            "Product": "Products",
            "Customer": "Customers", 
            "Task": "Tasks",
            # Authentication schemas
            "User": "Users",
            "AuthMethod": "Auth Methods",
            "Role": "Roles",
            "UserRole": "User Roles",
        }
        
        # Include auto-generated CRUD routes for each registered schema
        for schema_name in meta_engine.list_schemas():
            auto_router = meta_engine.get_router(schema_name)
            if auto_router:
                # Use consistent plural tags
                plural_tag = tag_mapping.get(schema_name, f"{schema_name}s")
                prefix = f"/api/v1/{schema_name.lower()}s"
                
                app.include_router(
                    auto_router, 
                    prefix=prefix, 
                    tags=[plural_tag]
                )
                print(f"✅ Registered auto-generated CRUD routes for {schema_name} at {prefix} with tag '{plural_tag}'")
        
        print(f"🚀 Meta-engine auto-generated routes registered!")
        
    except Exception as e:
        print(f"❌ Failed to register meta-engine routes: {e}")
        # Don't raise - let the app continue without auto-generated routes


# =============================================================================
# Create Application Instance
# =============================================================================
app = create_application()


# =============================================================================
# Development Server
# =============================================================================
if __name__ == "__main__":
    import uvicorn
    
    logger.info(f"Starting development server...")
    logger.info(f"Environment: {settings.ENVIRONMENT}")
    logger.info(f"Database URL: {settings.DATABASE_URL}")
    
    uvicorn.run(
        "app.main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.RELOAD and settings.DEBUG,
        log_level=settings.LOG_LEVEL.lower(),
        access_log=settings.DEBUG,
    ) 