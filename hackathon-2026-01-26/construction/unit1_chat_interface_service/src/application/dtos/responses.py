"""Response DTOs"""
from dataclasses import dataclass
from datetime import datetime
from typing import List, Optional


@dataclass
class DocumentationLinkResponse:
    """Documentation link response"""
    title: str
    url: str
    description: str
    source: str
    format: str
    relevance: float


@dataclass
class FeedbackResponse:
    """Feedback response"""
    answered_question: bool
    problem_solved: bool
    submitted_at: str


@dataclass
class MessageResponse:
    """Message response"""
    message_id: str
    conversation_id: str
    role: str
    content: str
    timestamp: str
    has_screenshot: bool
    screenshot_url: Optional[str] = None
    documentation_links: List[DocumentationLinkResponse] = None
    feedback: Optional[FeedbackResponse] = None

    def __post_init__(self):
        if self.documentation_links is None:
            self.documentation_links = []


@dataclass
class ConversationResponse:
    """Conversation response"""
    conversation_id: str
    title: Optional[str]
    status: str
    created_at: str
    updated_at: str
    messages: List[MessageResponse]


@dataclass
class ConversationListItemResponse:
    """Conversation list item response"""
    conversation_id: str
    title: Optional[str]
    status: str
    last_message_at: Optional[str]
    message_count: int


@dataclass
class ConversationListResponse:
    """Conversation list response"""
    conversations: List[ConversationListItemResponse]
    total: int


@dataclass
class EscalationResponse:
    """Escalation response"""
    conversation_id: str
    status: str
    escalated_at: str
    message: str
