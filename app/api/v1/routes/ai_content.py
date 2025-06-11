"""
AI Content Generation API for InscribeVerse AI SaaS Platform

Demonstrates subscription plan-based access control for AI features.
Different plans get access to different AI models and features.
"""

from typing import List, Optional, Dict, Any
from fastapi import APIRouter, HTTPException, Depends, Path, Body, status
from fastapi.responses import JSONResponse
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel, Field

from app.core.database import get_db_session
from app.services.security import (
    get_current_user, User,
    require_premium_or_higher, require_all_access_or_higher, require_admin_access,
    require_gpt4, require_claude_opus, require_bulk_processing
)


# Request/Response Models
class ContentGenerationRequest(BaseModel):
    """Request model for AI content generation."""
    prompt: str = Field(..., min_length=10, max_length=2000, description="Content generation prompt")
    ai_model: Optional[str] = Field("gpt-3.5-turbo", description="AI model to use")
    tone: Optional[str] = Field("professional", description="Content tone")
    length: Optional[str] = Field("medium", description="Content length (short, medium, long)")


class ContentResponse(BaseModel):
    """Response model for generated content."""
    content: str = Field(..., description="Generated content")
    model_used: str = Field(..., description="AI model used")
    tokens_used: int = Field(..., description="Tokens consumed")
    generation_time: float = Field(..., description="Generation time in seconds")


class UsageStatsResponse(BaseModel):
    """Response model for user usage statistics."""
    current_usage: Dict[str, Any] = Field(..., description="Current usage stats")
    limits: Dict[str, Any] = Field(..., description="Plan limits")
    plan_features: Dict[str, Any] = Field(..., description="Available features")


# Create router
router = APIRouter()


@router.post("/generate", response_model=ContentResponse, summary="Generate AI Content - FREE+")
async def generate_content(
    request: ContentGenerationRequest,
    current_user: User = Depends(get_current_user),  # All plans can access basic generation
    session: AsyncSession = Depends(get_db_session)
):
    """
    Generate AI content using available models based on subscription plan.
    
    - **Free Plan**: GPT-3.5 Turbo only, 100 requests/month
    - **Premium+**: GPT-4, Claude access, 2000+ requests/month
    - **All Access+**: All models including GPT-4 Turbo, Claude Opus
    """
    try:
        # Check if user can use the requested model
        user_plan = current_user.get("subscription_plan", "free_plan")
        available_models = current_user.get("plan_features", {}).get("ai_models", [])
        
        if request.ai_model not in available_models:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"AI model '{request.ai_model}' not available in {user_plan} plan"
            )
        
        # Simulate AI content generation
        mock_content = f"Generated content for: '{request.prompt}' using {request.ai_model}"
        
        return ContentResponse(
            content=mock_content,
            model_used=request.ai_model,
            tokens_used=150,
            generation_time=2.3
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Content generation failed: {str(e)}"
        )


@router.post("/generate/advanced", response_model=ContentResponse, summary="Advanced AI Content - PREMIUM+")
async def generate_advanced_content(
    request: ContentGenerationRequest,
    current_user: User = Depends(require_premium_or_higher()),  # Requires Premium or higher
    session: AsyncSession = Depends(get_db_session)
):
    """
    Generate advanced AI content with tone adjustment and SEO optimization.
    
    **Requires**: Premium, All Access, Admin, or Super Admin plan
    """
    try:
        mock_content = f"ADVANCED: {request.prompt} (tone: {request.tone}, optimized for SEO)"
        
        return ContentResponse(
            content=mock_content,
            model_used=request.ai_model,
            tokens_used=300,
            generation_time=4.1
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Advanced content generation failed: {str(e)}"
        )


@router.post("/generate/gpt4", response_model=ContentResponse, summary="GPT-4 Content Generation - PREMIUM+")
async def generate_gpt4_content(
    request: ContentGenerationRequest,
    current_user: User = Depends(require_gpt4()),  # Requires access to GPT-4 model
    session: AsyncSession = Depends(get_db_session)
):
    """
    Generate content using GPT-4 model specifically.
    
    **Requires**: Premium, All Access, Admin, or Super Admin plan with GPT-4 access
    """
    try:
        request.ai_model = "gpt-4"
        mock_content = f"GPT-4 GENERATED: High-quality content for '{request.prompt}'"
        
        return ContentResponse(
            content=mock_content,
            model_used="gpt-4",
            tokens_used=200,
            generation_time=3.8
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"GPT-4 content generation failed: {str(e)}"
        )


@router.get("/usage", response_model=UsageStatsResponse, summary="Get Usage Statistics")
async def get_usage_stats(
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_db_session)
):
    """Get current usage statistics and plan limits for the authenticated user."""
    try:
        return UsageStatsResponse(
            current_usage=current_user.get("current_usage", {}),
            limits=current_user.get("usage_limits", {}),
            plan_features=current_user.get("plan_features", {})
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get usage stats: {str(e)}"
        )


@router.post("/admin/upgrade-user/{user_id}", summary="Upgrade User Plan - ADMIN ONLY")
async def upgrade_user_plan(
    user_id: int = Path(..., description="User ID to upgrade"),
    new_plan: str = Body(..., description="New subscription plan"),
    current_user: User = Depends(require_admin_access()),  # Admin or Super Admin only
    session: AsyncSession = Depends(get_db_session)
):
    """
    Upgrade a user's subscription plan.
    
    **Requires**: Admin or Super Admin access
    """
    try:
        return JSONResponse(
            status_code=200,
            content={
                "message": f"User {user_id} upgraded to {new_plan} plan",
                "upgraded_by": current_user["username"],
                "new_plan": new_plan
            }
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Plan upgrade failed: {str(e)}"
        ) 