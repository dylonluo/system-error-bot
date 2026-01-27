"""Get conversation application service"""
from ...domain.value_objects.conversation_id import ConversationId
from ...domain.repositories.conversation_repository import IConversationRepository
from ..clients.access_control_client import AccessControlClient
from ..dtos.responses import ConversationResponse, MessageResponse, DocumentationLinkResponse, FeedbackResponse


class GetConversationApplicationService:
    """Application service for retrieving a conversation"""

    def __init__(
        self,
        repository: IConversationRepository,
        access_control_client: AccessControlClient
    ):
        self._repository = repository
        self._access_control_client = access_control_client

    def execute(self, conversation_id_str: str, token: str) -> ConversationResponse:
        """Execute get conversation use case"""
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

        # 4. Build response
        messages = []
        for message in conversation.messages:
            doc_links = [
                DocumentationLinkResponse(
                    title=link.title,
                    url=link.url,
                    description=link.description,
                    source=link.source,
                    format=link.format,
                    relevance=link.relevance
                )
                for link in message.documentation_links
            ]

            feedback = None
            if message.feedback:
                feedback = FeedbackResponse(
                    answered_question=message.feedback.answered_question,
                    problem_solved=message.feedback.problem_solved,
                    submitted_at=message.feedback.submitted_at.isoformat()
                )

            messages.append(MessageResponse(
                message_id=str(message.message_id),
                conversation_id=conversation_id_str,
                role=message.role.value,
                content=message.content,
                timestamp=message.timestamp.isoformat(),
                has_screenshot=message.has_screenshot(),
                screenshot_url=message.screenshot.storage_url if message.screenshot else None,
                documentation_links=doc_links,
                feedback=feedback
            ))

        return ConversationResponse(
            conversation_id=str(conversation.conversation_id),
            title=conversation.title,
            status=conversation.status.value,
            created_at=conversation.created_at.isoformat(),
            updated_at=conversation.updated_at.isoformat(),
            messages=messages
        )
