from typing import List
from ..value_objects import AIResponse, Intent, ConfidenceScore
from .response_generation_service import DocumentLink


class ConfidenceCalculationService:
    """Calculates confidence score for AI responses."""

    # Weights for confidence calculation
    AI_CONFIDENCE_WEIGHT = 0.5
    DOCUMENT_RELEVANCE_WEIGHT = 0.3
    INTENT_CONFIDENCE_WEIGHT = 0.2

    ESCALATION_THRESHOLD = 0.5

    def calculate_confidence(
        self,
        ai_response: AIResponse,
        documents: List[DocumentLink],
        intent: Intent,
    ) -> ConfidenceScore:
        """Calculate overall confidence score."""
        ai_score = self._score_ai_confidence(ai_response)
        doc_score = self._score_document_relevance(documents)
        intent_score = self._score_intent_confidence(intent)

        total = (
            ai_score * self.AI_CONFIDENCE_WEIGHT
            + doc_score * self.DOCUMENT_RELEVANCE_WEIGHT
            + intent_score * self.INTENT_CONFIDENCE_WEIGHT
        )

        return ConfidenceScore(value=round(total, 2))

    def _score_ai_confidence(self, ai_response: AIResponse) -> float:
        """Score based on AI response quality."""
        # Simple heuristic: longer responses with content are more confident
        content_length = len(ai_response.content)
        if content_length < 50:
            return 0.4
        elif content_length < 200:
            return 0.7
        else:
            return 0.9

    def _score_document_relevance(self, documents: List[DocumentLink]) -> float:
        """Score based on document relevance."""
        if not documents:
            return 0.3
        
        avg_relevance = sum(d.relevance for d in documents) / len(documents)
        return min(avg_relevance, 1.0)

    def _score_intent_confidence(self, intent: Intent) -> float:
        """Score based on intent detection confidence."""
        return intent.confidence
