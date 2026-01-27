"""Message entity"""
from datetime import datetime
from typing import Optional, List
from ..value_objects.message_id import MessageId
from ..value_objects.message_role import MessageRole
from ..value_objects.screenshot import Screenshot
from ..value_objects.feedback import Feedback
from ..value_objects.documentation_link import DocumentationLink


class Message:
    """Message entity within Conversation aggregate"""

    def __init__(
        self,
        message_id: MessageId,
        role: MessageRole,
        content: str,
        timestamp: datetime,
        screenshot: Optional[Screenshot] = None,
        documentation_links: Optional[List[DocumentationLink]] = None,
        feedback: Optional[Feedback] = None
    ):
        if not content:
            raise ValueError("Message content cannot be empty")

        self._message_id = message_id
        self._role = role
        self._content = content
        self._timestamp = timestamp
        self._screenshot = screenshot
        self._documentation_links = documentation_links or []
        self._feedback = feedback

    @property
    def message_id(self) -> MessageId:
        return self._message_id

    @property
    def role(self) -> MessageRole:
        return self._role

    @property
    def content(self) -> str:
        return self._content

    @property
    def timestamp(self) -> datetime:
        return self._timestamp

    @property
    def screenshot(self) -> Optional[Screenshot]:
        return self._screenshot

    @property
    def documentation_links(self) -> List[DocumentationLink]:
        return self._documentation_links.copy()

    @property
    def feedback(self) -> Optional[Feedback]:
        return self._feedback

    def submit_feedback(self, answered_question: bool, problem_solved: bool) -> None:
        """Submit feedback on this message"""
        if self._feedback is not None:
            raise ValueError("Feedback already submitted for this message")

        if not self._role.is_assistant():
            raise ValueError("Feedback can only be submitted for assistant messages")

        self._feedback = Feedback(
            answered_question=answered_question,
            problem_solved=problem_solved,
            submitted_at=datetime.utcnow()
        )

    def has_feedback(self) -> bool:
        """Check if message has feedback"""
        return self._feedback is not None

    def has_screenshot(self) -> bool:
        """Check if message has screenshot"""
        return self._screenshot is not None

    def get_documentation_links(self) -> List[DocumentationLink]:
        """Get documentation links"""
        return self.documentation_links
