"""DocumentAccessLevel value object."""

from enum import Enum


class AccessLevel(str, Enum):
    """Access level enumeration."""

    PUBLIC = "public"
    BASIC = "basic"
    ADVANCED = "advanced"


class DocumentAccessLevel:
    """Document access level with business rules."""

    def __init__(self, value: AccessLevel):
        if not isinstance(value, AccessLevel):
            raise ValueError(f"Invalid access level: {value}")
        self._value = value

    @property
    def value(self) -> AccessLevel:
        return self._value

    def is_public(self) -> bool:
        return self._value == AccessLevel.PUBLIC

    def is_basic(self) -> bool:
        return self._value == AccessLevel.BASIC

    def is_advanced(self) -> bool:
        return self._value == AccessLevel.ADVANCED

    def is_accessible_by(self, user_access_level: str) -> bool:
        """Check if user can access this document."""
        # PUBLIC: accessible to all
        if self._value == AccessLevel.PUBLIC:
            return True
        # BASIC: accessible to basic and all (admin)
        if self._value == AccessLevel.BASIC:
            return user_access_level in ["basic", "all"]
        # ADVANCED: accessible to all (admin) only
        if self._value == AccessLevel.ADVANCED:
            return user_access_level == "all"
        return False

    def __eq__(self, other) -> bool:
        if not isinstance(other, DocumentAccessLevel):
            return False
        return self._value == other._value

    def __hash__(self) -> int:
        return hash(self._value)

    def __str__(self) -> str:
        return self._value.value

    def __repr__(self) -> str:
        return f"DocumentAccessLevel({self._value.value})"
