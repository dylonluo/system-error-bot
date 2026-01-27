"""QueryId value object."""

from typing import Union
from uuid import UUID, uuid4


class QueryId:
    """Unique identifier for a search query."""

    def __init__(self, value: Union[str, UUID]):
        if isinstance(value, str):
            self._value = UUID(value)
        else:
            self._value = value

    @classmethod
    def generate(cls) -> "QueryId":
        """Generate a new QueryId."""
        return cls(uuid4())

    @property
    def value(self) -> UUID:
        return self._value

    def __eq__(self, other) -> bool:
        if not isinstance(other, QueryId):
            return False
        return self._value == other._value

    def __hash__(self) -> int:
        return hash(self._value)

    def __str__(self) -> str:
        return str(self._value)

    def __repr__(self) -> str:
        return f"QueryId({self._value})"
