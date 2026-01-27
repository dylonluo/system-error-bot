"""DocumentVersion entity."""

from datetime import datetime
from typing import Optional
from uuid import UUID, uuid4


class VersionId:
    """Unique identifier for a document version."""

    def __init__(self, value: UUID):
        self._value = value

    @classmethod
    def generate(cls) -> "VersionId":
        return cls(uuid4())

    @property
    def value(self) -> UUID:
        return self._value

    def __eq__(self, other) -> bool:
        if not isinstance(other, VersionId):
            return False
        return self._value == other._value

    def __hash__(self) -> int:
        return hash(self._value)

    def __str__(self) -> str:
        return str(self._value)


class DocumentVersion:
    """Entity representing a version of a document."""

    def __init__(
        self,
        version_id: VersionId,
        document_id,
        version_number: int,
        modified_at: datetime,
        modified_by: Optional[str] = None,
        change_description: Optional[str] = None,
    ):
        self._version_id = version_id
        self._document_id = document_id
        self._version_number = version_number
        self._modified_at = modified_at
        self._modified_by = modified_by
        self._change_description = change_description
        self._is_latest = False

    @property
    def version_id(self) -> VersionId:
        return self._version_id

    @property
    def document_id(self):
        return self._document_id

    @property
    def version_number(self) -> int:
        return self._version_number

    @property
    def modified_at(self) -> datetime:
        return self._modified_at

    @property
    def modified_by(self) -> Optional[str]:
        return self._modified_by

    @property
    def change_description(self) -> Optional[str]:
        return self._change_description

    def is_latest(self) -> bool:
        """Check if this is the latest version."""
        return self._is_latest

    def mark_as_latest(self) -> None:
        """Mark this version as the latest."""
        self._is_latest = True

    def mark_as_old(self) -> None:
        """Mark this version as not the latest."""
        self._is_latest = False

    def get_changes_since(self, version: "DocumentVersion") -> str:
        """Get description of changes since another version."""
        if self._version_number <= version._version_number:
            return "No changes"
        return self._change_description or f"Version {self._version_number} changes"

    def __eq__(self, other) -> bool:
        if not isinstance(other, DocumentVersion):
            return False
        return self._version_id == other._version_id

    def __repr__(self) -> str:
        return f"DocumentVersion(id={self._version_id}, number={self._version_number})"
