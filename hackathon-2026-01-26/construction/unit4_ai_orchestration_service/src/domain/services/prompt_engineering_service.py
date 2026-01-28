from typing import List, Optional
from ..value_objects import Prompt, Intent, IntentType
from ..entities import ContextMessage

class PromptEngineeringService:
    """Builds optimized prompts for AI provider with RAG support."""

    # STRICT NO-DOCS GUARDRAIL
    SYSTEM_PROMPT_NO_DOCS = (
        "You are a helpful documentation assistant.\n\n"
        "IMPORTANT: No relevant documentation was found for this query.\n\n"
        "Your response MUST be:\n"
        "\"I searched through our documentation but couldn't find specific information related to your question. "
        "Please escalate this to the relevant support personnel for assistance.\"\n\n"
        "Do not make up information. Do not provide generic advice."
    )

    # DETAILED RAG-ENABLED PROMPT
    SYSTEM_PROMPT_WITH_DOCS = (
        "You are a professional Technical Support Assistant. You have been provided with RELEVANT DOCUMENTATION sections "
        "to answer the user's query.\n\n"
        "CRITICAL RULES - FOLLOW EXACTLY:\n"
        "1. ONLY use information EXPLICITLY written in the provided documentation.\n"
        "2. Do NOT add ANY steps, recommendations, or information from your general knowledge.\n"
        "3. Do NOT infer, assume, or extrapolate beyond what is written.\n"
        "4. If the documentation shows steps 1-3, you MUST only list steps 1-3. Do NOT add step 4.\n"
        "5. If the documentation doesn't contain complete information, say: 'The documentation does not provide additional steps. Please escalate for further guidance.'\n"
        "6. Quote specific technical details, error codes, and field names EXACTLY as they appear.\n"
        "7. ALWAYS cite the document title/source name for every fact.\n"
        "8. If you cannot find the answer in the documentation, say so clearly.\n\n"
        "RESPONSE STRUCTURE:\n"
        "- DIRECT ANSWER: 1-2 sentence summary of what the documentation says.\n"
        "- INSTRUCTIONS: Numbered list of steps ONLY from the documentation. No additions.\n"
        "- SOURCES: List the exact document titles used.\n\n"
        "FORBIDDEN:\n"
        "- Adding 'Next Steps' or 'Additional Recommendations' not in the docs\n"
        "- Suggesting to 'contact support' unless the documentation says so\n"
        "- Providing generic troubleshooting steps not in the documentation"
    )

    def build_prompt(
        self,
        query_text: str,
        intent: Intent,
        context_messages: List[ContextMessage],
        document_context: Optional[str] = None,
    ) -> Prompt:
        """Build a complete prompt with intent-specific logic and context."""
        has_docs = bool(document_context and document_context.strip())
        
        system_prompt = self._build_system_prompt(intent, has_docs)
        user_prompt = self._build_user_prompt(query_text, intent, document_context)
        context = self._format_context(context_messages)

        return Prompt(
            system_prompt=system_prompt,
            user_prompt=user_prompt,
            context=context,
            # Keeping temperature low for factual accuracy
            temperature=0.2 if has_docs else 0.0,
            max_tokens=1200,
        )

    def _build_system_prompt(self, intent: Intent, has_docs: bool = False) -> str:
        if not has_docs:
            return self.SYSTEM_PROMPT_NO_DOCS
        
        base = self.SYSTEM_PROMPT_WITH_DOCS
        
        # Inject Intent-Specific Persona
        if intent.intent_type == IntentType.ERROR_TROUBLESHOOTING:
            base += (
                "\n\nCONTEXT: ERROR TROUBLESHOOTING\n"
                "- Prioritize root cause analysis.\n"
                "- Check for 'Known Issues' or 'Workarounds' in the docs."
            )
        elif intent.intent_type == IntentType.TASK_GUIDANCE:
            base += (
                "\n\nCONTEXT: TASK GUIDANCE\n"
                "- Focus on prerequisites and expected outcomes.\n"
                "- Ensure steps are sequential and logically ordered."
            )
        
        return base

    def _build_user_prompt(
        self, 
        query_text: str, 
        intent: Intent, 
        document_context: Optional[str] = None
    ) -> str:
        parts = []
        
        if document_context and document_context.strip():
            parts.append("### START OF DOCUMENTATION CONTEXT ###")
            parts.append(document_context)
            parts.append("### END OF DOCUMENTATION CONTEXT ###\n")
        
        # Enrich the query with detected entities (e.g., Error Codes)
        query_display = query_text
        error_code = intent.entities.get("error_code")
        if error_code:
            query_display = f"[Target Error: {error_code}] {query_display}"

        parts.append(f"USER QUESTION: {query_display}")
        
        if document_context:
            parts.append("\nInstruction: Answer using ONLY the context above. If not found, follow the escalation protocol.")

        return "\n".join(parts)

    def _format_context(self, messages: List[ContextMessage]) -> List[str]:
        """Keep the last 5 messages to maintain flow without hitting context limits."""
        return [
            f"{msg.role.value.upper()}: {msg.content}"
            for msg in messages[-5:]
        ]