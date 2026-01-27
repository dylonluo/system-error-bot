from dataclasses import dataclass
from uuid import UUID, uuid4


@dataclass(frozen=True)
class QueryId:
    """Unique identifier for an AI query."""
    value: UUID

    @classmethod
    def generate(cls) -> "QueryId":
        return cls(value=uuid4())

    @classmethod
    def from_string(cls, id_str: str) -> "QueryId":
        return cls(value=UUID(id_str))

    def __str__(self) -> str:
        return str(self.value)
