"""
Security dependencies and middleware for InscribeVerse Meta-Engine

JWT authentication with role-based access control.
Designed to scale from simple auth to multi-provider OAuth.
"""

from typing import Optional, List, Callable, Any
from functools import wraps

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db_session
from app.services.auth_service import get_auth_service, AuthService


# HTTP Bearer token scheme
oauth2_scheme = HTTPBearer(auto_error=False)


async def get_current_user(
    session: AsyncSession = Depends(get_db_session),
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(oauth2_scheme),
    auth_service: AuthService = Depends(get_auth_service)
):
    """
    Dependency to get current authenticated user from JWT token.
    
    Args:
        session: Database session
        credentials: HTTP Bearer credentials from request
        auth_service: Authentication service
        
    Returns:
        Current user data with roles and permissions
        
    Raises:
        HTTPException: If authentication fails
    """
    if not credentials:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication required",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    return await auth_service.get_current_user(session, credentials.credentials)


async def get_current_active_user(
    current_user: dict = Depends(get_current_user)
):
    """
    Dependency to get current active user.
    
    Args:
        current_user: User from get_current_user dependency
        
    Returns:
        Active user data
        
    Raises:
        HTTPException: If user is inactive
    """
    if not current_user.get("is_active", False):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Inactive user account"
        )
    return current_user


async def get_current_superuser(
    current_user: dict = Depends(get_current_active_user)
):
    """
    Dependency to get current superuser.
    
    Args:
        current_user: User from get_current_active_user dependency
        
    Returns:
        Superuser data
        
    Raises:
        HTTPException: If user is not a superuser
    """
    if not current_user.get("is_superuser", False):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Superuser privileges required"
        )
    return current_user


def require_permissions(*required_permissions: str):
    """
    Decorator to require specific permissions for an endpoint.
    
    Args:
        *required_permissions: List of permission strings required
        
    Returns:
        FastAPI dependency that checks permissions
        
    Example:
        @require_permissions("product:create", "product:update")
        async def create_product():
            pass
    """
    def dependency(current_user: dict = Depends(get_current_active_user)):
        user_permissions = set(current_user.get("permissions", []))
        required_perms = set(required_permissions)
        
        # Superusers have all permissions
        if current_user.get("is_superuser", False):
            return current_user
        
        # Check if user has all required permissions
        if not required_perms.issubset(user_permissions):
            missing_perms = required_perms - user_permissions
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Missing permissions: {', '.join(missing_perms)}"
            )
        
        return current_user
    
    return dependency


def require_roles(*required_roles: str):
    """
    Decorator to require specific roles for an endpoint.
    
    Args:
        *required_roles: List of role strings required
        
    Returns:
        FastAPI dependency that checks roles
        
    Example:
        @require_roles("admin", "manager")
        async def admin_endpoint():
            pass
    """
    def dependency(current_user: dict = Depends(get_current_active_user)):
        user_roles = set(current_user.get("roles", []))
        required_role_set = set(required_roles)
        
        # Superusers bypass role checks
        if current_user.get("is_superuser", False):
            return current_user
        
        # Check if user has any of the required roles
        if not required_role_set.intersection(user_roles):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Required roles: {', '.join(required_roles)}"
            )
        
        return current_user
    
    return dependency


def optional_auth():
    """
    Dependency for optional authentication.
    Returns user data if authenticated, None if not.
    
    Returns:
        User data or None
    """
    async def dependency(
        session: AsyncSession = Depends(get_db_session),
        credentials: Optional[HTTPAuthorizationCredentials] = Depends(oauth2_scheme),
        auth_service: AuthService = Depends(get_auth_service)
    ):
        if not credentials:
            return None
        
        try:
            return await auth_service.get_current_user(session, credentials.credentials)
        except HTTPException:
            return None
    
    return dependency


# Permission constants for easy reference
class Permissions:
    """Standard permission constants for the application."""
    
    # Product permissions
    PRODUCT_CREATE = "product:create"
    PRODUCT_READ = "product:read"
    PRODUCT_UPDATE = "product:update"
    PRODUCT_DELETE = "product:delete"
    
    # Customer permissions
    CUSTOMER_CREATE = "customer:create"
    CUSTOMER_READ = "customer:read"
    CUSTOMER_UPDATE = "customer:update"
    CUSTOMER_DELETE = "customer:delete"
    
    # Task permissions
    TASK_CREATE = "task:create"
    TASK_READ = "task:read"
    TASK_UPDATE = "task:update"
    TASK_DELETE = "task:delete"
    
    # User management permissions
    USER_CREATE = "user:create"
    USER_READ = "user:read"
    USER_UPDATE = "user:update"
    USER_DELETE = "user:delete"
    
    # Auth management permissions
    AUTH_MANAGE = "auth:manage"
    ROLE_MANAGE = "role:manage"
    
    # System permissions
    SYSTEM_ADMIN = "system:admin"
    SYSTEM_MONITOR = "system:monitor"


class Roles:
    """Standard role constants for the application."""
    
    ADMIN = "admin"
    MANAGER = "manager"
    USER = "user"
    VIEWER = "viewer"


# Route protection helpers for meta-engine integration
def get_schema_permissions(schema_name: str) -> dict:
    """
    Get standard CRUD permissions for a schema.
    
    Args:
        schema_name: Name of the schema (e.g., "Product", "Customer")
        
    Returns:
        Dict mapping operations to required permissions
    """
    schema_lower = schema_name.lower()
    return {
        "create": f"{schema_lower}:create",
        "read": f"{schema_lower}:read", 
        "update": f"{schema_lower}:update",
        "delete": f"{schema_lower}:delete",
        "list": f"{schema_lower}:read",
        "count": f"{schema_lower}:read",
    }


def protect_schema_routes(schema_name: str):
    """
    Get permission dependencies for all CRUD operations of a schema.
    
    Args:
        schema_name: Name of the schema
        
    Returns:
        Dict mapping operations to permission dependencies
    """
    permissions = get_schema_permissions(schema_name)
    
    return {
        "create": require_permissions(permissions["create"]),
        "read": require_permissions(permissions["read"]),
        "update": require_permissions(permissions["update"]),
        "delete": require_permissions(permissions["delete"]),
        "list": require_permissions(permissions["list"]),
        "count": require_permissions(permissions["count"]),
    } 