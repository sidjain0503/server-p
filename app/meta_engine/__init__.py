"""
Meta-Engine Package

This package contains the core meta-system that can:
- Define schemas dynamically
- Generate SQLAlchemy models from schemas
- Create FastAPI routes automatically
- Provide generic CRUD operations
- Handle permissions and validation
"""

from app.meta_engine.schema_definition import (
    SchemaDefinition,
    FieldDefinition,
    FieldType,
    RelationshipType,
    PermissionLevel
)

from app.meta_engine.model_factory import DynamicModelFactory
from app.meta_engine.crud_service import GenericCRUDService
from app.meta_engine.route_factory import DynamicRouteFactory
from app.meta_engine.meta_orchestrator import MetaOrchestrator

__all__ = [
    "SchemaDefinition",
    "FieldDefinition", 
    "FieldType",
    "RelationshipType",
    "PermissionLevel",
    "DynamicModelFactory",
    "GenericCRUDService",
    "DynamicRouteFactory",
    "MetaOrchestrator",
] 