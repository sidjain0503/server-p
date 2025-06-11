"""
Meta-System Orchestrator

This is the central coordinator that ties together all meta-engine components:
- Schema definitions
- Dynamic model generation
- CRUD services
- API route creation

This orchestrator makes it possible to go from schema → working API in seconds.
"""

from typing import Dict, List, Optional, Type, Any
from fastapi import APIRouter, FastAPI

from app.models.base import DynamicModel
from app.meta_engine.schema_definition import SchemaDefinition
from app.meta_engine.model_factory import DynamicModelFactory
from app.meta_engine.crud_service import GenericCRUDService
from app.meta_engine.route_factory import RouteFactory, create_router_for_schema


class MetaEngineOrchestrator:
    """
    Central orchestrator for the meta-engine system.
    
    This class coordinates all components to provide a complete
    schema-to-API transformation system.
    """
    
    def __init__(self):
        self.schemas: Dict[str, SchemaDefinition] = {}
        self.models: Dict[str, Type[DynamicModel]] = {}
        self.crud_services: Dict[str, GenericCRUDService] = {}
        self.routers: Dict[str, APIRouter] = {}
        self.model_factory = DynamicModelFactory()
        self.route_factories: Dict[str, RouteFactory] = {}
    
    def register_schema(self, schema: SchemaDefinition) -> None:
        """
        Register a new schema and generate all associated components.
        
        This method:
        1. Stores the schema definition
        2. Creates a dynamic SQLAlchemy model
        3. Creates a CRUD service
        4. Generates FastAPI routes
        5. Makes everything ready for use
        
        Args:
            schema: Schema definition to register
        """
        print(f"📋 Registering schema: {schema.name}")
        
        # 1. Store schema
        self.schemas[schema.name] = schema
        
        # 2. Create dynamic model
        print(f"🏗️  Creating dynamic model for: {schema.name}")
        model = self.model_factory.create_model(schema)
        self.models[schema.name] = model
        
        # 3. Create CRUD service
        print(f"🔧 Creating CRUD service for: {schema.name}")
        crud_service = GenericCRUDService(model, schema)
        self.crud_services[schema.name] = crud_service
        
        # 4. Generate FastAPI routes using RouteFactory
        print(f"🛣️  Generating API routes for: {schema.name}")
        route_factory = RouteFactory(schema, crud_service)
        self.route_factories[schema.name] = route_factory
        self.routers[schema.name] = route_factory.router
        
        print(f"✅ Schema '{schema.name}' registered successfully!")
    
    def get_schema(self, name: str) -> Optional[SchemaDefinition]:
        """Get a registered schema by name."""
        return self.schemas.get(name)
    
    def get_model(self, name: str) -> Optional[Type[DynamicModel]]:
        """Get a dynamic model by schema name."""
        return self.models.get(name)
    
    def get_crud_service(self, name: str) -> Optional[GenericCRUDService]:
        """Get a CRUD service by schema name."""
        return self.crud_services.get(name)
    
    def get_router(self, name: str) -> Optional[APIRouter]:
        """Get a FastAPI router by schema name."""
        return self.routers.get(name)
    
    def get_all_routers(self) -> List[APIRouter]:
        """Get all registered FastAPI routers."""
        return list(self.routers.values())
    
    def register_all_routes(self, app: FastAPI) -> None:
        """
        Register all generated routes with a FastAPI application.
        
        Args:
            app: FastAPI application instance
        """
        print(f"🔗 Registering {len(self.routers)} route groups with FastAPI app")
        
        for schema_name, router in self.routers.items():
            app.include_router(router)
            print(f"   ✅ Registered routes for: {schema_name}")
        
        print("🚀 All routes registered successfully!")
    
    def list_schemas(self) -> List[str]:
        """Get a list of all registered schema names."""
        return list(self.schemas.keys())
    
    def get_schema_info(self, name: str) -> Optional[Dict[str, Any]]:
        """
        Get comprehensive information about a registered schema.
        
        Args:
            name: Schema name
            
        Returns:
            Dictionary with schema information or None if not found
        """
        schema = self.schemas.get(name)
        if not schema:
            return None
        
        model = self.models.get(name)
        
        return {
            "name": schema.name,
            "title": schema.title,
            "description": schema.description,
            "field_count": len(schema.fields),
            "fields": [
                {
                    "name": field.name,
                    "type": field.field_type.value,
                    "required": field.required,
                    "description": field.description
                }
                for field in schema.fields
            ],
            "features": {
                "timestamps": schema.enable_timestamps,
                "audit_trail": schema.enable_audit,
                "soft_delete": schema.enable_soft_delete
            },
            "table_name": model.__tablename__ if model else None,
            "endpoints": [
                f"POST /api/v1/{schema.name.lower().replace('_', '-')}/",
                f"GET /api/v1/{schema.name.lower().replace('_', '-')}/",
                f"GET /api/v1/{schema.name.lower().replace('_', '-')}/:id",
                f"PUT /api/v1/{schema.name.lower().replace('_', '-')}/:id",
                f"DELETE /api/v1/{schema.name.lower().replace('_', '-')}/:id",
                f"GET /api/v1/{schema.name.lower().replace('_', '-')}/count"
            ]
        }
    
    def get_system_stats(self) -> Dict[str, Any]:
        """Get overall system statistics."""
        total_fields = sum(len(schema.fields) for schema in self.schemas.values())
        total_endpoints = len(self.schemas) * 6  # 6 endpoints per schema
        
        return {
            "registered_schemas": len(self.schemas),
            "total_fields": total_fields,
            "generated_models": len(self.models),
            "crud_services": len(self.crud_services),
            "api_routers": len(self.routers),
            "total_endpoints": total_endpoints,
            "schemas": list(self.schemas.keys())
        }
    
    def remove_schema(self, name: str) -> bool:
        """
        Remove a schema and all its associated components.
        
        Args:
            name: Schema name to remove
            
        Returns:
            True if removed, False if not found
        """
        if name not in self.schemas:
            return False
        
        print(f"🗑️  Removing schema: {name}")
        
        # Remove all components
        del self.schemas[name]
        del self.models[name]
        del self.crud_services[name]
        del self.routers[name]
        
        print(f"✅ Schema '{name}' removed successfully!")
        return True
    
    def update_schema(self, schema: SchemaDefinition) -> None:
        """
        Update an existing schema (re-register).
        
        Args:
            schema: Updated schema definition
        """
        if schema.name in self.schemas:
            print(f"🔄 Updating existing schema: {schema.name}")
            self.remove_schema(schema.name)
        
        self.register_schema(schema)
    
    def register_custom_route(
        self, 
        schema_name: str, 
        path: str, 
        method: str, 
        handler: callable,
        **route_kwargs
    ):
        """
        Register a custom route for a specific schema.
        
        Args:
            schema_name: Name of the schema to extend
            path: Route path (e.g., "/{record_id}/publish")
            method: HTTP method ("GET", "POST", "PUT", "DELETE")
            handler: Route handler function
            **route_kwargs: Additional FastAPI route parameters
        """
        if schema_name not in self.route_factories:
            raise ValueError(f"Schema '{schema_name}' not found. Register schema first.")
        
        route_factory = self.route_factories[schema_name]
        route_factory.add_custom_route(path, method, handler, **route_kwargs)
        
        print(f"✅ Custom route registered: {method} {path} for {schema_name}")
    
    def get_schema_custom_routes(self, schema_name: str) -> dict:
        """Get all custom routes for a specific schema."""
        if schema_name not in self.route_factories:
            return {}
        return self.route_factories[schema_name].get_custom_routes()


# Global orchestrator instance
meta_engine = MetaEngineOrchestrator()


def register_schema(schema: SchemaDefinition) -> None:
    """
    Convenience function to register a schema with the global orchestrator.
    
    Args:
        schema: Schema definition to register
    """
    meta_engine.register_schema(schema)


def get_meta_engine() -> MetaEngineOrchestrator:
    """Get the global meta-engine orchestrator instance."""
    return meta_engine


def register_all_meta_routes(app: FastAPI) -> None:
    """
    Convenience function to register all meta-engine routes with FastAPI.
    
    Args:
        app: FastAPI application instance
    """
    meta_engine.register_all_routes(app) 