"""
API v1 package for InscribeVerse Meta-Engine System

This package contains all version 1 API endpoints, combining:
- Auto-generated CRUD routes from meta-engine
- Custom business logic routes
- Authentication routes
- AI SaaS features routes
"""

from fastapi import APIRouter
from app.api.v1.routes import products, customers, tasks, auth, ai_content

# Create the main v1 router
api_router = APIRouter()

# Include authentication routes
api_router.include_router(
    auth.router,
    prefix="/auth",
    tags=["Authentication"]
)

# Include AI content generation routes (SaaS features)
api_router.include_router(
    ai_content.router,
    prefix="/ai",
    tags=["AI Content Generation"]
)

# Include custom business logic routes
api_router.include_router(
    products.router, 
    prefix="/products", 
    tags=["Products"]
)
api_router.include_router(
    customers.router, 
    prefix="/customers", 
    tags=["Customers"]
)
api_router.include_router(
    tasks.router, 
    prefix="/tasks", 
    tags=["Tasks"]
)

__all__ = ["api_router"] 