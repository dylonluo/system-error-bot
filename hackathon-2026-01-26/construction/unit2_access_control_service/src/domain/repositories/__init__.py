"""Domain Repository Interfaces - Abstract repository contracts."""

from .user_repository import IUserRepository
from .session_repository import ISessionRepository

__all__ = ['IUserRepository', 'ISessionRepository']
