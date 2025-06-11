"""
SaaS Subscription Plans for InscribeVerse AI Platform

Defines subscription tiers, features, limits, and permissions for the AI SaaS platform.
"""

from typing import Dict, List, Any
from enum import Enum
from dataclasses import dataclass
from datetime import timedelta


class SubscriptionPlan(str, Enum):
    """Subscription plan types for InscribeVerse AI SaaS."""
    FREE_PLAN = "free_plan"
    PREMIUM = "premium"
    ALL_ACCESS = "all_access"
    ADMIN = "admin"
    SUPER_ADMIN = "super_admin"


class AIModel(str, Enum):
    """Available AI models for different subscription tiers."""
    GPT_3_5_TURBO = "gpt-3.5-turbo"
    GPT_4 = "gpt-4"
    GPT_4_TURBO = "gpt-4-turbo"
    CLAUDE_HAIKU = "claude-3-haiku"
    CLAUDE_SONNET = "claude-3-sonnet"
    CLAUDE_OPUS = "claude-3-opus"


class AIFeature(str, Enum):
    """AI features available in different plans."""
    CONTENT_GENERATION = "content_generation"
    SMART_DRAFTS = "smart_drafts"
    AI_EDITING = "ai_editing"
    GRAMMAR_CHECK = "grammar_check"
    TONE_ADJUSTMENT = "tone_adjustment"
    SEO_OPTIMIZATION = "seo_optimization"
    MULTI_LANGUAGE = "multi_language"
    BULK_PROCESSING = "bulk_processing"
    API_ACCESS = "api_access"
    ADVANCED_ANALYTICS = "advanced_analytics"
    CUSTOM_MODELS = "custom_models"
    PRIORITY_SUPPORT = "priority_support"


@dataclass
class PlanLimits:
    """Usage limits for a subscription plan."""
    ai_requests_per_month: int
    max_documents: int
    max_projects: int
    max_team_members: int
    storage_gb: int
    api_calls_per_minute: int
    concurrent_generations: int


@dataclass
class PlanFeatures:
    """Features and capabilities for a subscription plan."""
    ai_models: List[AIModel]
    ai_features: List[AIFeature]
    limits: PlanLimits
    permissions: List[str]
    can_upgrade: bool = True
    priority_support: bool = False
    custom_branding: bool = False
    analytics_dashboard: bool = False


# Define all subscription plans
SUBSCRIPTION_PLANS: Dict[SubscriptionPlan, PlanFeatures] = {
    
    SubscriptionPlan.FREE_PLAN: PlanFeatures(
        ai_models=[AIModel.GPT_3_5_TURBO],
        ai_features=[
            AIFeature.CONTENT_GENERATION,
            AIFeature.GRAMMAR_CHECK,
        ],
        limits=PlanLimits(
            ai_requests_per_month=100,
            max_documents=10,
            max_projects=2,
            max_team_members=1,
            storage_gb=1,
            api_calls_per_minute=10,
            concurrent_generations=1
        ),
        permissions=[
            "content:create_basic",
            "content:read",
            "profile:update"
        ],
        can_upgrade=True,
        priority_support=False,
        custom_branding=False,
        analytics_dashboard=False
    ),
    
    SubscriptionPlan.PREMIUM: PlanFeatures(
        ai_models=[AIModel.GPT_3_5_TURBO, AIModel.GPT_4, AIModel.CLAUDE_HAIKU],
        ai_features=[
            AIFeature.CONTENT_GENERATION,
            AIFeature.SMART_DRAFTS,
            AIFeature.AI_EDITING,
            AIFeature.GRAMMAR_CHECK,
            AIFeature.TONE_ADJUSTMENT,
            AIFeature.SEO_OPTIMIZATION,
        ],
        limits=PlanLimits(
            ai_requests_per_month=2000,
            max_documents=100,
            max_projects=10,
            max_team_members=5,
            storage_gb=10,
            api_calls_per_minute=50,
            concurrent_generations=3
        ),
        permissions=[
            "content:create_basic",
            "content:create_advanced",
            "content:read",
            "content:update",
            "content:delete",
            "analytics:view_basic",
            "profile:update",
            "team:invite"
        ],
        can_upgrade=True,
        priority_support=True,
        custom_branding=False,
        analytics_dashboard=True
    ),
    
    SubscriptionPlan.ALL_ACCESS: PlanFeatures(
        ai_models=[
            AIModel.GPT_3_5_TURBO, 
            AIModel.GPT_4, 
            AIModel.GPT_4_TURBO,
            AIModel.CLAUDE_HAIKU, 
            AIModel.CLAUDE_SONNET, 
            AIModel.CLAUDE_OPUS
        ],
        ai_features=[
            AIFeature.CONTENT_GENERATION,
            AIFeature.SMART_DRAFTS,
            AIFeature.AI_EDITING,
            AIFeature.GRAMMAR_CHECK,
            AIFeature.TONE_ADJUSTMENT,
            AIFeature.SEO_OPTIMIZATION,
            AIFeature.MULTI_LANGUAGE,
            AIFeature.BULK_PROCESSING,
            AIFeature.API_ACCESS,
            AIFeature.ADVANCED_ANALYTICS,
            AIFeature.CUSTOM_MODELS
        ],
        limits=PlanLimits(
            ai_requests_per_month=10000,
            max_documents=1000,
            max_projects=50,
            max_team_members=25,
            storage_gb=100,
            api_calls_per_minute=200,
            concurrent_generations=10
        ),
        permissions=[
            "content:create_basic",
            "content:create_advanced",
            "content:create_premium",
            "content:read",
            "content:update",
            "content:delete",
            "content:bulk_process",
            "analytics:view_basic",
            "analytics:view_advanced",
            "api:access",
            "models:custom",
            "profile:update",
            "team:invite",
            "team:manage"
        ],
        can_upgrade=False,
        priority_support=True,
        custom_branding=True,
        analytics_dashboard=True
    ),
    
    SubscriptionPlan.ADMIN: PlanFeatures(
        ai_models=[
            AIModel.GPT_3_5_TURBO, 
            AIModel.GPT_4, 
            AIModel.GPT_4_TURBO,
            AIModel.CLAUDE_HAIKU, 
            AIModel.CLAUDE_SONNET, 
            AIModel.CLAUDE_OPUS
        ],
        ai_features=list(AIFeature),  # All features
        limits=PlanLimits(
            ai_requests_per_month=50000,
            max_documents=5000,
            max_projects=200,
            max_team_members=100,
            storage_gb=500,
            api_calls_per_minute=500,
            concurrent_generations=25
        ),
        permissions=[
            # All user permissions
            "content:create_basic",
            "content:create_advanced", 
            "content:create_premium",
            "content:read",
            "content:update",
            "content:delete",
            "content:bulk_process",
            "analytics:view_basic",
            "analytics:view_advanced",
            "api:access",
            "models:custom",
            "profile:update",
            "team:invite",
            "team:manage",
            # Admin permissions
            "users:read",
            "users:update",
            "users:suspend",
            "billing:view",
            "support:access",
            "platform:moderate"
        ],
        can_upgrade=False,
        priority_support=True,
        custom_branding=True,
        analytics_dashboard=True
    ),
    
    SubscriptionPlan.SUPER_ADMIN: PlanFeatures(
        ai_models=list(AIModel),  # All models
        ai_features=list(AIFeature),  # All features
        limits=PlanLimits(
            ai_requests_per_month=-1,  # Unlimited
            max_documents=-1,
            max_projects=-1,
            max_team_members=-1,
            storage_gb=-1,
            api_calls_per_minute=1000,
            concurrent_generations=50
        ),
        permissions=[
            # All permissions (system admin)
            "*"  # Wildcard for all permissions
        ],
        can_upgrade=False,
        priority_support=True,
        custom_branding=True,
        analytics_dashboard=True
    )
}


def get_plan_features(plan: SubscriptionPlan) -> PlanFeatures:
    """
    Get features for a subscription plan.
    
    Args:
        plan: Subscription plan
        
    Returns:
        Plan features and limits
    """
    return SUBSCRIPTION_PLANS.get(plan, SUBSCRIPTION_PLANS[SubscriptionPlan.FREE_PLAN])


def get_user_permissions(plan: SubscriptionPlan) -> List[str]:
    """
    Get permissions for a subscription plan.
    
    Args:
        plan: Subscription plan
        
    Returns:
        List of permission strings
    """
    features = get_plan_features(plan)
    return features.permissions


def can_access_feature(plan: SubscriptionPlan, feature: AIFeature) -> bool:
    """
    Check if a plan can access a specific AI feature.
    
    Args:
        plan: User's subscription plan
        feature: AI feature to check
        
    Returns:
        True if plan has access to feature
    """
    features = get_plan_features(plan)
    return feature in features.ai_features


def can_use_model(plan: SubscriptionPlan, model: AIModel) -> bool:
    """
    Check if a plan can use a specific AI model.
    
    Args:
        plan: User's subscription plan
        model: AI model to check
        
    Returns:
        True if plan has access to model
    """
    features = get_plan_features(plan)
    return model in features.ai_models


def get_usage_limits(plan: SubscriptionPlan) -> PlanLimits:
    """
    Get usage limits for a subscription plan.
    
    Args:
        plan: Subscription plan
        
    Returns:
        Plan usage limits
    """
    features = get_plan_features(plan)
    return features.limits


def check_usage_limit(plan: SubscriptionPlan, usage_type: str, current_usage: int) -> bool:
    """
    Check if current usage is within plan limits.
    
    Args:
        plan: Subscription plan
        usage_type: Type of usage to check (ai_requests_per_month, max_documents, etc.)
        current_usage: Current usage amount
        
    Returns:
        True if within limits, False if exceeded
    """
    limits = get_usage_limits(plan)
    limit_value = getattr(limits, usage_type, 0)
    
    # -1 means unlimited
    if limit_value == -1:
        return True
    
    return current_usage < limit_value


# Plan pricing information (for reference)
PLAN_PRICING = {
    SubscriptionPlan.FREE_PLAN: {"price": 0, "currency": "USD", "billing": "monthly"},
    SubscriptionPlan.PREMIUM: {"price": 29, "currency": "USD", "billing": "monthly"},
    SubscriptionPlan.ALL_ACCESS: {"price": 99, "currency": "USD", "billing": "monthly"},
    SubscriptionPlan.ADMIN: {"price": 299, "currency": "USD", "billing": "monthly"},
    SubscriptionPlan.SUPER_ADMIN: {"price": 0, "currency": "USD", "billing": "internal"}
} 