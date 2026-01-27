"""Conversation controller"""
from fastapi import APIRouter, Header, Query
from typing import Optional
from ...application.services.list_conversations_service import ListConversationsApplicationService
from ...application.services.get_conversation_service import GetConversationApplicationService
from ...application.services.escalate_conversation_service import EscalateConversationApplicationService
from ...application.dtos.requests import EscalateConversationRequest
from ...application.dtos.responses import ConversationListResponse, ConversationResponse, EscalationResponse


router = APIRouter(prefix="/api/v1/chat/conversations", tags=["conversations"])


# Dependency injection will be handled in main.py
_list_service: Optional[ListConversationsApplicationService] = None
_get_service: Optional[GetConversationApplicationService] = None
_escalate_service: Optional[EscalateConversationApplicationService] = None


def init_conversation_controller(
    list_service: ListConversationsApplicationService,
    get_service: GetConversationApplicationService,
    escalate_service: EscalateConversationApplicationService
):
    """Initialize controller with services"""
    global _list_service, _get_service, _escalate_service
    _list_service = list_service
    _get_service = get_service
    _escalate_service = escalate_service


@router.get("", response_model=ConversationListResponse)
async def list_conversations(
    authorization: str = Header(...),
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0)
):
    """List user's conversations"""
    token = authorization.replace("Bearer ", "")
    return _list_service.execute(token=token, limit=limit, offset=offset)


@router.get("/{conversation_id}", response_model=ConversationResponse)
async def get_conversation(
    conversation_id: str,
    authorization: str = Header(...)
):
    """Get conversation by ID"""
    token = authorization.replace("Bearer ", "")
    return _get_service.execute(conversation_id_str=conversation_id, token=token)


@router.post("/{conversation_id}/escalate", response_model=EscalationResponse)
async def escalate_conversation(
    conversation_id: str,
    request: EscalateConversationRequest,
    authorization: str = Header(...)
):
    """Escalate conversation to human support"""
    token = authorization.replace("Bearer ", "")
    return _escalate_service.execute(
        conversation_id_str=conversation_id,
        request=request,
        token=token
    )
