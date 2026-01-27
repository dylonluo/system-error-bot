import re
from typing import Dict
from ..value_objects import Intent, IntentType


class IntentDetectionService:
    """Detects user intent from query text."""

    # NetSuite/TMS keywords
    NETSUITE_KEYWORDS = ["netsuite", "ns_", "suitescript", "saved search", "workflow"]
    TMS_KEYWORDS = ["tms", "tms-error", "transportation", "shipment", "carrier"]
    ERROR_PATTERNS = [r"NS_\w+", r"TMS-ERROR-\d+", r"error", r"failed", r"exception"]
    TASK_KEYWORDS = ["create", "update", "delete", "configure", "setup", "how to", "how do i"]

    def detect_intent(self, query_text: str) -> Intent:
        """Detect intent from query text."""
        text_lower = query_text.lower()
        entities = self.extract_entities(query_text)

        # Check for error patterns first
        if self._has_error_pattern(query_text):
            return Intent(
                intent_type=IntentType.ERROR_TROUBLESHOOTING,
                confidence=0.9,
                entities=entities,
            )

        # Check for task keywords
        if self._has_task_keywords(text_lower):
            if self._has_system_keywords(text_lower):
                return Intent(
                    intent_type=IntentType.TASK_GUIDANCE,
                    confidence=0.85,
                    entities=entities,
                )

        # Check for general NetSuite/TMS questions
        if self._has_system_keywords(text_lower):
            return Intent(
                intent_type=IntentType.GENERAL_QUESTION,
                confidence=0.75,
                entities=entities,
            )

        # Off-topic if no relevant keywords found
        return Intent(
            intent_type=IntentType.OFF_TOPIC,
            confidence=0.95,
            entities={},
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

        return entities

    def _has_error_pattern(self, text: str) -> bool:
        for pattern in self.ERROR_PATTERNS:
            if re.search(pattern, text, re.IGNORECASE):
                return True
        return False

    def _has_task_keywords(self, text_lower: str) -> bool:
        return any(kw in text_lower for kw in self.TASK_KEYWORDS)

    def _has_system_keywords(self, text_lower: str) -> bool:
        all_keywords = self.NETSUITE_KEYWORDS + self.TMS_KEYWORDS
        return any(kw in text_lower for kw in all_keywords)
