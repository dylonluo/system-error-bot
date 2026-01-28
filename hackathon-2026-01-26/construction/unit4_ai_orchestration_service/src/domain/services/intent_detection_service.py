import re
from typing import Dict
from ..value_objects import Intent, IntentType


class IntentDetectionService:
    """Detects user intent from query text.
    
    Now works with any documentation, not just NS/TMS specific.
    """

    # Error-related patterns - expanded
    ERROR_PATTERNS = [
        r"error", r"failed", r"exception", r"issue", r"problem", 
        r"not working", r"doesn't work", r"can't", r"cannot", r"unable",
        r"won't", r"doesn't", r"NS_\w+", r"TMS-ERROR-\d+", r"ERR[-_]?\d+",
    ]
    
    # Task/How-to patterns - expanded
    TASK_KEYWORDS = [
        "create", "update", "delete", "configure", "setup", "set up",
        "how to", "how do i", "how can i", "steps to", "guide",
        "process", "procedure", "instructions", "help me",
    ]
    
    # Question patterns - expanded
    QUESTION_KEYWORDS = [
        "what is", "what are", "why", "when", "where", "which",
        "explain", "describe", "tell me", "show me", "what",
    ]

    def detect_intent(self, query_text: str) -> Intent:
        """Detect intent from query text - works with any documentation."""
        text_lower = query_text.lower()
        entities = self.extract_entities(query_text)

        # Check for error patterns first (highest priority)
        if self._has_error_pattern(query_text):
            return Intent(
                intent_type=IntentType.ERROR_TROUBLESHOOTING,
                confidence=0.9,
                entities=entities,
            )

        # Check for task/how-to keywords
        if self._has_task_keywords(text_lower):
            return Intent(
                intent_type=IntentType.TASK_GUIDANCE,
                confidence=0.85,
                entities=entities,
            )

        # Check for general questions
        if self._has_question_keywords(text_lower):
            return Intent(
                intent_type=IntentType.GENERAL_QUESTION,
                confidence=0.8,
                entities=entities,
            )

        # Default to general question (let the document search determine relevance)
        # Only mark as off-topic for very short or clearly irrelevant queries
        if len(query_text.strip()) < 3:
            return Intent(
                intent_type=IntentType.OFF_TOPIC,
                confidence=0.95,
                entities={},
            )
        
        # Assume it's a general question - let RAG handle it
        return Intent(
            intent_type=IntentType.GENERAL_QUESTION,
            confidence=0.7,
            entities=entities,
        )

    def extract_entities(self, query_text: str) -> Dict[str, str]:
        """Extract entities like error codes from query."""
        entities = {}
        
        # Extract NS_ error codes
        ns_errors = re.findall(r"NS_\w+", query_text, re.IGNORECASE)
        if ns_errors:
            entities["error_code"] = ns_errors[0].upper()

        # Extract TMS error codes
        tms_errors = re.findall(r"TMS-ERROR-\d+", query_text, re.IGNORECASE)
        if tms_errors:
            entities["error_code"] = tms_errors[0].upper()
        
        # Extract generic error codes (ERR-123, ERR_456, etc.)
        generic_errors = re.findall(r"ERR[-_]?\d+", query_text, re.IGNORECASE)
        if generic_errors and "error_code" not in entities:
            entities["error_code"] = generic_errors[0].upper()

        return entities

    def _has_error_pattern(self, text: str) -> bool:
        for pattern in self.ERROR_PATTERNS:
            if re.search(pattern, text, re.IGNORECASE):
                return True
        return False

    def _has_task_keywords(self, text_lower: str) -> bool:
        return any(kw in text_lower for kw in self.TASK_KEYWORDS)

    def _has_question_keywords(self, text_lower: str) -> bool:
        return any(kw in text_lower for kw in self.QUESTION_KEYWORDS)
