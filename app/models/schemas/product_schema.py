"""
Product Schema Definition

E-commerce product catalog schema with comprehensive field definitions,
validation rules, and enterprise features.
"""

from app.meta_engine.schema_definition import (
    SchemaDefinition, FieldDefinition, FieldType, 
    ValidationRule, PermissionLevel, CommonFields
)


def get_product_schema() -> SchemaDefinition:
    """
    Get the Product schema definition.
    
    This schema represents an e-commerce product with all necessary fields
    for inventory management, pricing, categorization, and more.
    
    Returns:
        SchemaDefinition: Complete product schema definition
    """
    return SchemaDefinition(
        name="Product",
        title="Product",
        description="E-commerce product catalog",
        fields=[
            FieldDefinition(
                name="name",
                field_type=FieldType.STRING,
                required=True,
                max_length=200,
                description="Product name"
            ),
            FieldDefinition(
                name="description",
                field_type=FieldType.TEXT,
                description="Product description"
            ),
            FieldDefinition(
                name="price",
                field_type=FieldType.CURRENCY,
                required=True,
                min_value=0.01,
                description="Product price in USD"
            ),
            FieldDefinition(
                name="category",
                field_type=FieldType.CHOICE,
                choices=[
                    {"value": "electronics", "label": "Electronics"},
                    {"value": "clothing", "label": "Clothing"},
                    {"value": "books", "label": "Books"},
                    {"value": "home", "label": "Home"},
                    {"value": "sports", "label": "Sports"}
                ],
                required=True,
                description="Product category"
            ),
            FieldDefinition(
                name="tags",
                field_type=FieldType.MULTI_CHOICE,
                choices=[
                    {"value": "new", "label": "New"},
                    {"value": "sale", "label": "Sale"},
                    {"value": "popular", "label": "Popular"},
                    {"value": "limited", "label": "Limited"},
                    {"value": "featured", "label": "Featured"}
                ],
                description="Product tags"
            ),
            FieldDefinition(
                name="in_stock",
                field_type=FieldType.BOOLEAN,
                default=True,
                description="Whether product is in stock"
            ),
            FieldDefinition(
                name="stock_quantity",
                field_type=FieldType.INTEGER,
                min_value=0,
                default=0,
                description="Available stock quantity"
            ),
            FieldDefinition(
                name="image_url",
                field_type=FieldType.URL,
                description="Product image URL"
            )
        ],
        enable_timestamps=True,
        enable_audit=True,
        enable_soft_delete=True,
        
        # Authentication configuration: Public product catalog with protected admin operations
        auth_config={
            "require_auth": True,
            "read_public": True,  # Anyone can browse the product catalog
            "write_protected": True,  # Only authenticated users can create/update/delete products
        }
    ) 