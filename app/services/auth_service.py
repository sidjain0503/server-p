"""
Authentication Service for InscribeVerse Meta-Engine

JWT-based authentication with multi-provider support.
Starts with email/password but designed to scale to OAuth providers.
"""

import bcrypt
import jwt
from jwt.exceptions import ExpiredSignatureError, InvalidTokenError
from datetime import datetime, timedelta
from typing import Optional, Dict, Any, List
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_
from fastapi import HTTPException, status

from app.core.config import settings
from app.meta_engine.orchestrator import get_meta_engine
from app.meta_engine.crud_service import QueryParams
from app.services.saas_plans import (
    SubscriptionPlan, get_user_permissions, get_plan_features, 
    check_usage_limit, SUBSCRIPTION_PLANS
)


class AuthService:
    """
    Authentication service supporting multiple auth providers.
    Currently implements email/password, ready for OAuth expansion.
    """
    
    def __init__(self):
        self.secret_key = settings.SECRET_KEY
        self.algorithm = "HS256"
        self.access_token_expire_minutes = settings.ACCESS_TOKEN_EXPIRE_MINUTES
        
    async def register_user(
        self, 
        session: AsyncSession,
        email: str,
        username: str, 
        password: str,
        display_name: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Register a new user with email/password authentication.
        
        Args:
            session: Database session
            email: User's email address
            username: Unique username
            password: Plain text password (will be hashed)
            display_name: Optional display name
            
        Returns:
            Dict containing user info and JWT token
        """
        try:
            meta_engine = get_meta_engine()
            user_crud = meta_engine.get_crud_service("User")
            auth_method_crud = meta_engine.get_crud_service("AuthMethod")
            
            # Check if user already exists
            existing_user = await self._get_user_by_email(session, email)
            if existing_user:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="User with this email already exists"
                )
            
            existing_username = await self._get_user_by_username(session, username)
            if existing_username:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Username already taken"
                )
            
            # Create user
            user_data = {
                "email": email,
                "username": username,
                "display_name": display_name or username,
                "is_active": True,
                "is_superuser": False,
                "email_verified": False,
                # SaaS subscription defaults for new users
                "subscription_plan": "free_plan",
                "subscription_status": "active",
                "ai_requests_used": 0,
                "ai_requests_limit": 100,  # Free plan default
                "billing_cycle_start": datetime.utcnow(),
            }
            
            user = await user_crud.create(session=session, data=user_data)
            
            # Create local auth method with hashed password
            password_hash = self._hash_password(password)
            auth_method_data = {
                "user_id": user.id,
                "provider": "local",
                "password_hash": password_hash,
                "is_primary": True,
                "last_used": datetime.utcnow(),
            }
            
            await auth_method_crud.create(session=session, data=auth_method_data)
            
            # Assign default role
            await self._assign_default_role(session, user.id)
            
            # Generate JWT token
            access_token = await self._create_access_token(session, user.id)
            
            return {
                "user": {
                    "id": user.id,
                    "email": user.email,
                    "username": user.username,
                    "display_name": user.display_name,
                    "is_active": user.is_active,
                },
                "access_token": access_token,
                "token_type": "bearer"
            }
            
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Registration failed: {str(e)}"
            )
    
    async def authenticate_user(
        self,
        session: AsyncSession,
        email: str,
        password: str
    ) -> Dict[str, Any]:
        """
        Authenticate user with email/password.
        
        Args:
            session: Database session
            email: User's email
            password: Plain text password
            
        Returns:
            Dict containing user info and JWT token
        """
        try:
            # Get user by email
            user = await self._get_user_by_email(session, email)
            if not user:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Invalid email or password"
                )
            
            if not user.is_active:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Account is disabled"
                )
            
            # Get local auth method
            auth_method = await self._get_auth_method(session, user.id, "local")
            if not auth_method or not auth_method.password_hash:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Invalid email or password"
                )
            
            # Verify password
            if not self._verify_password(password, auth_method.password_hash):
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Invalid email or password"
                )
            
            # Update last login and auth method usage
            await self._update_last_login(session, user.id)
            await self._update_auth_method_usage(session, auth_method.id)
            
            # Generate JWT token
            access_token = await self._create_access_token(session, user.id)
            
            return {
                "user": {
                    "id": user.id,
                    "email": user.email,
                    "username": user.username,
                    "display_name": user.display_name,
                    "is_active": user.is_active,
                },
                "access_token": access_token,
                "token_type": "bearer"
            }
            
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Authentication failed: {str(e)}"
            )
    
    async def get_current_user(
        self,
        session: AsyncSession,
        token: str
    ) -> Dict[str, Any]:
        """
        Get current user from JWT token.
        
        Args:
            session: Database session
            token: JWT token
            
        Returns:
            User information with roles and permissions
        """
        try:
            # Decode JWT token
            payload = jwt.decode(token, self.secret_key, algorithms=[self.algorithm])
            user_id = payload.get("user_id")
            
            if user_id is None:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Invalid authentication token"
                )
            
            # Get user with roles and permissions
            user_data = await self._get_user_with_permissions(session, user_id)
            if not user_data:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="User not found"
                )
            
            return user_data
            
        except ExpiredSignatureError:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Authentication token has expired"
            )
        except InvalidTokenError:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid authentication token"
            )
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Authentication failed: {str(e)}"
            )
    
    def _hash_password(self, password: str) -> str:
        """Hash password using bcrypt."""
        salt = bcrypt.gensalt()
        return bcrypt.hashpw(password.encode('utf-8'), salt).decode('utf-8')
    
    def _verify_password(self, plain_password: str, hashed_password: str) -> bool:
        """Verify password against hash."""
        return bcrypt.checkpw(
            plain_password.encode('utf-8'), 
            hashed_password.encode('utf-8')
        )
    
    async def _create_access_token(self, session: AsyncSession, user_id: int) -> str:
        """Create JWT access token with user permissions."""
        # Get user with permissions
        user_data = await self._get_user_with_permissions(session, user_id)
        
        # Create JWT payload
        payload = {
            "user_id": user_id,
            "email": user_data["email"],
            "username": user_data["username"],
            "roles": user_data["roles"],
            "permissions": user_data["permissions"],
            "is_superuser": user_data["is_superuser"],
            "exp": datetime.utcnow() + timedelta(minutes=self.access_token_expire_minutes),
            "iat": datetime.utcnow(),
            "type": "access_token"
        }
        
        return jwt.encode(payload, self.secret_key, algorithm=self.algorithm)
    
    async def _get_user_by_email(self, session: AsyncSession, email: str):
        """Get user by email address."""
        meta_engine = get_meta_engine()
        user_crud = meta_engine.get_crud_service("User")
        
        # Use proper QueryParams instead of PaginationParams
        params = QueryParams(skip=0, limit=1000, include_deleted=False)
        users = await user_crud.list(session=session, params=params)
        for user in users:
            if user.email == email:
                return user
        return None
    
    async def _get_user_by_username(self, session: AsyncSession, username: str):
        """Get user by username."""
        meta_engine = get_meta_engine()
        user_crud = meta_engine.get_crud_service("User")
        
        params = QueryParams(skip=0, limit=1000, include_deleted=False)
        users = await user_crud.list(session=session, params=params)
        for user in users:
            if user.username == username:
                return user
        return None
    
    async def _get_auth_method(self, session: AsyncSession, user_id: int, provider: str):
        """Get authentication method for user and provider."""
        meta_engine = get_meta_engine()
        auth_method_crud = meta_engine.get_crud_service("AuthMethod")
        
        params = QueryParams(skip=0, limit=1000, include_deleted=False)
        auth_methods = await auth_method_crud.list(session=session, params=params)
        for auth_method in auth_methods:
            if auth_method.user_id == user_id and auth_method.provider == provider:
                return auth_method
        return None
    
    async def _get_user_with_permissions(self, session: AsyncSession, user_id: int) -> Dict[str, Any]:
        """Get user with their subscription plan permissions and limits."""
        meta_engine = get_meta_engine()
        user_crud = meta_engine.get_crud_service("User")
        
        user = await user_crud.get(session=session, record_id=user_id)
        if not user:
            return None
        
        # Get user's subscription plan
        subscription_plan = getattr(user, 'subscription_plan', 'free_plan')
        
        # Convert string to enum
        try:
            plan_enum = SubscriptionPlan(subscription_plan)
        except ValueError:
            plan_enum = SubscriptionPlan.FREE_PLAN
        
        # Get plan features and permissions
        plan_features = get_plan_features(plan_enum)
        permissions = get_user_permissions(plan_enum)
        
        # Get usage limits
        limits = plan_features.limits
        
        return {
            "id": user.id,
            "email": user.email,
            "username": user.username,
            "display_name": user.display_name,
            "is_active": user.is_active,
            "is_superuser": user.is_superuser,
            "subscription_plan": subscription_plan,
            "subscription_status": getattr(user, 'subscription_status', 'active'),
            "roles": [subscription_plan],  # Plan acts as role
            "permissions": permissions,
            "plan_features": {
                "ai_models": [model.value for model in plan_features.ai_models],
                "ai_features": [feature.value for feature in plan_features.ai_features],
                "priority_support": plan_features.priority_support,
                "custom_branding": plan_features.custom_branding,
                "analytics_dashboard": plan_features.analytics_dashboard
            },
            "usage_limits": {
                "ai_requests_per_month": limits.ai_requests_per_month,
                "max_documents": limits.max_documents,
                "max_projects": limits.max_projects,
                "max_team_members": limits.max_team_members,
                "storage_gb": limits.storage_gb,
                "api_calls_per_minute": limits.api_calls_per_minute,
                "concurrent_generations": limits.concurrent_generations
            },
            "current_usage": {
                "ai_requests_used": getattr(user, 'ai_requests_used', 0),
                "billing_cycle_start": getattr(user, 'billing_cycle_start', None)
            }
        }
    
    async def _assign_default_role(self, session: AsyncSession, user_id: int):
        """Assign default role to new user."""
        # For now, just mark in user record
        # TODO: Implement proper role assignment when RBAC is fully implemented
        pass
    
    async def _update_last_login(self, session: AsyncSession, user_id: int):
        """Update user's last login timestamp."""
        meta_engine = get_meta_engine()
        user_crud = meta_engine.get_crud_service("User")
        
        await user_crud.update(
            session=session,
            record_id=user_id,
            data={"last_login": datetime.utcnow()}
        )
    
    async def _update_auth_method_usage(self, session: AsyncSession, auth_method_id: int):
        """Update when auth method was last used."""
        meta_engine = get_meta_engine()
        auth_method_crud = meta_engine.get_crud_service("AuthMethod")
        
        await auth_method_crud.update(
            session=session,
            record_id=auth_method_id,
            data={"last_used": datetime.utcnow()}
        )


# Singleton instance
auth_service = AuthService()


def get_auth_service() -> AuthService:
    """Get the authentication service instance."""
    return auth_service 