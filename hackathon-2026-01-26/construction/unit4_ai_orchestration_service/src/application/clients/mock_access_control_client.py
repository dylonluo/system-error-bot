from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import List
from uuid import UUID

from ...domain.services.response_generation_service import DocumentLink


@dataclass
class User:
    """User information from access control."""
    user_id: UUID
    username: str
    access_level: str
    roles: List[str]


class IAccessControlClient(ABC):
    """Interface for access control client."""

    @abstractmethod
    def validate_token(self, token: str) -> User:
        pass

    @abstractmethod
    def filter_documents(self, documents: List[DocumentLink], user_id: UUID) -> List[DocumentLink]:
        pass


class MockAccessControlClient(IAccessControlClient):
    """Mock access control client."""

    def validate_token(self, token: str) -> User:
        """Always returns a valid user for demo purposes."""
        from uuid import uuid4
        return User(
            user_id=uuid4(),
            username="demo_user",
            access_level="standard",
            roles=["user", "viewer"],
        )

    def filter_documents(self, documents: List[DocumentLink], user_id: UUID) -> List[DocumentLink]:
        """Returns all documents (no filtering in mock)."""
        return documents
