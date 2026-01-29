import re
from typing import Dict
from ..value_objects import Intent, IntentType


class IntentDetectionService:
    """Detects user intent from query text.
    
    Distinguishes between:
    - NS/TMS related questions (should search documentation)
    - Off-topic/general chat (should politely decline)
    """

    # Error-related patterns
    ERROR_PATTERNS = [
        r"error", r"failed", r"exception", r"issue", r"problem", 
        r"not working", r"doesn't work", r"can't", r"cannot", r"unable",
        r"NS_\w+", r"TMS-ERROR-\d+", r"ERR[-_]?\d+",
    ]
    
    # Task/How-to patterns
    TASK_KEYWORDS = [
        "create", "update", "delete", "configure", "setup", "set up",
        "how to", "how do i", "how can i", "steps to", "guide",
        "process", "procedure", "instructions", "help me",
    ]
    
    # Question patterns
    QUESTION_KEYWORDS = [
        "what is", "what are", "why", "when", "where", "which",
        "explain", "describe", "tell me", "show me",
    ]
    
    # Domain-specific keywords that indicate NS/TMS related queries
    DOMAIN_KEYWORDS = [
        # NetSuite
        "netsuite", "ns", "ns_", "netsuit",
        # TMS
        "tms", "transport", "shipping", "shipment", "delivery", "carrier",
        # Business processes
        "invoice", "order", "sales order", "purchase order", "po", "so",
        "fulfillment", "fulfill", "inventory", "stock", "warehouse",
        "billing", "payment", "vendor", "customer", "account",
        "sync", "integration", "api", "import", "export",
        "return", "rma", "refund", "credit memo",
        # Technical
        "script", "workflow", "saved search", "record", "field",
        "transaction", "item", "sku", "lot", "serial",
        # Errors
        "error", "fail", "issue", "problem", "bug", "fix",
    ]
    
    # Off-topic patterns (general chat, greetings, unrelated questions)
    OFF_TOPIC_PATTERNS = [
        r"^(hi|hello|hey|good morning|good afternoon|good evening)\b",
        r"^how are you",
        r"^what('s| is) your name",
        r"^who are you",
        r"^(thanks|thank you|thx)\s*$",
        r"^(bye|goodbye|see you)\b",
        r"\b(weather|news|joke|story|recipe|movie|music|game)\b",
        r"^(can you|do you|are you)\s+(help|assist|talk|chat)\b",
        r"^tell me (a joke|about yourself|something)",
    ]

    def detect_intent(self, query_text: str) -> Intent:
        """Detect intent from query text."""
        text_lower = query_text.lower().strip()
        entities = self.extract_entities(query_text)

        # Check for off-topic patterns first (greetings, general chat)
        if self._is_off_topic(text_lower):
            return Intent(
                intent_type=IntentType.OFF_TOPIC,
                confidence=0.95,
                entities={},
            )

        # Check if query contains domain-specific keywords
        has_domain_keywords = self._has_domain_keywords(text_lower)

        # Check for error patterns (highest priority if domain-related)
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

        # Check for general questions with domain keywords
        if self._has_question_keywords(text_lower) and has_domain_keywords:
            return Intent(
                intent_type=IntentType.GENERAL_QUESTION,
                confidence=0.8,
                entities=entities,
            )

        # If has domain keywords, treat as general question
        if has_domain_keywords:
            return Intent(
                intent_type=IntentType.GENERAL_QUESTION,
                confidence=0.7,
                entities=entities,
            )

        # Very short queries without domain keywords are likely off-topic
        if len(text_lower.split()) <= 5 and not has_domain_keywords:
            return Intent(
                intent_type=IntentType.OFF_TOPIC,
                confidence=0.85,
                entities={},
            )
        
        # Default: treat as general question but with lower confidence
        # This allows RAG to try, but if no docs found, will handle appropriately
        return Intent(
            intent_type=IntentType.GENERAL_QUESTION,
            confidence=0.5,
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

    def _is_off_topic(self, text_lower: str) -> bool:
        """Check if query is clearly off-topic (greetings, general chat)."""
        for pattern in self.OFF_TOPIC_PATTERNS:
            if re.search(pattern, text_lower, re.IGNORECASE):
                return True
        return False

    def _has_domain_keywords(self, text_lower: str) -> bool:
        """Check if query contains NS/TMS domain-specific keywords."""
        return any(kw in text_lower for kw in self.DOMAIN_KEYWORDS)

    def _has_error_pattern(self, text: str) -> bool:
        for pattern in self.ERROR_PATTERNS:
            if re.search(pattern, text, re.IGNORECASE):
                return True
        return False

    def _has_task_keywords(self, text_lower: str) -> bool:
        return any(kw in text_lower for kw in self.TASK_KEYWORDS)

    def _has_question_keywords(self, text_lower: str) -> bool:
        return any(kw in text_lower for kw in self.QUESTION_KEYWORDS)
