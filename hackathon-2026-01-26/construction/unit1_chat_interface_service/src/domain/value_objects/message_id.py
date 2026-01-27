"""MessageId value object"""
from dataclasses import dataclass
from uuid import UUID, uuid4


@dataclass(frozen=True)
class MessageId:
    """Unique identifier for a message"""
    value: UUID

    @staticmethod
    def generate() -> 'MessageId':
        """Generate a new MessageId"""
        return MessageId(uuid4())

    @staticmethod
    def from_string(id_str: str) -> 'MessageId':
        """Create MessageId from string"""
        return MessageId(UUID(id_str))

    def __str__(self) -> str:
        return str(self.value)

    def __eq__(self, other) -> bool:
        if not isinstance(other, MessageId):
            return False
        return self.value == other.value

    def __hash__(self) -> int:
        return hash(self.value)
