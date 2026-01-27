"""Escalate conversation application service"""
from datetime import datetime
from ...domain.value_objects.conversation_id import ConversationId
from ...domain.repositories.conversation_repository import IConversationRepository
from ...domain.events.domain_events import ConversationEscalated
from ...infrastructure.events.in_memory_event_publisher import InMemoryEventPublisher
from ..clients.access_control_client import AccessControlClient
from ..clients.communication_analytics_client import CommunicationAnalyticsClient
from ..dtos.requests import EscalateConversationRequest
from ..dtos.responses import EscalationResponse


class EscalateConversationApplicationService:
    """Application service for escalating conversations"""

    def __init__(
        self,
        repository: IConversationRepository,
        event_publisher: InMemoryEventPublisher,
        access_control_client: AccessControlClient,
        analytics_client: CommunicationAnalyticsClient
    ):
        self._repository = repository
        self._event_publisher = event_publisher
        self._access_control_client = access_control_client
        self._analytics_client = analytics_client

    def execute(
        self,
        conversation_id_str: str,
        request: EscalateConversationRequest,
        token: str
    ) -> EscalationResponse:
        """Execute escalate conversation use case"""
        # 1. Validate authentication
        user = self._access_control_client.validate_token(token)

        # 2. Retrieve conversation
        conversation_id = ConversationId.from_string(conversation_id_str)
        conversation = self._repository.find_by_id(conversation_id)
        if conversation is None:
            raise ValueError(f"Conversation {conversation_id_str} not found")

        # 3. Verify ownership
        if not conversation.is_owned_by(user.user_id):
            raise ValueError("User does not own this conversation")

        # 4. Escalate conversation
        conversation.escalate_to_support(reason=request.reason)

        # 5. Save conversation
        self._repository.save(conversation)

        # 6. Build conversation history for email
        history = self._build_conversation_history(conversation)

        # 7. Send escalation email
        email_confirmation = self._analytics_client.send_escalation_email(
            conversation_id=conversation_id_str,
            user_id=user.user_id,
            conversation_history=history
        )

        # 8. Publish event
        self._event_publisher.publish(ConversationEscalated(
            conversation_id=conversation_id,
            user_id=user.user_id,
            reason=request.reason or "",
            occurred_at=datetime.utcnow()
        ))

        # 9. Record analytics
        self._analytics_client.record_event(
            event_type="conversation_escalated",
            metadata={
                "conversation_id": conversation_id_str,
                "user_id": str(user.user_id),
                "reason": request.reason
            }
        )

        # 10. Return response
        return EscalationResponse(
            conversation_id=conversation_id_str,
            status=conversation.status.value,
            escalated_at=conversation.updated_at.isoformat(),
            message=email_confirmation.message
        )

    def _build_conversation_history(self, conversation) -> str:
        """Build conversation history for email"""
        history_parts = [f"Conversation: {conversation.title or 'Untitled'}"]
        for message in conversation.messages:
            history_parts.append(f"\n{message.role.value.upper()}: {message.content}")
        return "\n".join(history_parts)
