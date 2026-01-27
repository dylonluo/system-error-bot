"""Feedback value object"""
from dataclasses import dataclass
from datetime import datetime


@dataclass(frozen=True)
class Feedback:
    """User feedback on an assistant message"""
    answered_question: bool
    problem_solved: bool
    submitted_at: datetime

    def is_positive(self) -> bool:
        """Check if feedback is positive"""
        return self.answered_question and self.problem_solved

    def was_helpful(self) -> bool:
        """Check if response was helpful"""
        return self.answered_question or self.problem_solved
