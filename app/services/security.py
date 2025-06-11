"""
Security Dependencies for InscribeVerse Meta-Engine

This module provides authentication and authorization dependencies
for protecting API endpoints.
"""

from typing import Dict, Any, List, Optional
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db_session
from app.services.saas_plans import SubscriptionPlan, AIFeature, AIModel, can_access_feature, can_use_model

# Security scheme for JWT tokens
security = HTTPBearer()


# Type alias for user data
User = Dict[str, Any]


# Optional dependency for public routes
def get_optional_user() -> Optional[User]:
    """Optional user dependency - returns None for public routes."""
    return None


# SaaS Plan constants
class Plans:
    """Subscription plan constants."""
    FREE_PLAN = "free_plan"
    PREMIUM = "premium"
    ALL_ACCESS = "all_access"
    ADMIN = "admin"
    SUPER_ADMIN = "super_admin"


# Permission constants (AI SaaS focused)
# Content permissions
CONTENT_CREATE_BASIC = "content:create_basic"
CONTENT_CREATE_ADVANCED = "content:create_advanced"
CONTENT_CREATE_PREMIUM = "content:create_premium"
CONTENT_READ = "content:read"
CONTENT_UPDATE = "content:update"
CONTENT_DELETE = "content:delete"
CONTENT_BULK_PROCESS = "content:bulk_process"

# AI Model permissions
AI_GPT_3_5 = "ai:gpt-3.5-turbo"
AI_GPT_4 = "ai:gpt-4"
AI_CLAUDE = "ai:claude"

# Analytics permissions
ANALYTICS_VIEW_BASIC = "analytics:view_basic"
ANALYTICS_VIEW_ADVANCED = "analytics:view_advanced"

# Admin permissions
USERS_READ = "users:read"
USERS_UPDATE = "users:update"
USERS_SUSPEND = "users:suspend"
BILLING_VIEW = "billing:view"
PLATFORM_MODERATE = "platform:moderate"


# Permission constants
PRODUCT_CREATE = "product:create"
PRODUCT_READ = "product:read"
PRODUCT_UPDATE = "product:update"
PRODUCT_DELETE = "product:delete"

CUSTOMER_CREATE = "customer:create"
CUSTOMER_READ = "customer:read"
CUSTOMER_UPDATE = "customer:update"
CUSTOMER_DELETE = "customer:delete"

TASK_CREATE = "task:create"
TASK_READ = "task:read"
TASK_UPDATE = "task:update"
TASK_DELETE = "task:delete"

USER_CREATE = "user:create"
USER_READ = "user:read"
USER_UPDATE = "user:update"
USER_DELETE = "user:delete"


# Role constants
ADMIN = "admin"
MANAGER = "manager"
USER_ROLE = "user"
VIEWER = "viewer"


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    session: AsyncSession = Depends(get_db_session)
) -> User:
    """
    Get the current authenticated user from JWT token.
    
    Args:
        credentials: JWT token from Authorization header
        session: Database session
        
    Returns:
        User data dictionary
        
    Raises:
        HTTPException: If token is invalid or user not found
    """
    # Import here to avoid circular import
    from app.services.auth_service import get_auth_service
    
    auth_service = get_auth_service()
    
    try:
        # Extract token from credentials
        token = credentials.credentials
        
        # Get user from token
        user = await auth_service.get_current_user(session, token)
        
        return user
        
    except HTTPException:
        # Re-raise auth service exceptions
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )


async def get_current_active_user(
    current_user: User = Depends(get_current_user)
) -> User:
    """
    Get the current active user (not disabled).
    
    Args:
        current_user: Current user from get_current_user
        
    Returns:
        Active user data
        
    Raises:
        HTTPException: If user is inactive
    """
    if not current_user.get("is_active", False):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Inactive user"
        )
    return current_user


async def get_current_superuser(
    current_user: User = Depends(get_current_user)
) -> User:
    """
    Get the current superuser.
    
    Args:
        current_user: Current user from get_current_user
        
    Returns:
        Superuser data
        
    Raises:
        HTTPException: If user is not a superuser
    """
    if not current_user.get("is_superuser", False):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )
    return current_user


def require_permissions(*required_permissions: str):
    """
    Create a dependency that requires specific permissions.
    
    Args:
        *required_permissions: List of required permission strings
        
    Returns:
        FastAPI dependency function
    """
    def permission_checker(current_user: User = Depends(get_current_active_user)) -> User:
        user_permissions = current_user.get("permissions", [])
        
        # Superusers have all permissions
        if current_user.get("is_superuser", False):
            return current_user
        
        # Check if user has all required permissions
        for permission in required_permissions:
            if permission not in user_permissions:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail=f"Permission required: {permission}"
                )
        
        return current_user
    
    return permission_checker


def require_roles(*required_roles: str):
    """
    Create a dependency that requires specific roles.
    
    Args:
        *required_roles: List of required role names
        
    Returns:
        FastAPI dependency function
    """
    def role_checker(current_user: User = Depends(get_current_active_user)) -> User:
        user_roles = current_user.get("roles", [])
        
        # Check if user has any of the required roles
        for role in required_roles:
            if role in user_roles:
                return current_user
        
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"Role required: one of {required_roles}"
        )
    
    return role_checker


# Schema-specific permission helpers
def require_product_read():
    """Require product read permission."""
    return require_permissions(PRODUCT_READ)


def require_product_write():
    """Require product create/update permissions."""
    return require_permissions(PRODUCT_CREATE, PRODUCT_UPDATE)


def require_customer_read():
    """Require customer read permission."""
    return require_permissions(CUSTOMER_READ)


def require_customer_write():
    """Require customer create/update permissions."""
    return require_permissions(CUSTOMER_CREATE, CUSTOMER_UPDATE)


def require_task_read():
    """Require task read permission."""
    return require_permissions(TASK_READ)


def require_task_write():
    """Require task create/update permissions."""
    return require_permissions(TASK_CREATE, TASK_UPDATE)


# Admin-only dependencies
def require_admin():
    """Require admin role."""
    return require_roles(ADMIN)


def require_manager():
    """Require manager or admin role."""
    return require_roles(MANAGER, ADMIN)


# SaaS Plan-based dependencies
def require_plan(*required_plans: str):
    """
    Create a dependency that requires specific subscription plans.
    
    Args:
        *required_plans: List of required plan names
        
    Returns:
        FastAPI dependency function
    """
    def plan_checker(current_user: User = Depends(get_current_active_user)) -> User:
        user_plan = current_user.get("subscription_plan", "free_plan")
        
        # Super admin bypasses all checks
        if current_user.get("is_superuser", False):
            return current_user
        
        # Check if user has any of the required plans
        if user_plan not in required_plans:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Plan required: one of {required_plans}. Current plan: {user_plan}"
            )
        
        return current_user
    
    return plan_checker


def require_ai_feature(feature: AIFeature):
    """
    Create a dependency that requires access to a specific AI feature.
    
    Args:
        feature: AI feature required
        
    Returns:
        FastAPI dependency function
    """
    def feature_checker(current_user: User = Depends(get_current_active_user)) -> User:
        user_plan = current_user.get("subscription_plan", "free_plan")
        
        # Super admin has access to all features
        if current_user.get("is_superuser", False):
            return current_user
        
        try:
            plan_enum = SubscriptionPlan(user_plan)
        except ValueError:
            plan_enum = SubscriptionPlan.FREE_PLAN
        
        if not can_access_feature(plan_enum, feature):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Feature '{feature.value}' not available in {user_plan} plan"
            )
        
        return current_user
    
    return feature_checker


def require_ai_model(model: AIModel):
    """
    Create a dependency that requires access to a specific AI model.
    
    Args:
        model: AI model required
        
    Returns:
        FastAPI dependency function
    """
    def model_checker(current_user: User = Depends(get_current_active_user)) -> User:
        user_plan = current_user.get("subscription_plan", "free_plan")
        
        # Super admin has access to all models
        if current_user.get("is_superuser", False):
            return current_user
        
        try:
            plan_enum = SubscriptionPlan(user_plan)
        except ValueError:
            plan_enum = SubscriptionPlan.FREE_PLAN
        
        if not can_use_model(plan_enum, model):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"AI model '{model.value}' not available in {user_plan} plan"
            )
        
        return current_user
    
    return model_checker


def check_usage_limit(limit_type: str):
    """
    Create a dependency that checks usage limits for the current billing cycle.
    
    Args:
        limit_type: Type of limit to check (ai_requests_per_month, max_documents, etc.)
        
    Returns:
        FastAPI dependency function
    """
    def limit_checker(current_user: User = Depends(get_current_active_user)) -> User:
        user_plan = current_user.get("subscription_plan", "free_plan")
        
        # Super admin bypasses usage limits
        if current_user.get("is_superuser", False):
            return current_user
        
        try:
            plan_enum = SubscriptionPlan(user_plan)
        except ValueError:
            plan_enum = SubscriptionPlan.FREE_PLAN
        
        # Get current usage (this would come from usage tracking)
        current_usage = current_user.get("current_usage", {}).get(limit_type, 0)
        
        if not check_usage_limit(plan_enum, limit_type, current_usage):
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail=f"Usage limit exceeded for {limit_type} in {user_plan} plan"
            )
        
        return current_user
    
    return limit_checker


# Convenient plan-based dependencies
def require_premium_or_higher():
    """Require Premium, All Access, Admin, or Super Admin plan."""
    return require_plan(Plans.PREMIUM, Plans.ALL_ACCESS, Plans.ADMIN, Plans.SUPER_ADMIN)


def require_all_access_or_higher():
    """Require All Access, Admin, or Super Admin plan."""
    return require_plan(Plans.ALL_ACCESS, Plans.ADMIN, Plans.SUPER_ADMIN)


def require_admin_access():
    """Require Admin or Super Admin plan."""
    return require_plan(Plans.ADMIN, Plans.SUPER_ADMIN)


# AI feature-specific dependencies
def require_advanced_ai():
    """Require access to advanced AI features."""
    return require_ai_feature(AIFeature.AI_EDITING)


def require_bulk_processing():
    """Require access to bulk processing."""
    return require_ai_feature(AIFeature.BULK_PROCESSING)


def require_custom_models():
    """Require access to custom AI models."""
    return require_ai_feature(AIFeature.CUSTOM_MODELS)


# AI model-specific dependencies
def require_gpt4():
    """Require access to GPT-4 model."""
    return require_ai_model(AIModel.GPT_4)


def require_claude_opus():
    """Require access to Claude Opus model."""
    return require_ai_model(AIModel.CLAUDE_OPUS) 