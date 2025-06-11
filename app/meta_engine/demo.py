"""
Complete Meta-Engine System Demo

This demo showcases the full power of our meta-engine system:
- Schema definition → Working API in seconds
- Enterprise-grade features
- Complete CRUD operations
- Auto-generated documentation

Run this to see the meta-engine in action!
"""

from app.meta_engine.schema_definition import (
    SchemaDefinition, FieldDefinition, FieldType, 
    ValidationRule, PermissionLevel, CommonFields
)
from app.meta_engine.orchestrator import register_schema, get_meta_engine


def create_demo_schemas():
    """
    Create demonstration schemas for the meta-engine system.
    
    This creates realistic schemas that demonstrate all major features:
    - Different field types
    - Validation constraints
    - Choice fields
    - Enterprise features
    
    Returns:
        List of created schema definitions
    """
    print("🎯 Creating Demo Schemas for Meta-Engine System")
    print("=" * 60)
    
    # Schema 1: E-commerce Product
    print("📦 Creating E-commerce Product Schema...")
    product_schema = SchemaDefinition(
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
        enable_soft_delete=True
    )
    
    # Schema 2: Customer Management
    print("👤 Creating Customer Schema...")
    customer_schema = SchemaDefinition(
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
                default="Active",
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
        enable_soft_delete=True
    )
    
    # Schema 3: Task Management
    print("📋 Creating Task Management Schema...")
    task_schema = SchemaDefinition(
        name="Task",
        title="Task",
        description="Task and project management",
        fields=[
            FieldDefinition(
                name="title",
                field_type=FieldType.STRING,
                required=True,
                max_length=200,
                description="Task title"
            ),
            FieldDefinition(
                name="description",
                field_type=FieldType.TEXT,
                description="Detailed task description"
            ),
            FieldDefinition(
                name="priority",
                field_type=FieldType.CHOICE,
                choices=[
                    {"value": "low", "label": "Low"},
                    {"value": "medium", "label": "Medium"},
                    {"value": "high", "label": "High"},
                    {"value": "critical", "label": "Critical"}
                ],
                default="Medium",
                required=True,
                description="Task priority level"
            ),
            FieldDefinition(
                name="status",
                field_type=FieldType.CHOICE,
                choices=[
                    {"value": "todo", "label": "Todo"},
                    {"value": "in_progress", "label": "In Progress"},
                    {"value": "review", "label": "Review"},
                    {"value": "done", "label": "Done"},
                    {"value": "cancelled", "label": "Cancelled"}
                ],
                default="Todo",
                required=True,
                description="Current task status"
            ),
            FieldDefinition(
                name="due_date",
                field_type=FieldType.DATETIME,
                description="Task due date and time"
            ),
            FieldDefinition(
                name="estimated_hours",
                field_type=FieldType.FLOAT,
                min_value=0.1,
                description="Estimated hours to complete"
            ),
            FieldDefinition(
                name="labels",
                field_type=FieldType.MULTI_CHOICE,
                choices=[
                    {"value": "urgent", "label": "Urgent"},
                    {"value": "important", "label": "Important"},
                    {"value": "bug", "label": "Bug"},
                    {"value": "feature", "label": "Feature"},
                    {"value": "enhancement", "label": "Enhancement"}
                ],
                description="Task labels"
            ),
            FieldDefinition(
                name="is_urgent",
                field_type=FieldType.BOOLEAN,
                default=False,
                description="Whether task is urgent"
            )
        ],
        enable_timestamps=True,
        enable_audit=True,
        enable_soft_delete=True
    )
    
    print("\n🚀 Registering Schemas with Meta-Engine...")
    print("-" * 40)
    
    # Register all schemas
    from app.meta_engine.orchestrator import register_schema
    
    schemas = [product_schema, customer_schema, task_schema]
    for schema in schemas:
        register_schema(schema)
    
    # 🚀 NEW: Register custom routes after schemas are registered
    print("\n🎨 Registering Demo Custom Routes...")
    print("-" * 40)
    register_demo_custom_routes()
    
    print(f"\n✅ Created {len(schemas)} demo schemas with custom routes!")
    print("   📦 Product (with analytics, inventory, duplicate routes)")
    print("   👤 Customer") 
    print("   📋 Task")
    
    return schemas


def demonstrate_meta_engine():
    """Demonstrate the complete meta-engine system capabilities."""
    
    print("\n" + "=" * 80)
    print("🎉 COMPLETE META-ENGINE SYSTEM DEMONSTRATION")
    print("=" * 80)
    
    # Create and register demo schemas
    schemas = create_demo_schemas()
    
    # Get the meta-engine orchestrator
    meta_engine = get_meta_engine()
    
    # Show system statistics
    print("\n📊 Meta-Engine System Statistics:")
    print("-" * 40)
    stats = meta_engine.get_system_stats()
    for key, value in stats.items():
        print(f"   {key}: {value}")
    
    # Show detailed information for each schema
    print("\n🔍 Schema Details:")
    print("-" * 40)
    
    for schema in schemas:
        print(f"\n📋 Schema: {schema.name}")
        info = meta_engine.get_schema_info(schema.name)
        
        print(f"   Display Name: {info['title']}")
        print(f"   Description: {info['description']}")
        print(f"   Field Count: {info['field_count']}")
        print(f"   Table Name: {info['table_name']}")
        
        print(f"   Fields:")
        for field in info['fields']:
            required_marker = " (required)" if field['required'] else ""
            print(f"     - {field['name']}: {field['type']}{required_marker}")
        
        print(f"   Enterprise Features:")
        for feature, enabled in info['features'].items():
            status = "✅" if enabled else "❌"
            print(f"     {status} {feature}")
        
        print(f"   Generated API Endpoints:")
        for endpoint in info['endpoints']:
            print(f"     {endpoint}")
    
    # Show generated models information
    print("\n🏗️  Generated SQLAlchemy Models:")
    print("-" * 40)
    
    for schema_name in meta_engine.list_schemas():
        model = meta_engine.get_model(schema_name)
        print(f"   📊 {schema_name}Model")
        print(f"      Table: {model.__tablename__}")
        print(f"      Columns: {len(model.__table__.columns)}")
        
        # Show some column details
        print("      Key Columns:")
        for column in list(model.__table__.columns)[:5]:  # Show first 5 columns
            print(f"        - {column.name}: {column.type}")
        if len(model.__table__.columns) > 5:
            print(f"        ... and {len(model.__table__.columns) - 5} more")
    
    # Show CRUD services
    print("\n🔧 Generated CRUD Services:")
    print("-" * 40)
    
    for schema_name in meta_engine.list_schemas():
        crud_service = meta_engine.get_crud_service(schema_name)
        print(f"   ⚙️  {schema_name}CRUDService")
        print(f"      Model: {crud_service.model.__name__}")
        print(f"      Schema: {crud_service.schema.name}")
        print(f"      Operations: Create, Read, Update, Delete, List, Count")
    
    # Show API routers
    print("\n🛣️  Generated FastAPI Routers:")
    print("-" * 40)
    
    for schema_name in meta_engine.list_schemas():
        router = meta_engine.get_router(schema_name)
        print(f"   📡 {schema_name}Router")
        print(f"      Prefix: {router.prefix}")
        print(f"      Tags: {router.tags}")
        print(f"      Routes: {len(router.routes)}")
    
    print("\n" + "=" * 80)
    print("✅ META-ENGINE DEMONSTRATION COMPLETE!")
    print("=" * 80)
    
    print("\n🎯 What we built:")
    print("   • Schema Definition System with 15+ field types")
    print("   • Dynamic SQLAlchemy model generation")
    print("   • Universal CRUD operations")
    print("   • Auto-generated REST APIs")
    print("   • Enterprise features (audit, soft delete, etc.)")
    print("   • Complete system orchestration")
    
    print("\n🚀 Next Steps:")
    print("   • Connect to a real database")
    print("   • Add authentication system")
    print("   • Test the APIs with actual HTTP requests")
    print("   • Build a React frontend")
    print("   • Add more advanced features")
    
    print("\n💡 This is essentially a low-code platform engine!")
    print("   Similar to: Salesforce, Strapi, Supabase, or Airtable")
    
    return meta_engine


# =============================================================================
# Custom Route Registration for Demo
# =============================================================================
def register_demo_custom_routes():
    """Register some demo custom routes to show the capability."""
    from app.meta_engine.orchestrator import get_meta_engine
    from fastapi import HTTPException, Depends, Path, Body
    from fastapi.responses import JSONResponse
    from sqlalchemy.ext.asyncio import AsyncSession
    from pydantic import BaseModel
    from app.core.database import get_db_session
    
    # Custom request/response models
    class ProductAnalyticsResponse(BaseModel):
        product_id: int
        total_views: int
        total_sales: int
        popularity_score: float
        trending: bool
        
    class InventoryUpdateRequest(BaseModel):
        quantity_change: int
        reason: str = "manual_adjustment"
    
    # Custom route handlers
    async def get_product_analytics(
        product_id: int = Path(..., description="Product ID"),
        session: AsyncSession = Depends(get_db_session)
    ):
        """Get analytics data for a product."""
        try:
            meta_engine = get_meta_engine()
            crud_service = meta_engine.get_crud_service("Product")
            
            product = await crud_service.get(session, product_id)
            if not product:
                raise HTTPException(status_code=404, detail="Product not found")
            
            # Mock analytics data
            return ProductAnalyticsResponse(
                product_id=product_id,
                total_views=1250,
                total_sales=87,
                popularity_score=8.5,
                trending=True
            )
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))
    
    async def update_inventory(
        product_id: int = Path(..., description="Product ID"),
        request: InventoryUpdateRequest = Body(...),
        session: AsyncSession = Depends(get_db_session)
    ):
        """Update product inventory with tracking."""
        try:
            meta_engine = get_meta_engine()
            crud_service = meta_engine.get_crud_service("Product")
            
            product = await crud_service.get(session, product_id)
            if not product:
                raise HTTPException(status_code=404, detail="Product not found")
            
            # Update stock quantity
            new_quantity = product.stock_quantity + request.quantity_change
            if new_quantity < 0:
                raise HTTPException(status_code=400, detail="Insufficient inventory")
            
            await crud_service.update(session, product_id, {
                "stock_quantity": new_quantity,
                "in_stock": new_quantity > 0
            })
            
            return JSONResponse(
                status_code=200,
                content={
                    "message": "Inventory updated successfully",
                    "old_quantity": product.stock_quantity,
                    "new_quantity": new_quantity,
                    "change": request.quantity_change,
                    "reason": request.reason
                }
            )
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))
    
    async def duplicate_product(
        product_id: int = Path(..., description="Product ID to duplicate"),
        session: AsyncSession = Depends(get_db_session)
    ):
        """Create a duplicate product for A/B testing."""
        try:
            meta_engine = get_meta_engine()
            crud_service = meta_engine.get_crud_service("Product")
            
            original = await crud_service.get(session, product_id)
            if not original:
                raise HTTPException(status_code=404, detail="Product not found")
            
            # Create duplicate with modified data
            duplicate_data = {
                "name": f"{original.name} (Copy)",
                "description": original.description,
                "price": original.price,
                "category": original.category,
                "tags": original.tags,
                "in_stock": False,  # Start as out of stock
                "stock_quantity": 0,
                "image_url": original.image_url
            }
            
            new_product = await crud_service.create(session, duplicate_data)
            
            return JSONResponse(
                status_code=201,
                content={
                    "message": "Product duplicated successfully",
                    "original_id": product_id,
                    "new_id": new_product.id,
                    "new_name": duplicate_data["name"]
                }
            )
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))
    
    # Register the custom routes
    meta_engine = get_meta_engine()
    
    print("🎨 Registering demo custom routes for Product schema...")
    
    # Product Analytics
    meta_engine.register_custom_route(
        schema_name="Product",
        path="/{product_id}/analytics",
        method="GET",
        handler=get_product_analytics,
        summary="Get Product Analytics",
        description="Get detailed analytics and performance metrics for a product"
    )
    
    # Inventory Management
    meta_engine.register_custom_route(
        schema_name="Product",
        path="/{product_id}/inventory",
        method="PUT",
        handler=update_inventory,
        summary="Update Product Inventory",
        description="Update product inventory with quantity changes and tracking"
    )
    
    # Product Duplication
    meta_engine.register_custom_route(
        schema_name="Product",
        path="/{product_id}/duplicate",
        method="POST",
        handler=duplicate_product,
        summary="Duplicate Product",
        description="Create a copy of a product for A/B testing or variations"
    )
    
    print("✅ Demo custom routes registered!")
    print("   📊 GET  /api/v1/product/{id}/analytics")
    print("   📦 PUT  /api/v1/product/{id}/inventory")
    print("   📋 POST /api/v1/product/{id}/duplicate")


# =============================================================================
# Updated Demo Function
# =============================================================================


if __name__ == "__main__":
    # Run the complete demonstration
    demonstrate_meta_engine() 