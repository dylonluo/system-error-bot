"""ConversationId value object"""
from dataclasses import dataclass
from uuid import UUID, uuid4


@dataclass(frozen=True)
class ConversationId:
    """Unique identifier for a conversation"""
    value: UUID

    @staticmethod
    def generate() -> 'ConversationId':
        """Generate a new ConversationId"""
        return ConversationId(uuid4())

    @staticmethod
    def from_string(id_str: str) -> 'ConversationId':
        """Create ConversationId from string"""
        return ConversationId(UUID(id_str))

    def __str__(self) -> str:
        return str(self.value)

    def __eq__(self, other) -> bool:
        if not isinstance(other, ConversationId):
            return False
        return self.value == other.value

    def __hash__(self) -> int:
        return hash(self.value)
