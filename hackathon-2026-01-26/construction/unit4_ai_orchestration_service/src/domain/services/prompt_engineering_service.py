from typing import List, Optional
from ..value_objects import Prompt, Intent, IntentType
from ..entities import ContextMessage


class PromptEngineeringService:
    """Builds optimized prompts for AI provider with RAG support."""

    SYSTEM_PROMPT = """You are a helpful documentation assistant for NetSuite and TMS (Transportation Management System).
Your role is to provide accurate, concise answers based on the company's internal documentation.
Focus on troubleshooting errors, guiding users through tasks, and answering system-related questions.
Always be professional and helpful.

IMPORTANT: Base your answers primarily on the provided documentation context. If the documentation 
doesn't contain relevant information, say so and provide general guidance while suggesting 
the user escalate to human support for specific details."""

    SYSTEM_PROMPT_WITH_RAG = """You are a helpful documentation assistant for NetSuite and TMS (Transportation Management System).
Your role is to provide accurate, concise answers based on the company's internal documentation.

CRITICAL INSTRUCTIONS:
1. Base your answers PRIMARILY on the "RELEVANT DOCUMENTATION" section provided below.
2. Quote or reference specific information from the documentation when answering.
3. If the documentation contains the answer, use it directly.
4. If the documentation is partially relevant, use what's available and note any gaps.
5. If the documentation doesn't help, say "Based on the available documentation, I couldn't find specific information about this. Here's general guidance..." and suggest escalation.
6. Always mention which document(s) you're referencing in your answer.

Focus on troubleshooting errors, guiding users through tasks, and answering system-related questions.
Always be professional and helpful."""

    def build_prompt(
        self,
        query_text: str,
        intent: Intent,
        context_messages: List[ContextMessage],
        document_context: Optional[str] = None,
    ) -> Prompt:
        """Build a complete prompt for the AI provider with optional RAG context."""
        system_prompt = self._build_system_prompt(intent, has_doc_context=bool(document_context))
        user_prompt = self._build_user_prompt(query_text, intent, document_context)
        context = self._format_context(context_messages)

        return Prompt(
            system_prompt=system_prompt,
            user_prompt=user_prompt,
            context=context,
            temperature=0.3,
            max_tokens=800,  # Increased for more detailed responses
        )

    def _build_system_prompt(self, intent: Intent, has_doc_context: bool = False) -> str:
        """Build system prompt based on intent and whether we have document context."""
        base = self.SYSTEM_PROMPT_WITH_RAG if has_doc_context else self.SYSTEM_PROMPT
        
        if intent.intent_type == IntentType.ERROR_TROUBLESHOOTING:
            base += "\n\nFor error troubleshooting: Focus on identifying the root cause and providing step-by-step resolution."
        elif intent.intent_type == IntentType.TASK_GUIDANCE:
            base += "\n\nFor task guidance: Provide clear, numbered step-by-step instructions."
        
        return base

    def _build_user_prompt(
        self, 
        query_text: str, 
        intent: Intent, 
        document_context: Optional[str] = None
    ) -> str:
        """Build user prompt with intent context and RAG documentation."""
        parts = []
        
        # Add document context if available
        if document_context:
            parts.append("=== RELEVANT DOCUMENTATION ===")
            parts.append(document_context)
            parts.append("=== END DOCUMENTATION ===\n")
        
        # Add the user's question
        parts.append("USER QUESTION:")
        
        prompt = query_text
        if intent.entities.get("error_code"):
            prompt = f"[Error Code: {intent.entities['error_code']}] {prompt}"
        
        parts.append(prompt)
        
        if document_context:
            parts.append("\nPlease answer based on the documentation provided above. Reference the specific document(s) in your response.")
        
        return "\n".join(parts)

    def _format_context(self, messages: List[ContextMessage]) -> List[str]:
        """Format context messages for prompt."""
        return [
            f"{msg.role.value}: {msg.content}"
            for msg in messages[-5:]  # Last 5 messages
        ]
