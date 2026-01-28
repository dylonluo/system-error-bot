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
        "STRICT RULES:\n"
        "1. ONLY use information from the provided documentation. Do NOT add steps or information from your own knowledge.\n"
        "2. If the documentation doesn't contain complete steps, say 'The documentation does not specify further steps. Please escalate for additional guidance.'\n"
        "3. Quote specific technical details or error codes exactly as they appear.\n"
        "4. ALWAYS cite the document title/source name for every fact provided.\n"
        "5. Do NOT invent, assume, or infer steps that are not explicitly in the documentation.\n\n"
        "RESPONSE STRUCTURE:\n"
        "- DIRECT ANSWER: Provide a 1-2 sentence summary first.\n"
        "- INSTRUCTIONS: Use numbered lists for steps. Only include steps found in the documentation.\n"
        "- SOURCES: List the documents used at the end of your response."
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