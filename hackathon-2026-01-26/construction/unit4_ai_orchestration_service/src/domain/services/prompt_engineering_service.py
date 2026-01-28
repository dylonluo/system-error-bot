from typing import List, Optional
from ..value_objects import Prompt, Intent, IntentType
from ..entities import ContextMessage


class PromptEngineeringService:
    """Builds optimized prompts for AI provider with RAG support."""

    SYSTEM_PROMPT_NO_DOCS = """You are a helpful documentation assistant for NetSuite and TMS (Transportation Management System).

IMPORTANT: No relevant documentation was found for this query.

Your response MUST be:
"I searched through our documentation but couldn't find specific information related to your question. Please escalate this to the relevant support personnel for assistance."

Do not make up information. Do not provide generic advice. Simply acknowledge that no documentation was found and recommend escalation."""

    SYSTEM_PROMPT_WITH_DOCS = """You are a helpful documentation assistant for NetSuite and TMS (Transportation Management System).

You have been provided with RELEVANT DOCUMENTATION below. Your job is to:

1. READ and UNDERSTAND the documentation provided
2. FIND the specific information that answers the user's question
3. SUMMARIZE the relevant steps or information in your own words
4. QUOTE specific details from the documentation when helpful
5. ALWAYS mention which document(s) you're referencing

RESPONSE FORMAT:
- Start with a direct answer to the question
- Provide step-by-step instructions if the documentation contains them
- Summarize what the document explains
- Reference the document title(s) you used

If the documentation doesn't fully answer the question, say what you found and suggest escalation for the remaining parts.

Be concise but thorough. Use bullet points for steps."""

    def build_prompt(
        self,
        query_text: str,
        intent: Intent,
        context_messages: List[ContextMessage],
        document_context: Optional[str] = None,
    ) -> Prompt:
        """Build a complete prompt for the AI provider with optional RAG context."""
        has_docs = bool(document_context and document_context.strip())
        
        system_prompt = self._build_system_prompt(intent, has_docs)
        user_prompt = self._build_user_prompt(query_text, intent, document_context)
        context = self._format_context(context_messages)

        return Prompt(
            system_prompt=system_prompt,
            user_prompt=user_prompt,
            context=context,
            temperature=0.2 if has_docs else 0.1,  # Lower temp for more consistent responses
            max_tokens=1000,
        )

    def _build_system_prompt(self, intent: Intent, has_docs: bool = False) -> str:
        """Build system prompt based on whether we have document context."""
        if not has_docs:
            return self.SYSTEM_PROMPT_NO_DOCS
        
        base = self.SYSTEM_PROMPT_WITH_DOCS
        
        if intent.intent_type == IntentType.ERROR_TROUBLESHOOTING:
            base += "\n\nThis is an ERROR TROUBLESHOOTING query. Focus on:\n- Root cause identification\n- Step-by-step resolution\n- Any error codes or specific fixes mentioned in the docs"
        elif intent.intent_type == IntentType.TASK_GUIDANCE:
            base += "\n\nThis is a TASK GUIDANCE query. Focus on:\n- Clear numbered steps\n- Prerequisites or requirements\n- Expected outcomes"
        
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
        if document_context and document_context.strip():
            parts.append("=" * 50)
            parts.append("RELEVANT DOCUMENTATION:")
            parts.append("=" * 50)
            parts.append(document_context)
            parts.append("=" * 50)
            parts.append("")
        
        # Add the user's question
        parts.append("USER QUESTION:")
        
        prompt = query_text
        if intent.entities.get("error_code"):
            prompt = f"[Error Code: {intent.entities['error_code']}] {prompt}"
        
        parts.append(prompt)
        
        if document_context and document_context.strip():
            parts.append("")
            parts.append("Please read the documentation above carefully and provide a helpful answer based on what you find. Summarize the relevant information and reference which document(s) you used.")
        
        return "\n".join(parts)

    def _format_context(self, messages: List[ContextMessage]) -> List[str]:
        """Format context messages for prompt."""
        return [
            f"{msg.role.value}: {msg.content}"
            for msg in messages[-5:]  # Last 5 messages
        ]
