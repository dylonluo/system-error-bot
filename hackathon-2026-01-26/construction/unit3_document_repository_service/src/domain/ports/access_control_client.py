"""IAccessControlClient interface."""

from abc import ABC, abstractmethod
from typing import Any, Dict, List


class IAccessControlClient(ABC):
    """Interface for Access Control Context communication."""

    @abstractmethod
    def validate_token(self, token: str) -> Dict[str, Any]:
        """Validate user token and return user info."""
        pass

    @abstractmethod
    def filter_documents(self, documents: List, user_id: str) -> List:
        """Filter documents based on user access level."""
        pass
