"""Communication & Analytics Context client (mock)"""
from dataclasses import dataclass
from uuid import UUID


@dataclass
class EmailConfirmation:
    """Email confirmation model"""
    email_id: str
    status: str
    message: str


@dataclass
class EventConfirmation:
    """Event confirmation model"""
    event_id: str
    status: str


class CommunicationAnalyticsClient:
    """Mock client for Communication & Analytics Context"""

    def send_escalation_email(
        self,
        conversation_id: str,
        user_id: UUID,
        conversation_history: str
    ) -> EmailConfirmation:
        """Send escalation email to support team"""
        # Mock implementation
        print(f"[EMAIL] Sending escalation email for conversation {conversation_id}")
        return EmailConfirmation(
            email_id=f"email-{conversation_id}",
            status="sent",
            message="Escalation email sent successfully to support team"
        )

    def record_event(self, event_type: str, metadata: dict) -> EventConfirmation:
        """Record analytics event"""
        # Mock implementation - fire and forget
        print(f"[ANALYTICS] Recording event: {event_type} - {metadata}")
        return EventConfirmation(
            event_id=f"event-{event_type}",
            status="recorded"
        )
