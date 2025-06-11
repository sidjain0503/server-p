"""
Dynamic Model Factory

This module converts schema definitions into SQLAlchemy models at runtime.
It uses Python metaclasses and type() to dynamically create model classes.
"""

import re
from typing import Any, Dict, Type, Optional
from datetime import datetime, date, time
from decimal import Decimal

from sqlalchemy import (
    Column, Integer, String, Text, Boolean, Float, DateTime, Date, Time,
    JSON, ForeignKey, Index, UniqueConstraint, CheckConstraint, Numeric
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship, validates
from sqlalchemy.ext.declarative import declared_attr

from app.core.database import Base
from app.models.base import DynamicModel, TimestampMixin, AuditMixin, SoftDeleteMixin, MetadataMixin
from app.meta_engine.schema_definition import SchemaDefinition, FieldDefinition, FieldType, RelationshipType


class DynamicModelFactory:
    """
    Factory class that creates SQLAlchemy model classes from schema definitions.
    
    This uses Python metaclasses to dynamically generate model classes at runtime
    that inherit from our base model classes and include all the fields and
    relationships defined in the schema.
    """
    
    def __init__(self):
        self._created_models: Dict[str, Type] = {}
        self._schema_cache: Dict[str, SchemaDefinition] = {}
    
    def create_model(self, schema: SchemaDefinition) -> Type[DynamicModel]:
        """
        Create a SQLAlchemy model class from a schema definition.
        
        Args:
            schema: The schema definition to convert
            
        Returns:
            A dynamically created SQLAlchemy model class
        """
        model_name = schema.model_name
        
        # Check if model already exists
        if model_name in self._created_models:
            return self._created_models[model_name]
        
        # Cache the schema
        self._schema_cache[model_name] = schema
        
        # Determine base classes
        base_classes = [DynamicModel]
        
        if schema.enable_timestamps and TimestampMixin not in base_classes:
            base_classes.append(TimestampMixin)
        
        if schema.enable_audit and AuditMixin not in base_classes:
            base_classes.append(AuditMixin)
        
        if schema.enable_soft_delete and SoftDeleteMixin not in base_classes:
            base_classes.append(SoftDeleteMixin)
        
        # Always include metadata for dynamic models
        if MetadataMixin not in base_classes:
            base_classes.append(MetadataMixin)
        
        # Create class attributes dictionary
        class_attrs = self._build_class_attributes(schema)
        
        # Set schema metadata
        class_attrs['_schema_name'] = schema.name
        class_attrs['_schema_version'] = schema.version
        class_attrs['__table_args__'] = self._build_table_constraints(schema)
        
        # Create the model class dynamically
        model_class = type(
            model_name,
            tuple(base_classes),
            class_attrs
        )
        
        # Cache the created model
        self._created_models[model_name] = model_class
        
        return model_class
    
    def _build_class_attributes(self, schema: SchemaDefinition) -> Dict[str, Any]:
        """Build the class attributes dictionary for the dynamic model."""
        attrs = {}
        
        # Set table name
        if schema.table_name:
            attrs['__tablename__'] = schema.table_name
        else:
            # Convert CamelCase to snake_case and pluralize
            table_name = self._camel_to_snake(schema.name)
            if not table_name.endswith('s'):
                table_name += 's'
            attrs['__tablename__'] = table_name
        
        # Add fields as SQLAlchemy columns
        for field in schema.fields:
            column = self._create_column(field)
            if column is not None:
                attrs[field.name] = column
        
        # Add validation methods
        attrs.update(self._create_validation_methods(schema))
        
        # Add relationship methods (will be implemented after all models are created)
        relationship_attrs = self._create_relationships(schema)
        attrs.update(relationship_attrs)
        
        return attrs
    
    def _create_column(self, field: FieldDefinition) -> Optional[Column]:
        """Create a SQLAlchemy column from a field definition."""
        
        # Skip relationship fields (they're handled separately)
        if field.relationship_type:
            return None
        
        # Map field types to SQLAlchemy types
        sql_type = self._get_sqlalchemy_type(field)
        
        # Build column arguments
        column_args = []
        column_kwargs = {
            'nullable': not field.required,
            'doc': field.description or field.label
        }
        
        # Add constraints
        if field.unique:
            column_kwargs['unique'] = True
        
        if field.indexed:
            column_kwargs['index'] = True
        
        if field.default is not None:
            column_kwargs['default'] = field.default
        
        # Add field-specific constraints
        if field.field_type == FieldType.STRING and field.max_length:
            # String type with max length already handled in _get_sqlalchemy_type
            pass
        
        return Column(sql_type, *column_args, **column_kwargs)
    
    def _get_sqlalchemy_type(self, field: FieldDefinition):
        """Map field types to SQLAlchemy column types."""
        
        type_mapping = {
            FieldType.STRING: String(field.max_length or 255),
            FieldType.TEXT: Text,
            FieldType.INTEGER: Integer,
            FieldType.FLOAT: Float,
            FieldType.BOOLEAN: Boolean,
            FieldType.DATE: Date,
            FieldType.DATETIME: DateTime(timezone=True),
            FieldType.TIME: Time,
            FieldType.EMAIL: String(255),  # Email is just a string with validation
            FieldType.URL: String(2048),   # URLs can be long
            FieldType.UUID: UUID(as_uuid=True),
            FieldType.JSON: JSON,
            FieldType.DECIMAL: Numeric(precision=10, scale=2),
            FieldType.CURRENCY: Numeric(precision=10, scale=2),
            FieldType.CHOICE: String(100),
            FieldType.MULTI_CHOICE: JSON,  # Store as JSON array
            FieldType.FILE: String(500),   # Store file path/URL
            FieldType.IMAGE: String(500),  # Store image path/URL
        }
        
        return type_mapping.get(field.field_type, String(255))
    
    def _create_validation_methods(self, schema: SchemaDefinition) -> Dict[str, Any]:
        """Create validation methods for the model."""
        validation_methods = {}
        
        for field in schema.fields:
            # Skip relationships
            if field.relationship_type:
                continue
            
            validators = []
            
            # Add built-in validations
            if field.field_type == FieldType.EMAIL:
                validators.append(self._create_email_validator(field.name))
            
            if field.field_type == FieldType.URL:
                validators.append(self._create_url_validator(field.name))
            
            if field.min_length or field.max_length:
                validators.append(self._create_length_validator(field.name, field.min_length, field.max_length))
            
            if field.min_value is not None or field.max_value is not None:
                validators.append(self._create_range_validator(field.name, field.min_value, field.max_value))
            
            if field.choices:
                validators.append(self._create_choice_validator(field.name, field.choices))
            
            # Add custom validation rules
            for rule in field.validation_rules:
                validator_func = self._create_custom_validator(field.name, rule)
                if validator_func:
                    validators.append(validator_func)
            
            # Combine all validators for this field
            if validators:
                validation_methods[f'validate_{field.name}'] = self._combine_validators(field.name, validators)
        
        return validation_methods
    
    def _create_email_validator(self, field_name: str):
        """Create email validation function."""
        def validator(self, key, value):
            if value and '@' not in value:
                raise ValueError(f"Invalid email address: {value}")
            return value
        return validates(field_name)(validator)
    
    def _create_url_validator(self, field_name: str):
        """Create URL validation function."""
        def validator(self, key, value):
            if value and not (value.startswith('http://') or value.startswith('https://')):
                raise ValueError(f"Invalid URL: {value}")
            return value
        return validates(field_name)(validator)
    
    def _create_length_validator(self, field_name: str, min_length: Optional[int], max_length: Optional[int]):
        """Create string length validation function."""
        def validator(self, key, value):
            if value:
                length = len(str(value))
                if min_length and length < min_length:
                    raise ValueError(f"{field_name} must be at least {min_length} characters")
                if max_length and length > max_length:
                    raise ValueError(f"{field_name} must be no more than {max_length} characters")
            return value
        return validates(field_name)(validator)
    
    def _create_range_validator(self, field_name: str, min_value: Optional[float], max_value: Optional[float]):
        """Create numeric range validation function."""
        def validator(self, key, value):
            if value is not None:
                if min_value is not None and value < min_value:
                    raise ValueError(f"{field_name} must be at least {min_value}")
                if max_value is not None and value > max_value:
                    raise ValueError(f"{field_name} must be no more than {max_value}")
            return value
        return validates(field_name)(validator)
    
    def _create_choice_validator(self, field_name: str, choices: list):
        """Create choice validation function."""
        valid_values = [choice['value'] for choice in choices]
        
        def validator(self, key, value):
            if value and value not in valid_values:
                raise ValueError(f"{field_name} must be one of: {valid_values}")
            return value
        return validates(field_name)(validator)
    
    def _create_custom_validator(self, field_name: str, rule):
        """Create custom validation function from validation rule."""
        # This can be extended to support various custom validation types
        rule_type = rule.rule_type
        
        if rule_type == "regex":
            pattern = re.compile(rule.value)
            def validator(self, key, value):
                if value and not pattern.match(str(value)):
                    message = rule.message or f"{field_name} does not match required pattern"
                    raise ValueError(message)
                return value
            return validates(field_name)(validator)
        
        # Add more custom validation types as needed
        return None
    
    def _combine_validators(self, field_name: str, validators: list):
        """Combine multiple validators into a single validation method."""
        def combined_validator(self, key, value):
            for validator_func in validators:
                value = validator_func(self, key, value)
            return value
        return validates(field_name)(combined_validator)
    
    def _create_relationships(self, schema: SchemaDefinition) -> Dict[str, Any]:
        """Create relationship attributes for the model."""
        relationships = {}
        
        for field in schema.fields:
            if not field.relationship_type:
                continue
            
            # Create foreign key column if needed
            if field.relationship_type in [RelationshipType.MANY_TO_ONE, RelationshipType.ONE_TO_ONE]:
                fk_column_name = field.foreign_key or f"{field.name}_id"
                relationships[fk_column_name] = Column(Integer, ForeignKey(f"{field.related_schema.lower()}s.id"))
            
            # Create relationship
            rel_kwargs = {
                'back_populates': schema.name.lower() + 's' if field.relationship_type == RelationshipType.ONE_TO_MANY else schema.name.lower()
            }
            
            if field.relationship_type == RelationshipType.MANY_TO_MANY:
                # For many-to-many, we'd need to create association tables
                # This is more complex and would be implemented in a full system
                pass
            else:
                relationships[field.name] = relationship(
                    f"Dynamic{field.related_schema.title()}",
                    **rel_kwargs
                )
        
        return relationships
    
    def _build_table_constraints(self, schema: SchemaDefinition) -> tuple:
        """Build table-level constraints."""
        constraints = []
        
        # Add unique constraints for combinations of fields
        unique_fields = [f.name for f in schema.fields if f.unique]
        if len(unique_fields) > 1:
            constraints.append(UniqueConstraint(*unique_fields))
        
        # Add indexes for frequently queried fields
        indexed_fields = [f.name for f in schema.fields if f.indexed]
        for field_name in indexed_fields:
            constraints.append(Index(f"idx_{schema.name.lower()}_{field_name}", field_name))
        
        return tuple(constraints)
    
    def _camel_to_snake(self, name: str) -> str:
        """Convert CamelCase to snake_case."""
        s1 = re.sub('(.)([A-Z][a-z]+)', r'\1_\2', name)
        return re.sub('([a-z0-9])([A-Z])', r'\1_\2', s1).lower()
    
    def get_model(self, schema_name: str) -> Optional[Type[DynamicModel]]:
        """Get an already created model by schema name."""
        model_name = f"Dynamic{schema_name.title()}"
        return self._created_models.get(model_name)
    
    def get_schema(self, model_name: str) -> Optional[SchemaDefinition]:
        """Get the schema definition for a model."""
        return self._schema_cache.get(model_name)
    
    def list_models(self) -> Dict[str, Type[DynamicModel]]:
        """Get all created models."""
        return self._created_models.copy()
    
    def clear_cache(self):
        """Clear the model cache (useful for testing)."""
        self._created_models.clear()
        self._schema_cache.clear()


# Global factory instance
model_factory = DynamicModelFactory() 