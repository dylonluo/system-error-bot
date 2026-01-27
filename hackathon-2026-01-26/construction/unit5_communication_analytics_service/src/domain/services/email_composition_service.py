from ..value_objects import EmailContent, EmailFormat, ConversationSnapshot
from typing import Dict, Any, List


class EmailCompositionService:
    """Domain service for composing escalation emails."""
    
    def compose_email(self, conversation_snapshot: ConversationSnapshot, user_info: Dict[str, Any]) -> EmailContent:
        """Compose escalation email content."""
        body = self._build_email_body(conversation_snapshot, user_info)
        return EmailContent(body=body, format=EmailFormat.PLAIN_TEXT)
    
    def _build_email_body(self, conversation_snapshot: ConversationSnapshot, user_info: Dict[str, Any]) -> str:
        """Build the email body."""
        lines = []
        lines.append("=" * 70)
        lines.append("SUPPORT ESCALATION REQUEST")
        lines.append("=" * 70)
        lines.append("")
        lines.append(self.format_user_info(user_info))
        lines.append("")
        lines.append(self.format_conversation_history(conversation_snapshot))
        lines.append("")
        lines.append("=" * 70)
        lines.append("Please review this conversation and provide assistance.")
        lines.append("Expected response time: 24-48 hours")
        lines.append("=" * 70)
        return "\n".join(lines)
    
    def format_conversation_history(self, conversation_snapshot: ConversationSnapshot) -> str:
        """Format conversation history for email."""
        return conversation_snapshot.format_for_email()
    
    def format_user_info(self, user: Dict[str, Any]) -> str:
        """Format user information for email."""
        lines = []
        lines.append("USER INFORMATION:")
        lines.append(f"  Name: {user.get('name', 'N/A')}")
        lines.append(f"  Email: {user.get('email', 'N/A')}")
        lines.append(f"  Role: {user.get('role', 'N/A')}")
        lines.append(f"  User ID: {user.get('user_id', 'N/A')}")
        return "\n".join(lines)
    
    def generate_subject(self, conversation_id: str) -> str:
        """Generate email subject."""
        return f"Support Escalation - {conversation_id}"
