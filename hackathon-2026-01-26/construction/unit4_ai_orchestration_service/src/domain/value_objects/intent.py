from dataclasses import dataclass, field
from enum import Enum
from typing import Dict


class IntentType(Enum):
    ERROR_TROUBLESHOOTING = "error_troubleshooting"
    TASK_GUIDANCE = "task_guidance"
    GENERAL_QUESTION = "general_question"
    OFF_TOPIC = "off_topic"


@dataclass(frozen=True)
class Intent:
    """Detected intent from user query."""
    intent_type: IntentType
    confidence: float
    entities: Dict[str, str] = field(default_factory=dict)

    def __post_init__(self):
        if not 0.0 <= self.confidence <= 1.0:
            raise ValueError("Confidence must be between 0.0 and 1.0")

    def is_off_topic(self) -> bool:
        return self.intent_type == IntentType.OFF_TOPIC

    def is_error_related(self) -> bool:
        return self.intent_type == IntentType.ERROR_TROUBLESHOOTING
