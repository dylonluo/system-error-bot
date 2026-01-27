"""Message controller"""
from fastapi import APIRouter, Header, UploadFile, File, Form
from typing import Optional
from ...application.services.submit_query_service import SubmitQueryApplicationService
from ...application.services.submit_feedback_service import SubmitFeedbackApplicationService
from ...application.dtos.requests import SubmitMessageRequest, SubmitFeedbackRequest
from ...application.dtos.responses import MessageResponse, FeedbackResponse


router = APIRouter(prefix="/api/v1/chat/conversations", tags=["messages"])


# Dependency injection will be handled in main.py
_submit_query_service: Optional[SubmitQueryApplicationService] = None
_submit_feedback_service: Optional[SubmitFeedbackApplicationService] = None


def init_message_controller(
    submit_query_service: SubmitQueryApplicationService,
    submit_feedback_service: SubmitFeedbackApplicationService
):
    """Initialize controller with services"""
    global _submit_query_service, _submit_feedback_service
    _submit_query_service = submit_query_service
    _submit_feedback_service = submit_feedback_service


@router.post("/{conversation_id}/messages", response_model=MessageResponse)
async def submit_message(
    conversation_id: Optional[str],
    query_text: str = Form(...),
    authorization: str = Header(...),
    screenshot: Optional[UploadFile] = File(None)
):
    """Submit a message to a conversation"""
    token = authorization.replace("Bearer ", "")

    # Handle screenshot if present
    screenshot_content = None
    screenshot_filename = None
    screenshot_mime_type = None
    if screenshot:
        screenshot_content = await screenshot.read()
        screenshot_filename = screenshot.filename
        screenshot_mime_type = screenshot.content_type

    # Create request
    request = SubmitMessageRequest(
        query_text=query_text,
        conversation_id=conversation_id if conversation_id != "new" else None,
        screenshot_filename=screenshot_filename,
        screenshot_content=screenshot_content,
        screenshot_mime_type=screenshot_mime_type
    )

    return _submit_query_service.execute(request=request, token=token)


@router.post("/{conversation_id}/feedback", response_model=FeedbackResponse)
async def submit_feedback(
    conversation_id: str,
    request: SubmitFeedbackRequest,
    authorization: str = Header(...)
):
    """Submit feedback on a message"""
    token = authorization.replace("Bearer ", "")
    return _submit_feedback_service.execute(
        conversation_id_str=conversation_id,
        request=request,
        token=token
    )
