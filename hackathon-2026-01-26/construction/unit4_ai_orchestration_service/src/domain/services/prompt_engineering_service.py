from typing import List
from ..value_objects import Prompt, Intent, IntentType
from ..entities import ContextMessage


class PromptEngineeringService:
    """Builds optimized prompts for AI provider."""

    SYSTEM_PROMPT = """You are a helpful documentation assistant for NetSuite and TMS (Transportation Management System).
Your role is to provide accurate, concise answers and relevant documentation links.
Focus on troubleshooting errors, guiding users through tasks, and answering system-related questions.
Always be professional and helpful."""

    def build_prompt(
        self,
        query_text: str,
        intent: Intent,
        context_messages: List[ContextMessage],
    ) -> Prompt:
        """Build a complete prompt for the AI provider."""
        system_prompt = self._build_system_prompt(intent)
        user_prompt = self._build_user_prompt(query_text, intent)
        context = self._format_context(context_messages)

        return Prompt(
            system_prompt=system_prompt,
            user_prompt=user_prompt,
            context=context,
            temperature=0.3,
            max_tokens=500,
        )

    def _build_system_prompt(self, intent: Intent) -> str:
        """Build system prompt based on intent."""
        base = self.SYSTEM_PROMPT
        
        if intent.intent_type == IntentType.ERROR_TROUBLESHOOTING:
            base += "\nFocus on error resolution steps and common causes."
        elif intent.intent_type == IntentType.TASK_GUIDANCE:
            base += "\nProvide step-by-step instructions."
        
        return base

    def _build_user_prompt(self, query_text: str, intent: Intent) -> str:
        """Build user prompt with intent context."""
        prompt = query_text
        
        if intent.entities.get("error_code"):
            prompt = f"[Error Code: {intent.entities['error_code']}] {prompt}"
        
        return prompt

    def _format_context(self, messages: List[ContextMessage]) -> List[str]:
        """Format context messages for prompt."""
        return [
            f"{msg.role.value}: {msg.content}"
            for msg in messages[-5:]  # Last 5 messages
        ]
