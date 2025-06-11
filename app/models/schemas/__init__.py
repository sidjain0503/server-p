"""
Schema definitions package

This package contains all the schema definitions for the meta-engine system.
Each schema is defined in its own module for better organization and maintainability.
"""

from .product_schema import get_product_schema
from .customer_schema import get_customer_schema
from .task_schema import get_task_schema

__all__ = [
    "get_product_schema",
    "get_customer_schema", 
    "get_task_schema"
] 