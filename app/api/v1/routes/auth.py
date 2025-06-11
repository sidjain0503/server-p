"""
Authentication routes for InscribeVerse Meta-Engine

JWT-based authentication with user registration, login, and management.
OAuth-ready architecture for future provider integration.
"""

from typing import Dict, Any
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel, EmailStr, Field, validator

from app.core.database import get_db_session
from app.core.security import (
    get_current_user, 
    get_current_active_user, 
    get_current_superuser,
    require_permissions,
    Permissions
)
from app.services.auth_service import get_auth_service, AuthService


# Request/Response Models
class UserRegisterRequest(BaseModel):
    """User registration request model."""
    email: EmailStr = Field(..., description="User's email address")
    username: str = Field(..., min_length=3, max_length=50, description="Unique username")
    password: str = Field(..., min_length=8, max_length=100, description="User password")
    display_name: str = Field(None, max_length=100, description="Display name (optional)")
    
    @validator('username')
    def username_alphanumeric(cls, v):
        if not v.replace('_', '').replace('-', '').isalnum():
            raise ValueError('Username must be alphanumeric (with - and _ allowed)')
        return v
    
    @validator('password')
    def password_strength(cls, v):
        if len(v) < 8:
            raise ValueError('Password must be at least 8 characters long')
        if not any(c.isupper() for c in v):
            raise ValueError('Password must contain at least one uppercase letter')
        if not any(c.islower() for c in v):
            raise ValueError('Password must contain at least one lowercase letter')
        if not any(c.isdigit() for c in v):
            raise ValueError('Password must contain at least one digit')
        return v


class UserLoginRequest(BaseModel):
    """User login request model."""
    email: EmailStr = Field(..., description="User's email address")
    password: str = Field(..., description="User password")


class AuthResponse(BaseModel):
    """Authentication response model."""
    user: Dict[str, Any] = Field(..., description="User information")
    access_token: str = Field(..., description="JWT access token")
    token_type: str = Field(default="bearer", description="Token type")


# Create router
router = APIRouter()


@router.post("/register", response_model=AuthResponse, status_code=status.HTTP_201_CREATED)
async def register_user(
    user_data: UserRegisterRequest,
    session: AsyncSession = Depends(get_db_session),
    auth_service: AuthService = Depends(get_auth_service)
):
    """
    Register a new user with email/password authentication.
    
    Creates a new user account and returns a JWT access token.
    """
    try:
        result = await auth_service.register_user(
            session=session,
            email=user_data.email,
            username=user_data.username,
            password=user_data.password,
            display_name=user_data.display_name
        )
        
        return AuthResponse(**result)
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Registration failed: {str(e)}"
        )


@router.post("/login", response_model=AuthResponse)
async def login_user(
    login_data: UserLoginRequest,
    session: AsyncSession = Depends(get_db_session),
    auth_service: AuthService = Depends(get_auth_service)
):
    """
    Authenticate user with email/password.
    
    Returns a JWT access token for successful authentication.
    """
    try:
        result = await auth_service.authenticate_user(
            session=session,
            email=login_data.email,
            password=login_data.password
        )
        
        return AuthResponse(**result)
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Authentication failed: {str(e)}"
        )


@router.post("/logout")
async def logout_user(
    current_user: dict = Depends(get_current_active_user)
):
    """
    Logout current user.
    
    For JWT tokens, logout is handled client-side by discarding the token.
    This endpoint can be used for logging/audit purposes.
    """
    return {
        "message": "Successfully logged out",
        "user_id": current_user["id"]
    }


@router.get("/me")
async def get_current_user_info(
    current_user: dict = Depends(get_current_active_user)
):
    """
    Get current authenticated user information.
    
    Returns detailed information about the currently authenticated user.
    """
    return current_user 