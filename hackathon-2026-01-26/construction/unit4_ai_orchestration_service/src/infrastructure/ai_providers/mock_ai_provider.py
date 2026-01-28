from abc import ABC, abstractmethod
from ...domain.value_objects import Prompt, AIResponse


class IAIProvider(ABC):
    """Interface for AI providers."""

    @abstractmethod
    def generate_response(self, prompt: Prompt) -> AIResponse:
        pass

    @abstractmethod
    def is_available(self) -> bool:
        pass

    @abstractmethod
    def get_model_name(self) -> str:
        pass


class MockAIProvider(IAIProvider):
    """Mock AI provider for testing and demo."""

    MODEL_NAME = "mock-ai-v1"

    # Pattern-based responses
    RESPONSES = {
        "error": "Based on the error code, here are the recommended troubleshooting steps:\n1. Check the system logs for detailed error messages\n2. Verify your permissions and access levels\n3. Ensure all required fields are populated\n4. Try clearing the cache and retrying the operation",
        "create": "To create this in NetSuite/TMS, follow these steps:\n1. Navigate to the appropriate module\n2. Click 'New' or 'Create'\n3. Fill in the required fields\n4. Save and verify the record was created successfully",
        "configure": "To configure this setting:\n1. Go to Setup > Configuration\n2. Locate the relevant section\n3. Adjust the parameters as needed\n4. Save your changes and test the configuration",
        "default": "Here's what I found about your question:\nThis is a common topic in NetSuite/TMS. Please refer to the documentation links below for detailed information and best practices.",
    }

    # Follow-up responses when user says previous answer didn't help
    FOLLOWUP_RESPONSES = {
        "not_working": (
            "I understand the previous solution didn't work for you. To help you better, could you please tell me:\n\n"
            "1. **What specific step failed?** (e.g., step 2 didn't work)\n"
            "2. **What error message did you see?** (if any)\n"
            "3. **What exactly happened?** (e.g., nothing changed, got a different error)\n\n"
            "With these details, I can search for more specific documentation or escalate to the right team."
        ),
        "need_more_help": (
            "I see you need more assistance. Let me try a different approach:\n\n"
            "- Could you describe what you're trying to achieve in more detail?\n"
            "- What have you already tried?\n"
            "- Are there any specific error codes or messages?\n\n"
            "If this issue is urgent, I recommend escalating to human support for faster resolution."
        ),
        "clarification": (
            "I want to make sure I understand your question correctly. Based on our conversation, "
            "it seems you're asking about a specific issue. Could you:\n\n"
            "1. Confirm what system/module you're working with\n"
            "2. Describe the expected vs actual behavior\n"
            "3. Share any relevant order/invoice numbers (if applicable)\n\n"
            "This will help me find the most relevant documentation."
        ),
    }

    # Patterns that indicate follow-up frustration
    FOLLOWUP_PATTERNS = [
        (["not working", "doesn't work", "didn't work", "still not", "same issue", "same error"], "not_working"),
        (["tried", "already", "but", "however", "still"], "not_working"),
        (["help", "stuck", "confused", "don't understand"], "need_more_help"),
        (["what", "how", "why", "huh", "eh"], "clarification"),
    ]

    def generate_response(self, prompt: Prompt) -> AIResponse:
        """Generate a mock response based on prompt content and conversation context."""
        prompt_text = prompt.user_prompt.lower()
        
        # Check if screenshot is mentioned in the prompt
        if "screenshot" in prompt_text or "image" in prompt_text or hasattr(prompt, 'screenshot_url'):
            content = self._get_screenshot_response(prompt_text)
            return AIResponse.create(
                content=content,
                model=self.MODEL_NAME,
                tokens_used=len(content.split()) * 2,
            )
        
        # Check if this is a follow-up message by looking at context
        if prompt.context and self._is_followup_message(prompt_text, prompt.context):
            content = self._get_followup_response(prompt_text)
            return AIResponse.create(
                content=content,
                model=self.MODEL_NAME,
                tokens_used=len(content.split()) * 2,
            )
        
        # Select response based on keywords for initial queries
        if any(kw in prompt_text for kw in ["error", "failed", "exception", "ns_", "tms-error"]):
            content = self.RESPONSES["error"]
        elif any(kw in prompt_text for kw in ["create", "add", "new"]):
            content = self.RESPONSES["create"]
        elif any(kw in prompt_text for kw in ["configure", "setup", "setting"]):
            content = self.RESPONSES["configure"]
        else:
            content = self.RESPONSES["default"]

        return AIResponse.create(
            content=content,
            model=self.MODEL_NAME,
            tokens_used=len(content.split()) * 2,
        )

    def _get_screenshot_response(self, prompt_text: str) -> str:
        """Generate response acknowledging screenshot attachment."""
        # Check if there's also an error mentioned
        if any(kw in prompt_text for kw in ["error", "failed", "exception", "issue", "problem"]):
            return (
                "Thank you for sharing the screenshot. I can see you're experiencing an issue.\n\n"
                "Based on the screenshot, here's what I recommend:\n\n"
                "1. **Check the error message** - Note any specific error codes (e.g., NS_ERROR_xxx)\n"
                "2. **Verify your permissions** - Ensure you have the required access level\n"
                "3. **Review recent changes** - Check if any configuration was modified recently\n\n"
                "If you can share the exact error code or message from the screenshot, "
                "I can search for more specific documentation.\n\n"
                "Would you like to escalate this to human support for faster resolution?"
            )
        else:
            return (
                "Thank you for sharing the screenshot. I've received your image.\n\n"
                "To help you better, could you please tell me:\n\n"
                "1. **What are you trying to accomplish?** (e.g., create an order, sync data)\n"
                "2. **What specific issue are you facing?** (e.g., button not working, field missing)\n"
                "3. **Any error messages visible?** (please share the exact text if possible)\n\n"
                "This will help me find the most relevant documentation for your situation."
            )

    def _is_followup_message(self, query: str, context: list) -> bool:
        """Detect if this is a follow-up to a previous response."""
        # Must have previous conversation
        if not context or len(context) < 2:
            return False
        
        # Check if query is short (likely a follow-up)
        word_count = len(query.split())
        if word_count > 20:
            return False  # Long queries are usually new questions
        
        # Check for follow-up patterns
        for patterns, _ in self.FOLLOWUP_PATTERNS:
            if any(p in query for p in patterns):
                return True
        
        # Short message without technical keywords = likely follow-up
        technical_keywords = ["error", "invoice", "order", "netsuite", "tms", "sync", "integration"]
        if word_count <= 10 and not any(kw in query for kw in technical_keywords):
            return True
        
        return False

    def _get_followup_response(self, query: str) -> str:
        """Get appropriate follow-up response based on user's message."""
        for patterns, response_key in self.FOLLOWUP_PATTERNS:
            if any(p in query for p in patterns):
                return self.FOLLOWUP_RESPONSES[response_key]
        
        # Default follow-up
        return self.FOLLOWUP_RESPONSES["need_more_help"]

    def is_available(self) -> bool:
        return True

    def get_model_name(self) -> str:
        return self.MODEL_NAME
