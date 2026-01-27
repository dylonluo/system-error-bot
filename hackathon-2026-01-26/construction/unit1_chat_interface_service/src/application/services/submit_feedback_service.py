"""Submit feedback application service"""
from datetime import datetime
from ...domain.value_objects.conversation_id import ConversationId
from ...domain.value_objects.message_id import MessageId
from ...domain.repositories.conversation_repository import IConversationRepository
from ...domain.events.domain_events import FeedbackSubmitted
from ...infrastructure.events.in_memory_event_publisher import InMemoryEventPublisher
from ..clients.access_control_client import AccessControlClient
from ..clients.communication_analytics_client import CommunicationAnalyticsClient
from ..dtos.requests import SubmitFeedbackRequest
from ..dtos.responses import FeedbackResponse


class SubmitFeedbackApplicationService:
    """Application service for submitting feedback"""

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
        request: SubmitFeedbackRequest,
        token: str
    ) -> FeedbackResponse:
        """Execute submit feedback use case"""
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

        # 4. Find message
        message_id = MessageId.from_string(request.message_id)
        message = conversation.find_message(message_id)
        if message is None:
            raise ValueError(f"Message {request.message_id} not found")

        # 5. Submit feedback
        message.submit_feedback(
            answered_question=request.answered_question,
            problem_solved=request.problem_solved
        )

        # 6. Save conversation
        self._repository.save(conversation)

        # 7. Publish event
        self._event_publisher.publish(FeedbackSubmitted(
            conversation_id=conversation_id,
            message_id=message_id,
            answered_question=request.answered_question,
            problem_solved=request.problem_solved,
            occurred_at=datetime.utcnow()
        ))

        # 8. Record analytics
        self._analytics_client.record_event(
            event_type="feedback_submitted",
            metadata={
                "conversation_id": conversation_id_str,
                "message_id": request.message_id,
                "answered_question": request.answered_question,
                "problem_solved": request.problem_solved
            }
        )

        # 9. Return response
        return FeedbackResponse(
            answered_question=request.answered_question,
            problem_solved=request.problem_solved,
            submitted_at=message.feedback.submitted_at.isoformat()
        )
