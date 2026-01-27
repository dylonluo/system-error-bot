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

    def generate_response(self, prompt: Prompt) -> AIResponse:
        """Generate a mock response based on prompt content."""
        prompt_text = prompt.user_prompt.lower()
        
        # Select response based on keywords
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
            tokens_used=len(content.split()) * 2,  # Rough estimate
        )

    def is_available(self) -> bool:
        return True

    def get_model_name(self) -> str:
        return self.MODEL_NAME
