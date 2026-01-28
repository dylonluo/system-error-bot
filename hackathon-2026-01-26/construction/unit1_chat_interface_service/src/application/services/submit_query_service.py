"""Submit query application service"""
from datetime import datetime
from typing import Optional
from ...domain.aggregates.conversation import Conversation
from ...domain.value_objects.conversation_id import ConversationId
from ...domain.value_objects.message_role import MessageRole
from ...domain.value_objects.screenshot import Screenshot
from ...domain.value_objects.documentation_link import DocumentationLink
from ...domain.repositories.conversation_repository import IConversationRepository
from ...domain.services.screenshot_validation_service import ScreenshotValidationService
from ...domain.events.domain_events import ConversationCreated, MessageAdded
from ...infrastructure.storage.in_memory_screenshot_storage import InMemoryScreenshotStorage
from ...infrastructure.events.in_memory_event_publisher import InMemoryEventPublisher
from ..clients.access_control_client import AccessControlClient
from ..clients.ai_orchestration_client import AIOrchestrationClient
from ..clients.communication_analytics_client import CommunicationAnalyticsClient
from ..dtos.requests import SubmitMessageRequest
from ..dtos.responses import MessageResponse, DocumentationLinkResponse


class SubmitQueryApplicationService:
    """Application service for submitting queries"""

    def __init__(
        self,
        repository: IConversationRepository,
        screenshot_storage: InMemoryScreenshotStorage,
        event_publisher: InMemoryEventPublisher,
        access_control_client: AccessControlClient,
        ai_client: AIOrchestrationClient,
        analytics_client: CommunicationAnalyticsClient,
        screenshot_validation_service: ScreenshotValidationService
    ):
        self._repository = repository
        self._screenshot_storage = screenshot_storage
        self._event_publisher = event_publisher
        self._access_control_client = access_control_client
        self._ai_client = ai_client
        self._analytics_client = analytics_client
        self._screenshot_validation_service = screenshot_validation_service

    def execute(self, request: SubmitMessageRequest, token: str) -> MessageResponse:
        """Execute submit query use case"""
        # 0. Validate query is not empty
        if not request.query_text or not request.query_text.strip():
            raise ValueError("Query text cannot be empty")
        
        # 1. Validate authentication
        user = self._access_control_client.validate_token(token)

        # 2. Handle screenshot if present
        screenshot: Optional[Screenshot] = None
        if request.screenshot_content:
            screenshot = self._handle_screenshot(
                request.screenshot_content,
                request.screenshot_filename,
                request.screenshot_mime_type
            )

        # 3. Get or create conversation
        conversation, is_new = self._get_or_create_conversation(
            request.conversation_id,
            user.user_id
        )

        # 4. Add user message
        user_message = conversation.add_message(
            content=request.query_text,
            role=MessageRole.USER,
            screenshot=screenshot
        )

        # 5. Save conversation
        self._repository.save(conversation)

        # 6. Publish ConversationCreated event if new
        if is_new:
            self._event_publisher.publish(ConversationCreated(
                conversation_id=conversation.conversation_id,
                user_id=user.user_id,
                occurred_at=datetime.utcnow()
            ))

        # 7. Publish MessageAdded event for user message
        self._event_publisher.publish(MessageAdded(
            conversation_id=conversation.conversation_id,
            message_id=user_message.message_id,
            role=MessageRole.USER,
            has_screenshot=screenshot is not None,
            occurred_at=datetime.utcnow()
        ))

        # 8. Process query with AI
        ai_response = self._ai_client.process_query(
            query=request.query_text,
            context=self._build_context(conversation),
            user_id=user.user_id,
            conversation_id=conversation.conversation_id  # Pass conversation ID for follow-up detection
        )

        # 9. Convert AI documentation links to domain objects
        doc_links = [
            DocumentationLink(
                title=link.title,
                url=link.url,
                description=link.description,
                source=link.source,
                format=link.format,
                relevance=link.relevance
            )
            for link in ai_response.documentation_links
        ]

        # 10. Add assistant response
        assistant_message = conversation.add_message(
            content=ai_response.content,
            role=MessageRole.ASSISTANT,
            documentation_links=doc_links
        )

        # 11. Save conversation again
        self._repository.save(conversation)

        # 12. Publish MessageAdded event for assistant message
        self._event_publisher.publish(MessageAdded(
            conversation_id=conversation.conversation_id,
            message_id=assistant_message.message_id,
            role=MessageRole.ASSISTANT,
            has_screenshot=False,
            occurred_at=datetime.utcnow()
        ))

        # 13. Record analytics
        self._analytics_client.record_event(
            event_type="message_submitted",
            metadata={
                "conversation_id": str(conversation.conversation_id),
                "user_id": str(user.user_id),
                "has_screenshot": screenshot is not None
            }
        )

        # 14. Return response
        return self._build_message_response(assistant_message, str(conversation.conversation_id))

    def _handle_screenshot(
        self,
        content: bytes,
        filename: str,
        mime_type: str
    ) -> Screenshot:
        """Handle screenshot upload"""
        # Sanitize filename
        sanitized_filename = self._screenshot_validation_service.sanitize_filename(filename)

        # Create screenshot value object
        screenshot = Screenshot(
            filename=sanitized_filename,
            storage_url="",  # Will be set after storage
            mime_type=mime_type,
            size=len(content),
            uploaded_at=datetime.utcnow()
        )

        # Validate
        validation_result = self._screenshot_validation_service.validate_screenshot(screenshot)
        if not validation_result.is_valid:
            raise ValueError(validation_result.error_message)

        # Store
        storage_url = self._screenshot_storage.store(content, sanitized_filename, mime_type)

        # Return screenshot with storage URL
        return Screenshot(
            filename=sanitized_filename,
            storage_url=storage_url,
            mime_type=mime_type,
            size=len(content),
            uploaded_at=screenshot.uploaded_at
        )

    def _get_or_create_conversation(
        self,
        conversation_id_str: Optional[str],
        user_id
    ) -> tuple[Conversation, bool]:
        """Get existing conversation or create new one"""
        if conversation_id_str:
            # Retrieve existing conversation
            conversation_id = ConversationId.from_string(conversation_id_str)
            conversation = self._repository.find_by_id(conversation_id)
            if conversation is None:
                raise ValueError(f"Conversation {conversation_id_str} not found")
            if not conversation.is_owned_by(user_id):
                raise ValueError("User does not own this conversation")
            return conversation, False
        else:
            # Create new conversation
            conversation = Conversation(
                conversation_id=ConversationId.generate(),
                user_id=user_id
            )
            return conversation, True

    def _build_context(self, conversation: Conversation) -> str:
        """Build context from conversation history"""
        recent_messages = conversation.get_recent_messages(limit=5)
        context_parts = []
        for msg in recent_messages:
            context_parts.append(f"{msg.role.value}: {msg.content}")
        return "\n".join(context_parts)

    def _build_message_response(self, message, conversation_id: str) -> MessageResponse:
        """Build message response DTO"""
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

        return MessageResponse(
            message_id=str(message.message_id),
            conversation_id=conversation_id,
            role=message.role.value,
            content=message.content,
            timestamp=message.timestamp.isoformat(),
            has_screenshot=message.has_screenshot(),
            screenshot_url=message.screenshot.storage_url if message.screenshot else None,
            documentation_links=doc_links,
            feedback=None
        )
