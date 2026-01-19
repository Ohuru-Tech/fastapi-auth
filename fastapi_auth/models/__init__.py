"""
Models package for FastAPI Auth.

This package provides base models and utilities for user authentication.
"""

from sqlalchemy import MetaData

from fastapi_auth.models.base import Base
from fastapi_auth.models.rbac import Permission, Role, RolePermission, UserRole
from fastapi_auth.models.social_providers import SocialProvider
from fastapi_auth.models.user import User


def get_metadata() -> MetaData:
    """
    Expose this package's SQLAlchemy MetaData for use in Alembic migrations.
    
    Returns:
        MetaData: SQLAlchemy MetaData containing all tables defined by this package (Base.metadata).
    """
    return Base.metadata


__all__ = [
    "Base",
    "SocialProvider",
    "User",
    "Role",
    "Permission",
    "UserRole",
    "RolePermission",
    "get_metadata",
]