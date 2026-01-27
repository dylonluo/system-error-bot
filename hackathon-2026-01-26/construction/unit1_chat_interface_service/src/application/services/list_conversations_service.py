"""List conversations application service"""
from ..clients.access_control_client import AccessControlClient
from ...domain.repositories.conversation_repository import IConversationRepository
from ..dtos.responses import ConversationListResponse, ConversationListItemResponse


class ListConversationsApplicationService:
    """Application service for listing conversations"""

    def __init__(
        self,
        repository: IConversationRepository,
        access_control_client: AccessControlClient
    ):
        self._repository = repository
        self._access_control_client = access_control_client

    def execute(self, token: str, limit: int = 20, offset: int = 0) -> ConversationListResponse:
        """Execute list conversations use case"""
        # 1. Validate authentication
        user = self._access_control_client.validate_token(token)

        # 2. Retrieve user's conversations
        conversations = self._repository.find_by_user_id(
            user_id=user.user_id,
            limit=limit,
            offset=offset
        )

        # 3. Build response
        conversation_items = []
        for conv in conversations:
            conversation_items.append(ConversationListItemResponse(
                conversation_id=str(conv.conversation_id),
                title=conv.title,
                status=conv.status.value,
                last_message_at=conv.last_message_at.isoformat() if conv.last_message_at else None,
                message_count=len(conv.messages)
            ))

        return ConversationListResponse(
            conversations=conversation_items,
            total=len(conversation_items)
        )
