"""
Models package for FastAPI Auth.

This package provides base models and utilities for user authentication.
"""

from models.base import Base
from models.user import User

__all__ = [
    "Base",
    "User",
]
