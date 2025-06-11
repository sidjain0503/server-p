"""
Authentication schemas for InscribeVerse Meta-Engine

OAuth-ready architecture that starts with email/password but can scale
to Google, LinkedIn, GitHub, etc. without breaking changes.
"""

from app.meta_engine.schema_definition import (
    SchemaDefinition, FieldDefinition, FieldType, 
    ValidationRule, PermissionLevel, CommonFields
)

def get_user_schema() -> SchemaDefinition:
    """
    Get the User schema definition for AI SaaS platform.
    
    Users with subscription-based access control for AI features.
    """
    return SchemaDefinition(
        name="User",
        title="User", 
        description="AI SaaS platform users with subscription-based access",
        fields=[
            FieldDefinition(
                name="email",
                field_type=FieldType.EMAIL,
                required=True,
                unique=True,
                description="User email address"
            ),
            FieldDefinition(
                name="username", 
                field_type=FieldType.STRING,
                required=True,
                unique=True,
                max_length=50,
                description="Unique username"
            ),
            FieldDefinition(
                name="display_name",
                field_type=FieldType.STRING,
                max_length=100,
                description="User display name"
            ),
            FieldDefinition(
                name="avatar_url",
                field_type=FieldType.URL,
                description="User avatar image URL"
            ),
            FieldDefinition(
                name="is_active",
                field_type=FieldType.BOOLEAN,
                default=True,
                description="Whether the user account is active"
            ),
            FieldDefinition(
                name="is_superuser",
                field_type=FieldType.BOOLEAN,
                default=False,
                description="Whether the user has admin privileges"
            ),
            FieldDefinition(
                name="email_verified",
                field_type=FieldType.BOOLEAN,
                default=False,
                description="Whether the user's email is verified"
            ),
            FieldDefinition(
                name="last_login",
                field_type=FieldType.DATETIME,
                description="Last login timestamp"
            ),
            # SaaS Subscription Fields
            FieldDefinition(
                name="subscription_plan",
                field_type=FieldType.CHOICE,
                choices=[
                    {"value": "free_plan", "label": "Free Plan"},
                    {"value": "premium", "label": "Premium Plan"},
                    {"value": "all_access", "label": "All Access Plan"},
                    {"value": "admin", "label": "Admin"},
                    {"value": "super_admin", "label": "Super Admin"}
                ],
                default="free_plan",
                required=True,
                description="User subscription plan/role"
            ),
            FieldDefinition(
                name="subscription_status",
                field_type=FieldType.CHOICE,
                choices=[
                    {"value": "active", "label": "Active"},
                    {"value": "expired", "label": "Expired"},
                    {"value": "cancelled", "label": "Cancelled"},
                    {"value": "trial", "label": "Trial"},
                    {"value": "suspended", "label": "Suspended"}
                ],
                default="active",
                required=True,
                description="Subscription status"
            ),
            FieldDefinition(
                name="subscription_expires_at",
                field_type=FieldType.DATETIME,
                description="When subscription expires"
            ),
            FieldDefinition(
                name="trial_ends_at",
                field_type=FieldType.DATETIME,
                description="When trial period ends"
            ),
            # AI Usage Tracking
            FieldDefinition(
                name="ai_requests_used",
                field_type=FieldType.INTEGER,
                default=0,
                min_value=0,
                description="AI requests used this billing period"
            ),
            FieldDefinition(
                name="ai_requests_limit",
                field_type=FieldType.INTEGER,
                default=100,
                min_value=0,
                description="AI requests limit for current plan"
            ),
            FieldDefinition(
                name="billing_cycle_start",
                field_type=FieldType.DATETIME,
                description="Start of current billing cycle"
            ),
            FieldDefinition(
                name="preferences",
                field_type=FieldType.JSON,
                description="User preferences and settings"
            )
        ],
        enable_timestamps=True,
        enable_audit=True,
        enable_soft_delete=True
    )

# Authentication methods - supports multiple auth providers per user
auth_method_schema = SchemaDefinition(
    name="AuthMethod",
    title="Authentication Method",
    description="Authentication provider methods linked to users (password, Google, LinkedIn, etc.)",
    fields=[
        FieldDefinition(
            name="user_id",
            field_type=FieldType.INTEGER,
            required=True,
            description="ID of the user this auth method belongs to"
        ),
        FieldDefinition(
            name="provider",
            field_type=FieldType.STRING,
            required=True,
            max_length=50,
            description="Authentication provider (local, google, linkedin, github, etc.)"
        ),
        FieldDefinition(
            name="provider_user_id",
            field_type=FieldType.STRING,
            required=False,
            max_length=200,
            description="User ID from the external provider"
        ),
        FieldDefinition(
            name="provider_email",
            field_type=FieldType.EMAIL,
            required=False,
            description="Email address from the external provider"
        ),
        FieldDefinition(
            name="password_hash",
            field_type=FieldType.STRING,
            required=False,
            max_length=255,
            description="Hashed password (only for local authentication)"
        ),
        FieldDefinition(
            name="access_token",
            field_type=FieldType.TEXT,
            required=False,
            description="Encrypted OAuth access token"
        ),
        FieldDefinition(
            name="refresh_token",
            field_type=FieldType.TEXT,
            required=False,
            description="Encrypted OAuth refresh token"
        ),
        FieldDefinition(
            name="provider_data",
            field_type=FieldType.JSON,
            required=False,
            description="Additional data from the auth provider"
        ),
        FieldDefinition(
            name="last_used",
            field_type=FieldType.DATETIME,
            required=False,
            description="When this auth method was last used"
        ),
        FieldDefinition(
            name="is_primary",
            field_type=FieldType.BOOLEAN,
            required=True,
            default=True,
            description="Whether this is the primary auth method for the user"
        ),
    ]
)

# Role schema for RBAC (future expansion)
role_schema = SchemaDefinition(
    name="Role",
    title="User Role",
    description="User roles for role-based access control",
    fields=[
        FieldDefinition(
            name="name",
            field_type=FieldType.STRING,
            required=True,
            unique=True,
            max_length=50,
            description="Role name (admin, manager, user, etc.)"
        ),
        FieldDefinition(
            name="description",
            field_type=FieldType.TEXT,
            required=False,
            description="Description of the role and its permissions"
        ),
        FieldDefinition(
            name="permissions",
            field_type=FieldType.JSON,
            required=True,
            default=[],
            description="List of permission strings for this role"
        ),
        FieldDefinition(
            name="is_default",
            field_type=FieldType.BOOLEAN,
            required=True,
            default=False,
            description="Whether this role is assigned to new users by default"
        ),
    ]
)

# User-Role relationship (many-to-many)
user_role_schema = SchemaDefinition(
    name="UserRole",
    title="User Role Assignment",
    description="Assignment of roles to users",
    fields=[
        FieldDefinition(
            name="user_id",
            field_type=FieldType.INTEGER,
            required=True,
            description="ID of the user"
        ),
        FieldDefinition(
            name="role_id",
            field_type=FieldType.INTEGER,
            required=True,
            description="ID of the role"
        ),
        FieldDefinition(
            name="assigned_by",
            field_type=FieldType.INTEGER,
            required=False,
            description="ID of the user who assigned this role"
        ),
        FieldDefinition(
            name="assigned_at",
            field_type=FieldType.DATETIME,
            required=True,
            description="When this role was assigned"
        ),
    ]
)

# Export schemas for registration
AUTH_SCHEMAS = [
    get_user_schema(),
    auth_method_schema,
    role_schema,
    user_role_schema,
] 