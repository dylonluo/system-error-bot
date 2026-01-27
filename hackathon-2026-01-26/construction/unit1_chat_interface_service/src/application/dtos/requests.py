"""Request DTOs"""
from dataclasses import dataclass
from typing import Optional


@dataclass
class SubmitMessageRequest:
    """Request to submit a message"""
    query_text: str
    conversation_id: Optional[str] = None
    screenshot_filename: Optional[str] = None
    screenshot_content: Optional[bytes] = None
    screenshot_mime_type: Optional[str] = None


@dataclass
class SubmitFeedbackRequest:
    """Request to submit feedback"""
    message_id: str
    answered_question: bool
    problem_solved: bool


@dataclass
class EscalateConversationRequest:
    """Request to escalate conversation"""
    reason: Optional[str] = None
