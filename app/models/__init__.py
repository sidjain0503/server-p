"""
Database Models Package

This package contains:
- Base model classes
- System models (User, Role, etc.)
- Dynamically generated models (created by meta-engine)
"""

from app.core.database import Base

# Import all model classes here for Alembic auto-discovery
from app.models.base import *

__all__ = ["Base"] 