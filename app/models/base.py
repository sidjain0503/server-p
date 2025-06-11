"""
Base Model Classes

This module defines base classes that all database models inherit from.
These provide common functionality like timestamps, IDs, and audit trails.
"""

import uuid
from datetime import datetime
from typing import Any, Dict

from sqlalchemy import Column, Integer, String, DateTime, Boolean, Text, JSON
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.ext.declarative import declared_attr
from sqlalchemy.sql import func

from app.core.database import Base


class TimestampMixin:
    """
    Mixin that adds created_at and updated_at timestamps to models.
    """
    
    created_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
        index=True,
        doc="When the record was created"
    )
    
    updated_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
        index=True,
        doc="When the record was last updated"
    )


class UUIDMixin:
    """
    Mixin that adds a UUID primary key to models.
    """
    
    id = Column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        nullable=False,
        doc="Unique identifier for the record"
    )


class IntegerIDMixin:
    """
    Mixin that adds an integer primary key to models.
    """
    
    id = Column(
        Integer,
        primary_key=True,
        autoincrement=True,
        nullable=False,
        doc="Unique identifier for the record"
    )


class SoftDeleteMixin:
    """
    Mixin that adds soft delete functionality to models.
    Records are marked as deleted instead of being physically removed.
    """
    
    is_deleted = Column(
        Boolean,
        default=False,
        nullable=False,
        index=True,
        doc="Whether the record is soft deleted"
    )
    
    deleted_at = Column(
        DateTime(timezone=True),
        nullable=True,
        index=True,
        doc="When the record was soft deleted"
    )


class AuditMixin:
    """
    Mixin that adds audit trail fields to models.
    Tracks who created and modified records.
    """
    
    created_by_id = Column(
        Integer,
        nullable=True,
        doc="ID of the user who created the record"
    )
    
    updated_by_id = Column(
        Integer,
        nullable=True,
        doc="ID of the user who last updated the record"
    )


class MetadataMixin:
    """
    Mixin that adds metadata fields for storing additional information.
    """
    
    metadata_json = Column(
        JSON,
        nullable=True,
        default=dict,
        doc="Additional metadata stored as JSON"
    )
    
    tags = Column(
        JSON,
        nullable=True,
        default=list,
        doc="Tags associated with the record"
    )


class BaseModel(Base, TimestampMixin, IntegerIDMixin):
    """
    Base model class that all database models should inherit from.
    
    Provides:
    - Integer primary key
    - Created/updated timestamps
    - Basic model methods
    """
    
    __abstract__ = True
    
    def to_dict(self, exclude_fields: set = None) -> Dict[str, Any]:
        """
        Convert model instance to dictionary.
        
        Args:
            exclude_fields: Set of field names to exclude
            
        Returns:
            Dictionary representation of the model
        """
        exclude_fields = exclude_fields or set()
        
        result = {}
        for column in self.__table__.columns:
            if column.name not in exclude_fields:
                value = getattr(self, column.name)
                
                # Handle datetime serialization
                if isinstance(value, datetime):
                    result[column.name] = value.isoformat()
                # Handle UUID serialization
                elif isinstance(value, uuid.UUID):
                    result[column.name] = str(value)
                else:
                    result[column.name] = value
        
        return result
    
    def update_from_dict(self, data: Dict[str, Any], exclude_fields: set = None) -> None:
        """
        Update model instance from dictionary.
        
        Args:
            data: Dictionary with field values
            exclude_fields: Set of field names to exclude from update
        """
        exclude_fields = exclude_fields or {'id', 'created_at'}
        
        for key, value in data.items():
            if key not in exclude_fields and hasattr(self, key):
                setattr(self, key, value)
    
    @classmethod
    def get_field_names(cls) -> list:
        """Get list of all field names for this model."""
        return [column.name for column in cls.__table__.columns]
    
    @classmethod
    def get_searchable_fields(cls) -> list:
        """
        Get list of fields that can be used for text search.
        Override in subclasses to specify searchable fields.
        """
        searchable_fields = []
        for column in cls.__table__.columns:
            if column.type.python_type == str:
                searchable_fields.append(column.name)
        return searchable_fields
    
    def __repr__(self) -> str:
        """String representation of the model."""
        return f"<{self.__class__.__name__}(id={self.id})>"


class AuditableModel(BaseModel, AuditMixin, SoftDeleteMixin):
    """
    Enhanced base model with audit trail and soft delete capabilities.
    
    Use this for models that need:
    - User tracking (who created/modified)
    - Soft delete functionality
    - Full audit trail
    """
    
    __abstract__ = True
    
    def soft_delete(self, deleted_by_id: int = None) -> None:
        """
        Soft delete the record.
        
        Args:
            deleted_by_id: ID of the user performing the deletion
        """
        self.is_deleted = True
        self.deleted_at = datetime.utcnow()
        if deleted_by_id:
            self.updated_by_id = deleted_by_id
    
    def restore(self, restored_by_id: int = None) -> None:
        """
        Restore a soft deleted record.
        
        Args:
            restored_by_id: ID of the user performing the restoration
        """
        self.is_deleted = False
        self.deleted_at = None
        if restored_by_id:
            self.updated_by_id = restored_by_id


class SystemModel(BaseModel):
    """
    Base class for core system models.
    
    These are models that are part of the core system and cannot be
    modified or deleted by the meta-engine.
    """
    
    __abstract__ = True
    
    # System models are protected
    _is_system_model = True


class DynamicModel(AuditableModel, MetadataMixin):
    """
    Base class for dynamically generated models.
    
    These models are created by the meta-engine based on user-defined schemas.
    They include all enterprise features:
    - Audit trail
    - Soft delete
    - Metadata storage
    - Full tracking
    """
    
    __abstract__ = True
    
    # This will be set by the meta-engine
    _schema_name: str = None
    _schema_version: int = None
    
    @declared_attr
    def __tablename__(cls):
        """
        Generate table name from class name.
        Converts CamelCase to snake_case and adds plural.
        """
        # Convert CamelCase to snake_case
        import re
        s1 = re.sub('(.)([A-Z][a-z]+)', r'\1_\2', cls.__name__)
        table_name = re.sub('([a-z0-9])([A-Z])', r'\1_\2', s1).lower()
        
        # Add 's' for plural (simple pluralization)
        if not table_name.endswith('s'):
            table_name += 's'
        
        return table_name
    
    def get_schema_info(self) -> Dict[str, Any]:
        """Get information about the schema this model was generated from."""
        return {
            "schema_name": self._schema_name,
            "schema_version": self._schema_version,
            "model_class": self.__class__.__name__,
            "table_name": self.__tablename__,
        } 