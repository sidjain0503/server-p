"""
Schema Definition System

This module provides a powerful way to define data schemas that can be converted
into SQLAlchemy models, Pydantic models, and FastAPI routes automatically.
"""

from enum import Enum
from typing import Any, Dict, List, Optional, Union
from datetime import datetime
from pydantic import BaseModel, Field, validator
from dataclasses import field


class FieldType(str, Enum):
    """Supported field types for schema definitions."""
    
    # Basic Types
    STRING = "string"
    TEXT = "text"
    INTEGER = "integer"
    FLOAT = "float"
    BOOLEAN = "boolean"
    
    # Date/Time Types
    DATE = "date"
    DATETIME = "datetime"
    TIME = "time"
    
    # Special Types
    EMAIL = "email"
    URL = "url"
    UUID = "uuid"
    JSON = "json"
    
    # File Types
    FILE = "file"
    IMAGE = "image"
    
    # Numeric Types
    DECIMAL = "decimal"
    CURRENCY = "currency"
    
    # Selection Types
    CHOICE = "choice"
    MULTI_CHOICE = "multi_choice"


class RelationshipType(str, Enum):
    """Types of relationships between models."""
    
    ONE_TO_ONE = "one_to_one"
    ONE_TO_MANY = "one_to_many" 
    MANY_TO_ONE = "many_to_one"
    MANY_TO_MANY = "many_to_many"


class PermissionLevel(str, Enum):
    """Permission levels for field access."""
    
    PUBLIC = "public"          # Anyone can read/write
    READ_ONLY = "read_only"    # Anyone can read, only admin can write
    ADMIN_ONLY = "admin_only"  # Only admin can read/write
    OWNER_ONLY = "owner_only"  # Only the owner can read/write
    PRIVATE = "private"        # Only system can access


class ValidationRule(BaseModel):
    """Defines validation rules for fields."""
    
    rule_type: str = Field(..., description="Type of validation rule")
    value: Any = Field(..., description="Value for the validation rule")
    message: Optional[str] = Field(None, description="Custom error message")
    
    class Config:
        extra = "allow"


class FieldDefinition(BaseModel):
    """Defines a single field in a schema."""
    
    name: str = Field(..., description="Field name")
    field_type: FieldType = Field(..., description="Type of the field")
    label: Optional[str] = Field(None, description="Human-readable label")
    description: Optional[str] = Field(None, description="Field description")
    
    # Constraints
    required: bool = Field(default=False, description="Is field required")
    unique: bool = Field(default=False, description="Is field unique")
    indexed: bool = Field(default=False, description="Should field be indexed")
    
    # Default values
    default: Optional[Any] = Field(None, description="Default value")
    auto_generate: bool = Field(default=False, description="Auto-generate value")
    
    # String/Text constraints
    min_length: Optional[int] = Field(None, description="Minimum string length")
    max_length: Optional[int] = Field(None, description="Maximum string length")
    
    # Numeric constraints
    min_value: Optional[Union[int, float]] = Field(None, description="Minimum numeric value")
    max_value: Optional[Union[int, float]] = Field(None, description="Maximum numeric value")
    
    # Choice fields
    choices: Optional[List[Dict[str, Any]]] = Field(None, description="Available choices")
    
    # Relationships
    relationship_type: Optional[RelationshipType] = Field(None, description="Type of relationship")
    related_schema: Optional[str] = Field(None, description="Name of related schema")
    foreign_key: Optional[str] = Field(None, description="Foreign key field")
    
    # Permissions
    permission_level: PermissionLevel = Field(default=PermissionLevel.PUBLIC, description="Access level")
    
    # Validation
    validation_rules: List[ValidationRule] = Field(default_factory=list, description="Custom validation rules")
    
    # UI hints
    widget_type: Optional[str] = Field(None, description="UI widget type")
    placeholder: Optional[str] = Field(None, description="Placeholder text")
    help_text: Optional[str] = Field(None, description="Help text for users")
    
    @validator("choices")
    def validate_choices(cls, v, values):
        """Validate that choices are provided for choice fields."""
        if values.get("field_type") in [FieldType.CHOICE, FieldType.MULTI_CHOICE]:
            if not v:
                raise ValueError("Choices must be provided for choice fields")
        return v
    
    @validator("related_schema")
    def validate_relationship_schema(cls, v, values):
        """Validate that related_schema is provided for relationship fields."""
        if values.get("relationship_type") and not v:
            raise ValueError("related_schema must be provided for relationship fields")
        return v


class SchemaDefinition(BaseModel):
    """Defines a complete data schema that can be converted to models and APIs."""
    
    # Basic Information
    name: str = Field(..., description="Schema name (will be used for table/model name)")
    version: str = Field(default="1.0.0", description="Schema version")
    title: Optional[str] = Field(None, description="Human-readable title")
    description: Optional[str] = Field(None, description="Schema description")
    
    # Fields
    fields: List[FieldDefinition] = Field(..., description="List of field definitions")
    
    # Table Configuration
    table_name: Optional[str] = Field(None, description="Custom table name")
    plural_name: Optional[str] = Field(None, description="Plural form for API endpoints")
    
    # Features
    enable_audit: bool = Field(default=True, description="Enable audit trail")
    enable_soft_delete: bool = Field(default=True, description="Enable soft delete")
    enable_timestamps: bool = Field(default=True, description="Enable created/updated timestamps")
    enable_versioning: bool = Field(default=False, description="Enable record versioning")
    
    # Authentication configuration
    auth_config: Dict[str, Any] = Field(default_factory=lambda: {
        "require_auth": True,  # By default, require authentication
        "public_routes": [],   # List of routes that should be public: ["list", "get", "count"]
        "protected_routes": [], # List of routes that should be protected (overrides require_auth=False)
        "read_public": False,  # Make read operations (GET) public
        "write_protected": True,  # Always protect write operations (POST, PUT, DELETE)
    }, description="Authentication configuration for generated routes")
    
    # Metadata
    tags: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    # Features
    enable_crud_api: bool = Field(default=True, description="Generate CRUD API endpoints")
    enable_search_api: bool = Field(default=True, description="Generate search endpoints")
    enable_bulk_api: bool = Field(default=True, description="Generate bulk operation endpoints")
    
    # Permissions
    default_permission: PermissionLevel = Field(default=PermissionLevel.PUBLIC, description="Default permission level")
    permission_fields: Optional[List[str]] = Field(None, description="Fields that control permissions")
    
    # Metadata
    category: Optional[str] = Field(None, description="Schema category")
    icon: Optional[str] = Field(None, description="Icon for UI")
    color: Optional[str] = Field(None, description="Color theme for UI")
    
    # System fields (auto-managed)
    created_at: Optional[datetime] = Field(None, description="When schema was created")
    updated_at: Optional[datetime] = Field(None, description="When schema was last updated")
    created_by: Optional[str] = Field(None, description="Who created the schema")
    is_system: bool = Field(default=False, description="Is this a system schema")
    
    @validator("name")
    def validate_name(cls, v):
        """Validate schema name follows conventions."""
        if not v.isidentifier():
            raise ValueError("Schema name must be a valid Python identifier")
        if v.startswith("_"):
            raise ValueError("Schema name cannot start with underscore")
        return v
    
    @validator("fields")
    def validate_fields(cls, v):
        """Validate field definitions."""
        if not v:
            raise ValueError("Schema must have at least one field")
        
        field_names = [field.name for field in v]
        if len(field_names) != len(set(field_names)):
            raise ValueError("Field names must be unique")
        
        # Check for reserved field names
        reserved_names = ["id", "created_at", "updated_at", "is_deleted", "deleted_at"]
        for field in v:
            if field.name in reserved_names:
                raise ValueError(f"Field name '{field.name}' is reserved")
        
        return v
    
    @property
    def model_name(self) -> str:
        """Get the model class name."""
        return f"Dynamic{self.name.title()}"
    
    @property
    def api_prefix(self) -> str:
        """Get the API prefix for this schema."""
        return self.plural_name or f"{self.name.lower()}s"
    
    def get_field(self, name: str) -> Optional[FieldDefinition]:
        """Get a field by name."""
        for field in self.fields:
            if field.name == name:
                return field
        return None
    
    def get_required_fields(self) -> List[FieldDefinition]:
        """Get all required fields."""
        return [field for field in self.fields if field.required]
    
    def get_unique_fields(self) -> List[FieldDefinition]:
        """Get all unique fields."""
        return [field for field in self.fields if field.unique]
    
    def get_relationship_fields(self) -> List[FieldDefinition]:
        """Get all relationship fields."""
        return [field for field in self.fields if field.relationship_type]
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for storage."""
        return self.dict()
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "SchemaDefinition":
        """Create from dictionary."""
        return cls(**data)


# Predefined common field definitions for quick schema creation
class CommonFields:
    """Common field definitions that can be reused across schemas."""
    
    @staticmethod
    def id_field() -> FieldDefinition:
        """Standard ID field."""
        return FieldDefinition(
            name="id",
            field_type=FieldType.INTEGER,
            label="ID",
            description="Unique identifier",
            required=True,
            unique=True,
            auto_generate=True
        )
    
    @staticmethod
    def name_field() -> FieldDefinition:
        """Standard name field."""
        return FieldDefinition(
            name="name",
            field_type=FieldType.STRING,
            label="Name",
            description="Name of the item",
            required=True,
            max_length=255,
            indexed=True
        )
    
    @staticmethod
    def email_field() -> FieldDefinition:
        """Standard email field."""
        return FieldDefinition(
            name="email",
            field_type=FieldType.EMAIL,
            label="Email",
            description="Email address",
            required=True,
            unique=True,
            indexed=True
        )
    
    @staticmethod
    def status_field() -> FieldDefinition:
        """Standard status field."""
        return FieldDefinition(
            name="status",
            field_type=FieldType.CHOICE,
            label="Status",
            description="Current status",
            choices=[
                {"value": "active", "label": "Active"},
                {"value": "inactive", "label": "Inactive"},
                {"value": "pending", "label": "Pending"}
            ],
            default="active",
            indexed=True
        )
    
    @staticmethod
    def description_field() -> FieldDefinition:
        """Standard description field."""
        return FieldDefinition(
            name="description",
            field_type=FieldType.TEXT,
            label="Description",
            description="Detailed description",
            required=False
        ) 