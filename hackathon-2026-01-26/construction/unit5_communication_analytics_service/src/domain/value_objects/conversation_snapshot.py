from dataclasses import dataclass
from datetime import datetime
from typing import List, Dict, Any


@dataclass(frozen=True)
class ConversationSnapshot:
    """Value object representing a snapshot of a conversation."""
    
    conversation_id: str
    messages: List[Dict[str, Any]]
    user_info: Dict[str, Any]
    created_at: datetime
    
    def __post_init__(self):
        if not self.conversation_id:
            raise ValueError("Conversation ID cannot be empty")
        if not self.messages:
            raise ValueError("Conversation must have at least one message")
        if not self.user_info:
            raise ValueError("User info cannot be empty")
    
    def format_for_email(self) -> str:
        """Format conversation for email body."""
        lines = []
        lines.append(f"Conversation ID: {self.conversation_id}")
        lines.append(f"Created At: {self.created_at.isoformat()}")
        lines.append(f"\nUser Information:")
        lines.append(f"  Name: {self.user_info.get('name', 'N/A')}")
        lines.append(f"  Email: {self.user_info.get('email', 'N/A')}")
        lines.append(f"  Role: {self.user_info.get('role', 'N/A')}")
        lines.append(f"\nConversation History ({len(self.messages)} messages):")
        lines.append("-" * 60)
        
        for i, msg in enumerate(self.messages, 1):
            role = msg.get('role', 'unknown')
            content = msg.get('content', '')
            timestamp = msg.get('timestamp', 'N/A')
            lines.append(f"\n[{i}] {role.upper()} ({timestamp}):")
            lines.append(f"{content}")
        
        return "\n".join(lines)
    
    def get_message_count(self) -> int:
        """Get the number of messages in the conversation."""
        return len(self.messages)
    
    def __str__(self):
        return f"ConversationSnapshot({self.conversation_id}, {len(self.messages)} messages)"
