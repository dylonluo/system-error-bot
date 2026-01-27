from ...domain.services import IntentDetectionService
from ..dtos import DetectIntentRequest, DetectIntentResponse


class DetectIntentService:
    """Application service for intent detection."""

    def __init__(self, intent_detection_service: IntentDetectionService):
        self._intent_service = intent_detection_service

    def execute(self, request: DetectIntentRequest) -> DetectIntentResponse:
        """Detect intent from query text."""
        intent = self._intent_service.detect_intent(request.query)

        return DetectIntentResponse(
            intent=intent.intent_type.value,
            confidence=intent.confidence,
            entities=dict(intent.entities),
        )
