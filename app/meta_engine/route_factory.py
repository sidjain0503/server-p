"""
Dynamic Route Factory

This module automatically generates FastAPI routes for any schema definition.
It creates complete REST APIs with validation, documentation, and error handling.
"""

from typing import Any, Dict, List, Optional, Type, Callable
from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, Query, Path, Body
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field, create_model
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db_session
from app.models.base import DynamicModel
from app.meta_engine.schema_definition import SchemaDefinition, FieldDefinition, FieldType
from app.meta_engine.crud_service import GenericCRUDService, QueryParams, CRUDException
from app.services.security import get_current_user, User


def get_optional_user() -> Optional[User]:
    """Dummy dependency that returns None for public routes."""
    return None


class RouteFactory:
    """
    Factory for creating FastAPI routes from schema definitions.
    
    This factory generates standard CRUD routes and supports custom route extensions.
    Respects schema auth_config for flexible public/protected routes.
    """
    
    def __init__(self, schema: SchemaDefinition, crud_service: GenericCRUDService):
        self.schema = schema
        self.crud_service = crud_service
        self.router = APIRouter()
        
        # Store for custom routes
        self.custom_routes = {}
        
        # Generate standard CRUD routes
        self._create_crud_routes()
    
    def add_custom_route(
        self,
        path: str,
        method: str,
        handler: callable,
        **route_kwargs
    ):
        """
        Add a custom route to this schema's router.
        
        Args:
            path: Route path (e.g., "/{record_id}/publish")
            method: HTTP method ("GET", "POST", "PUT", "DELETE")
            handler: Route handler function
            **route_kwargs: Additional FastAPI route parameters
        """
        route_decorator = getattr(self.router, method.lower())
        route_decorator(path, **route_kwargs)(handler)
        
        # Store for reference
        self.custom_routes[f"{method} {path}"] = handler
        
        print(f"🔧 Added custom route: {method} {path} to {self.schema.name}")
    
    def get_custom_routes(self) -> dict:
        """Get all registered custom routes."""
        return self.custom_routes
    
    def _create_crud_routes(self):
        """Create all CRUD routes for the schema."""
        self._add_create_route()
        self._add_list_route()
        self._add_get_route()
        self._add_update_route()
        self._add_delete_route()
        self._add_count_route()
    
    def _add_create_route(self):
        """Add POST route for creating new records."""
        
        @self.router.post(
            "/",
            response_model=self._create_response_model(),
            status_code=201,
            summary=f"Create {self.schema.title or self.schema.name}",
            description=f"Create a new {self.schema.title or self.schema.name} record"
        )
        async def create_record(
            data: self._create_request_model(),
            session: AsyncSession = Depends(get_db_session),
            current_user: Optional[User] = self._get_auth_dependency("create")
        ):
            try:
                # Convert Pydantic model to dict
                record_data = data.dict(exclude_unset=True)
                
                # Create record using CRUD service
                instance = await self.crud_service.create(
                    session=session,
                    data=record_data,
                    created_by_id=current_user["id"] if current_user else None
                )
                
                return self._model_to_response(instance)
                
            except CRUDException as e:
                raise HTTPException(status_code=400, detail=str(e))
            except Exception as e:
                raise HTTPException(status_code=500, detail="Internal server error")
    
    def _add_list_route(self):
        """Add GET route for listing records with filtering and pagination."""
        
        @self.router.get(
            "/",
            response_model=self._create_list_response_model(),
            summary=f"List {self.schema.title or self.schema.name} records",
            description=f"Get a paginated list of {self.schema.title or self.schema.name} records with optional filtering and search"
        )
        async def list_records(
            # Pagination
            skip: int = Query(0, ge=0, description="Number of records to skip"),
            limit: int = Query(100, ge=1, le=1000, description="Maximum number of records to return"),
            
            # Sorting
            order_by: Optional[str] = Query(None, description="Field to sort by"),
            order_desc: bool = Query(False, description="Sort in descending order"),
            
            # Search
            search: Optional[str] = Query(None, description="Search term"),
            search_fields: Optional[str] = Query(None, description="Comma-separated list of fields to search in"),
            
            session: AsyncSession = Depends(get_db_session),
            current_user: Optional[User] = self._get_auth_dependency("list")
        ):
            try:
                # Build query parameters
                params = QueryParams(
                    skip=skip,
                    limit=limit,
                    order_by=order_by,
                    order_desc=order_desc,
                    search=search,
                    search_fields=search_fields.split(",") if search_fields else None,
                    filters={}  # TODO: Implement dynamic filtering
                )
                
                # Get records and count
                records = await self.crud_service.list(
                    session=session,
                    params=params,
                    user_id=current_user["id"] if current_user else None
                )
                
                total = await self.crud_service.count(
                    session=session,
                    params=params,
                    user_id=current_user["id"] if current_user else None
                )
                
                return {
                    "items": [self._model_to_response(record) for record in records],
                    "total": total,
                    "skip": skip,
                    "limit": limit,
                    "has_next": skip + limit < total
                }
                
            except CRUDException as e:
                raise HTTPException(status_code=400, detail=str(e))
            except Exception as e:
                raise HTTPException(status_code=500, detail="Internal server error")
    
    def _add_get_route(self):
        """Add GET route for retrieving a single record by ID."""
        
        @self.router.get(
            "/{record_id}",
            response_model=self._create_response_model(),
            summary=f"Get {self.schema.title or self.schema.name}",
            description=f"Get a single {self.schema.title or self.schema.name} record by ID"
        )
        async def get_record(
            record_id: int = Path(..., description="Record ID"),
            session: AsyncSession = Depends(get_db_session),
            current_user: Optional[User] = self._get_auth_dependency("get")
        ):
            try:
                instance = await self.crud_service.get(
                    session=session,
                    record_id=record_id,
                    user_id=current_user["id"] if current_user else None
                )
                
                if not instance:
                    raise HTTPException(
                        status_code=404, 
                        detail=f"{self.schema.title or self.schema.name} not found"
                    )
                
                return self._model_to_response(instance)
                
            except HTTPException:
                raise
            except CRUDException as e:
                raise HTTPException(status_code=400, detail=str(e))
            except Exception as e:
                raise HTTPException(status_code=500, detail="Internal server error")
    
    def _add_update_route(self):
        """Add PUT route for updating records."""
        
        @self.router.put(
            "/{record_id}",
            response_model=self._create_response_model(),
            summary=f"Update {self.schema.title or self.schema.name}",
            description=f"Update a {self.schema.title or self.schema.name} record"
        )
        async def update_record(
            record_id: int = Path(..., description="Record ID"),
            data: self._create_update_model() = Body(...),
            session: AsyncSession = Depends(get_db_session),
            current_user: Optional[User] = self._get_auth_dependency("update")
        ):
            try:
                # Convert Pydantic model to dict, excluding unset fields
                update_data = data.dict(exclude_unset=True)
                
                instance = await self.crud_service.update(
                    session=session,
                    record_id=record_id,
                    data=update_data,
                    updated_by_id=current_user["id"] if current_user else None
                )
                
                if not instance:
                    raise HTTPException(
                        status_code=404, 
                        detail=f"{self.schema.title or self.schema.name} not found"
                    )
                
                return self._model_to_response(instance)
                
            except HTTPException:
                raise
            except CRUDException as e:
                raise HTTPException(status_code=400, detail=str(e))
            except Exception as e:
                raise HTTPException(status_code=500, detail="Internal server error")
    
    def _add_delete_route(self):
        """Add DELETE route for deleting records."""
        
        @self.router.delete(
            "/{record_id}",
            status_code=204,
            summary=f"Delete {self.schema.title or self.schema.name}",
            description=f"Delete a {self.schema.title or self.schema.name} record"
        )
        async def delete_record(
            record_id: int = Path(..., description="Record ID"),
            hard_delete: bool = Query(False, description="Permanently delete the record"),
            session: AsyncSession = Depends(get_db_session),
            current_user: Optional[User] = self._get_auth_dependency("delete")
        ):
            try:
                deleted = await self.crud_service.delete(
                    session=session,
                    record_id=record_id,
                    deleted_by_id=current_user["id"] if current_user else None,
                    hard_delete=hard_delete
                )
                
                if not deleted:
                    raise HTTPException(
                        status_code=404, 
                        detail=f"{self.schema.title or self.schema.name} not found"
                    )
                
                return None  # 204 No Content
                
            except HTTPException:
                raise
            except CRUDException as e:
                raise HTTPException(status_code=400, detail=str(e))
            except Exception as e:
                raise HTTPException(status_code=500, detail="Internal server error")
    
    def _add_count_route(self):
        """Add GET route for counting records."""
        
        @self.router.get(
            "/count",
            response_model=dict,
            summary=f"Count {self.schema.title or self.schema.name} records",
            description=f"Get the total count of {self.schema.title or self.schema.name} records"
        )
        async def count_records(
            # Same filter parameters as list route
            search: Optional[str] = Query(None, description="Search term"),
            search_fields: Optional[str] = Query(None, description="Comma-separated list of fields to search in"),
            
            session: AsyncSession = Depends(get_db_session),
            current_user: Optional[User] = self._get_auth_dependency("count")
        ):
            try:
                params = QueryParams(
                    search=search,
                    search_fields=search_fields.split(",") if search_fields else None,
                    filters={}  # TODO: Implement dynamic filtering
                )
                
                total = await self.crud_service.count(
                    session=session,
                    params=params,
                    user_id=current_user["id"] if current_user else None
                )
                
                return {"count": total}
                
            except CRUDException as e:
                raise HTTPException(status_code=400, detail=str(e))
            except Exception as e:
                raise HTTPException(status_code=500, detail="Internal server error")
    
    def _create_request_model(self) -> Type[BaseModel]:
        """Create Pydantic model for request validation (CREATE)."""
        fields = {}
        
        for field in self.schema.fields:
            field_info = self._get_pydantic_field_info(field, required=field.required)
            fields[field.name] = field_info
        
        return create_model(
            f"{self.schema.name}Create",
            **fields,
            __base__=BaseModel
        )
    
    def _create_update_model(self) -> Type[BaseModel]:
        """Create Pydantic model for update validation (UPDATE)."""
        fields = {}
        
        for field in self.schema.fields:
            # All fields are optional for updates
            field_info = self._get_pydantic_field_info(field, required=False)
            fields[field.name] = field_info
        
        return create_model(
            f"{self.schema.name}Update",
            **fields,
            __base__=BaseModel
        )
    
    def _create_response_model(self) -> Type[BaseModel]:
        """Create Pydantic model for API responses."""
        fields = {}
        
        # Add ID field (always present)
        fields["id"] = (int, Field(..., description="Unique identifier"))
        
        # Add schema fields
        for field in self.schema.fields:
            field_info = self._get_pydantic_field_info(field, required=False, for_response=True)
            fields[field.name] = field_info
        
        # Add enterprise fields if enabled
        if self.schema.enable_timestamps:
            fields["created_at"] = (datetime, Field(..., description="Creation timestamp"))
            fields["updated_at"] = (Optional[datetime], Field(None, description="Last update timestamp"))
        
        if self.schema.enable_audit:
            fields["created_by_id"] = (Optional[int], Field(None, description="ID of user who created this record"))
            fields["updated_by_id"] = (Optional[int], Field(None, description="ID of user who last updated this record"))
        
        if self.schema.enable_soft_delete:
            fields["is_deleted"] = (bool, Field(False, description="Whether this record is deleted"))
            fields["deleted_at"] = (Optional[datetime], Field(None, description="Deletion timestamp"))
            fields["deleted_by_id"] = (Optional[int], Field(None, description="ID of user who deleted this record"))
        
        return create_model(
            f"{self.schema.name}Response",
            **fields,
            __base__=BaseModel
        )
    
    def _create_list_response_model(self) -> Type[BaseModel]:
        """Create Pydantic model for list API responses."""
        return create_model(
            f"{self.schema.name}ListResponse",
            items=(List[self._create_response_model()], Field(..., description="List of records")),
            total=(int, Field(..., description="Total number of records")),
            skip=(int, Field(..., description="Number of records skipped")),
            limit=(int, Field(..., description="Maximum number of records returned")),
            has_next=(bool, Field(..., description="Whether there are more records")),
            __base__=BaseModel
        )
    
    def _get_pydantic_field_info(self, field: FieldDefinition, required: bool, for_response: bool = False):
        """Convert schema field to Pydantic field info."""
        # Map field types to Python types
        type_mapping = {
            FieldType.STRING: str,
            FieldType.TEXT: str,
            FieldType.INTEGER: int,
            FieldType.FLOAT: float,
            FieldType.BOOLEAN: bool,
            FieldType.DATE: datetime,
            FieldType.DATETIME: datetime,
            FieldType.EMAIL: str,
            FieldType.URL: str,
            FieldType.UUID: str,
            FieldType.JSON: dict,
            FieldType.FILE: str,
            FieldType.IMAGE: str,
            FieldType.DECIMAL: float,
            FieldType.CURRENCY: float,
            FieldType.CHOICE: str,
            FieldType.MULTI_CHOICE: List[str],
        }
        
        python_type = type_mapping.get(field.field_type, str)
        
        # Make optional if not required
        if not required:
            python_type = Optional[python_type]
        
        # Create field info
        field_kwargs = {
            "description": field.description or f"{field.name} field"
        }
        
        # Add default value
        if field.default is not None:
            field_kwargs["default"] = field.default
        elif not required:
            field_kwargs["default"] = None
        else:
            field_kwargs["default"] = ...  # Required field marker
        
        # Add validation constraints
        if field.min_length:
            field_kwargs["min_length"] = field.min_length
        if field.max_length:
            field_kwargs["max_length"] = field.max_length
        if field.min_value:
            field_kwargs["ge"] = field.min_value  # Greater than or equal
        if field.max_value:
            field_kwargs["le"] = field.max_value  # Less than or equal
        
        return (python_type, Field(**field_kwargs))
    
    def _extract_filters(self, filters: Dict[str, Any]) -> Dict[str, Any]:
        """Extract valid filters from query parameters."""
        valid_filters = {}
        
        # Get valid field names from schema
        valid_field_names = {field.name for field in self.schema.fields}
        valid_field_names.update({"id", "created_at", "updated_at"})  # Add system fields
        
        for key, value in filters.items():
            if key in valid_field_names and value is not None:
                valid_filters[key] = value
        
        return valid_filters
    
    def _model_to_response(self, instance: DynamicModel) -> Dict[str, Any]:
        """Convert model instance to response dict."""
        # Get all attributes from the instance
        response_data = {}
        
        # Add ID
        response_data["id"] = instance.id
        
        # Add schema fields
        for field in self.schema.fields:
            if hasattr(instance, field.name):
                value = getattr(instance, field.name)
                response_data[field.name] = value
        
        # Add enterprise fields if they exist
        enterprise_fields = [
            "created_at", "updated_at", "created_by_id", "updated_by_id",
            "is_deleted", "deleted_at", "deleted_by_id"
        ]
        
        for field_name in enterprise_fields:
            if hasattr(instance, field_name):
                value = getattr(instance, field_name)
                response_data[field_name] = value
        
        return response_data
    
    def _get_auth_dependency(self, route_name: str):
        """
        Get the appropriate auth dependency based on schema auth_config.
        
        Args:
            route_name: Name of the route ("list", "get", "create", "update", "delete", "count")
        
        Returns:
            Auth dependency (either get_current_user or get_optional_user)
        """
        auth_config = self.schema.auth_config
        
        # Check if this specific route should be public
        if route_name in auth_config.get("public_routes", []):
            return Depends(get_optional_user)
        
        # Check if this specific route should be protected (overrides other settings)
        if route_name in auth_config.get("protected_routes", []):
            return Depends(get_current_user)
        
        # Check read_public setting for read operations
        if auth_config.get("read_public", False) and route_name in ["list", "get", "count"]:
            return Depends(get_optional_user)
        
        # Check write_protected setting for write operations
        if auth_config.get("write_protected", True) and route_name in ["create", "update", "delete"]:
            return Depends(get_current_user)
        
        # Default based on require_auth setting
        if auth_config.get("require_auth", True):
            return Depends(get_current_user)
        
        return Depends(get_optional_user)


def create_router_for_schema(schema: SchemaDefinition, model: Type[DynamicModel]) -> APIRouter:
    """
    Convenience function to create a router for a schema.
    
    Args:
        schema: Schema definition
        model: Dynamic model class
        
    Returns:
        FastAPI router with generated routes
    """
    factory = RouteFactory(schema, model)
    return factory.router


# Legacy class name for backward compatibility
DynamicRouteFactory = RouteFactory 