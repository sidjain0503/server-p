"""
Customer Schema Definition

Customer management schema with comprehensive field definitions
for customer relationship management (CRM) functionality.
"""

from app.meta_engine.schema_definition import (
    SchemaDefinition, FieldDefinition, FieldType, 
    ValidationRule, PermissionLevel, CommonFields
)


def get_customer_schema() -> SchemaDefinition:
    """
    Get the Customer schema definition.
    
    This schema represents a customer with all necessary fields
    for customer management, loyalty tracking, and communication.
    
    Returns:
        SchemaDefinition: Complete customer schema definition
    """
    return SchemaDefinition(
        name="Customer",
        title="Customer",
        description="Customer management system",
        fields=[
            FieldDefinition(
                name="first_name",
                field_type=FieldType.STRING,
                required=True,
                max_length=50,
                description="Customer first name"
            ),
            FieldDefinition(
                name="last_name",
                field_type=FieldType.STRING,
                required=True,
                max_length=50,
                description="Customer last name"
            ),
            FieldDefinition(
                name="email",
                field_type=FieldType.EMAIL,
                required=True,
                description="Customer email address"
            ),
            FieldDefinition(
                name="phone",
                field_type=FieldType.STRING,
                max_length=20,
                description="Customer phone number"
            ),
            FieldDefinition(
                name="date_of_birth",
                field_type=FieldType.DATE,
                description="Customer date of birth"
            ),
            FieldDefinition(
                name="status",
                field_type=FieldType.CHOICE,
                choices=[
                    {"value": "active", "label": "Active"},
                    {"value": "inactive", "label": "Inactive"},
                    {"value": "pending", "label": "Pending"},
                    {"value": "suspended", "label": "Suspended"}
                ],
                default="active",
                required=True,
                description="Customer status"
            ),
            FieldDefinition(
                name="loyalty_points",
                field_type=FieldType.INTEGER,
                min_value=0,
                default=0,
                description="Customer loyalty points"
            ),
            FieldDefinition(
                name="preferences",
                field_type=FieldType.JSON,
                description="Customer preferences as JSON"
            )
        ],
        enable_timestamps=True,
        enable_audit=True,
        enable_soft_delete=True,
        
        # Authentication configuration: All customer operations require authentication (sensitive data)
        auth_config={
            "require_auth": True,
            "read_public": False,  # Customer data is private
            "write_protected": True,  # All write operations require auth
        }
    ) 