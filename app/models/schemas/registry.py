"""
Schema Registry

This module handles the registration of all schemas with the meta-engine system.
It provides a centralized way to register and manage all schema definitions.
"""

from typing import List
from app.meta_engine.orchestrator import register_schema, get_meta_engine
from app.meta_engine.schema_definition import SchemaDefinition

from .product_schema import get_product_schema
from .customer_schema import get_customer_schema
from .task_schema import get_task_schema
from .auth_schemas import AUTH_SCHEMAS


def get_all_schemas() -> List[SchemaDefinition]:
    """
    Get all available schema definitions.
    
    Returns:
        List[SchemaDefinition]: List of all schema definitions
    """
    # Business domain schemas
    business_schemas = [
        get_product_schema(),
        get_customer_schema(),
        get_task_schema()
    ]
    
    # Combine business and auth schemas
    return business_schemas + AUTH_SCHEMAS


def register_all_schemas() -> None:
    """
    Register all schemas with the meta-engine system.
    
    This function registers all available schemas and sets up the complete
    API structure for the application.
    """
    print("🚀 Registering all schemas with Meta-Engine...")
    print("-" * 50)
    
    schemas = get_all_schemas()
    
    for schema in schemas:
        print(f"📋 Registering schema: {schema.name}")
        register_schema(schema)
    
    print(f"\n✅ Successfully registered {len(schemas)} schemas!")
    
    # Show system statistics
    meta_engine = get_meta_engine()
    stats = meta_engine.get_system_stats()
    
    print("\n📊 Meta-Engine System Statistics:")
    print("-" * 30)
    for key, value in stats.items():
        print(f"   {key}: {value}")


def get_schema_list() -> List[str]:
    """
    Get a list of all available schema names.
    
    Returns:
        List[str]: List of schema names
    """
    return [schema.name for schema in get_all_schemas()]


def get_schema_by_name(name: str) -> SchemaDefinition:
    """
    Get a specific schema by name.
    
    Args:
        name: Schema name to retrieve
        
    Returns:
        SchemaDefinition: The requested schema definition
        
    Raises:
        ValueError: If schema with given name is not found
    """
    schemas = get_all_schemas()
    
    for schema in schemas:
        if schema.name.lower() == name.lower():
            return schema
    
    raise ValueError(f"Schema '{name}' not found. Available schemas: {get_schema_list()}")


if __name__ == "__main__":
    # Allow this module to be run directly for testing
    register_all_schemas() 