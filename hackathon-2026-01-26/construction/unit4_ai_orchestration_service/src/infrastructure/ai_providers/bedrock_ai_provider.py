"""Amazon Bedrock AI Provider - Claude preferred, Nova fallback"""
import json
from typing import Optional
import boto3
from botocore.exceptions import ClientError, NoCredentialsError

from .mock_ai_provider import IAIProvider
from ...domain.value_objects import Prompt, AIResponse


class BedrockAIProvider(IAIProvider):
    """AI provider using Amazon Bedrock - tries Claude first, falls back to Nova."""

    # Models to try in order (APAC inference profiles for Singapore region)
    CLAUDE_MODELS = [
        "apac.anthropic.claude-3-5-sonnet-20241022-v2:0",  # Claude 3.5 Sonnet v2 (best)
        "apac.anthropic.claude-3-5-sonnet-20240620-v1:0",  # Claude 3.5 Sonnet
        "apac.anthropic.claude-3-haiku-20240307-v1:0",     # Claude 3 Haiku (fastest)
    ]
    
    NOVA_MODELS = [
        "apac.amazon.nova-lite-v1:0",   # APAC Nova Lite - fallback
        "apac.amazon.nova-micro-v1:0",  # APAC Nova Micro
    ]
    
    def __init__(self, region: str = "ap-southeast-1"):
        self._region = region
        self._client = None
        self._available = False
        self._model_id = None
        self._model_type = None  # "claude" or "nova"
        self._initialize()

    def _initialize(self):
        """Initialize Bedrock client and find working model."""
        try:
            self._client = boto3.client(
                'bedrock-runtime',
                region_name=self._region
            )
            
            # Try Claude models first
            for model_id in self.CLAUDE_MODELS:
                try:
                    print(f"[Bedrock AI] Trying Claude: {model_id}")
                    self._test_claude_model(model_id)
                    self._model_id = model_id
                    self._model_type = "claude"
                    self._available = True
                    print(f"[Bedrock AI] ✓ Connected using Claude: {model_id}")
                    return
                except ClientError as e:
                    error_code = e.response.get('Error', {}).get('Code', '')
                    print(f"[Bedrock AI] ✗ {model_id}: {error_code}")
                    continue
            
            # Fall back to Nova models
            for model_id in self.NOVA_MODELS:
                try:
                    print(f"[Bedrock AI] Trying Nova: {model_id}")
                    self._test_nova_model(model_id)
                    self._model_id = model_id
                    self._model_type = "nova"
                    self._available = True
                    print(f"[Bedrock AI] ✓ Connected using Nova: {model_id}")
                    return
                except ClientError as e:
                    error_code = e.response.get('Error', {}).get('Code', '')
                    print(f"[Bedrock AI] ✗ {model_id}: {error_code}")
                    continue
            
            print("[Bedrock AI] No working model found")
            self._available = False
            
        except NoCredentialsError:
            print("[Bedrock AI] AWS credentials not found")
            self._available = False
        except Exception as e:
            print(f"[Bedrock AI] Error initializing: {e}")
            self._available = False

    def _test_claude_model(self, model_id: str):
        """Test if a Claude model works."""
        body = {
            "anthropic_version": "bedrock-2023-05-31",
            "max_tokens": 10,
            "temperature": 0.1,
            "messages": [{"role": "user", "content": "Hi"}]
        }
        
        self._client.invoke_model(
            modelId=model_id,
            body=json.dumps(body),
            contentType="application/json",
            accept="application/json"
        )

    def _test_nova_model(self, model_id: str):
        """Test if a Nova model works."""
        body = {
            "messages": [
                {"role": "user", "content": [{"text": "Hi"}]}
            ],
            "inferenceConfig": {"maxTokens": 10, "temperature": 0.1}
        }
        
        self._client.invoke_model(
            modelId=model_id,
            body=json.dumps(body),
            contentType="application/json",
            accept="application/json"
        )

    def _invoke_claude(self, prompt_text: str, system_prompt: str = "", max_tokens: int = 1000, temperature: float = 0.3) -> dict:
        """Invoke Claude model."""
        messages = [{"role": "user", "content": prompt_text}]
        
        body = {
            "anthropic_version": "bedrock-2023-05-31",
            "max_tokens": max_tokens,
            "temperature": temperature,
            "messages": messages
        }
        
        if system_prompt:
            body["system"] = system_prompt

        response = self._client.invoke_model(
            modelId=self._model_id,
            body=json.dumps(body),
            contentType="application/json",
            accept="application/json"
        )

        return json.loads(response['body'].read())

    def _invoke_nova(self, prompt_text: str, system_prompt: str = "", max_tokens: int = 1000, temperature: float = 0.3) -> dict:
        """Invoke Nova model."""
        body = {
            "messages": [
                {"role": "user", "content": [{"text": prompt_text}]}
            ],
            "inferenceConfig": {
                "maxTokens": max_tokens,
                "temperature": temperature
            }
        }
        
        if system_prompt:
            body["system"] = [{"text": system_prompt}]

        response = self._client.invoke_model(
            modelId=self._model_id,
            body=json.dumps(body),
            contentType="application/json",
            accept="application/json"
        )

        return json.loads(response['body'].read())

    def generate_response(self, prompt: Prompt) -> AIResponse:
        """Generate a response using Amazon Bedrock (Claude or Nova)."""
        if not self._available:
            return self._fallback_response(prompt)

        try:
            # Build the prompt
            user_prompt = self._build_user_prompt(prompt)
            
            # Call appropriate model
            if self._model_type == "claude":
                response = self._invoke_claude(
                    user_prompt,
                    system_prompt=prompt.system_prompt,
                    max_tokens=prompt.max_tokens,
                    temperature=prompt.temperature
                )
                # Claude response format
                content = response.get("content", [{}])[0].get("text", "")
                tokens_used = response.get("usage", {}).get("output_tokens", 0)
            else:
                response = self._invoke_nova(
                    user_prompt,
                    system_prompt=prompt.system_prompt,
                    max_tokens=prompt.max_tokens,
                    temperature=prompt.temperature
                )
                # Nova response format
                output = response.get("output", {})
                message = output.get("message", {})
                content_list = message.get("content", [])
                content = content_list[0].get("text", "") if content_list else ""
                usage = response.get("usage", {})
                tokens_used = usage.get("outputTokens", 0)

            return AIResponse.create(
                content=content.strip(),
                model=self._model_id,
                tokens_used=tokens_used
            )

        except ClientError as e:
            print(f"[Bedrock AI] Error calling model: {e}")
            return self._fallback_response(prompt)
        except Exception as e:
            print(f"[Bedrock AI] Unexpected error: {e}")
            return self._fallback_response(prompt)

    def _build_user_prompt(self, prompt: Prompt) -> str:
        """Build user prompt with context."""
        parts = []
        
        # Conversation context FIRST (important for continuity)
        if prompt.context:
            parts.append("=== CONVERSATION HISTORY ===")
            for ctx in prompt.context:
                parts.append(ctx)
            parts.append("=== END CONVERSATION HISTORY ===")
            parts.append("")
        
        # User query (includes document context from PromptEngineeringService)
        parts.append(prompt.user_prompt)
        
        return "\n".join(parts)

    def _fallback_response(self, prompt: Prompt) -> AIResponse:
        """Fallback response when Bedrock is unavailable."""
        return AIResponse.create(
            content="I apologize, but I'm currently unable to process your request. Please try again in a moment or escalate to human support if the issue persists.",
            model="fallback",
            tokens_used=0
        )

    def is_available(self) -> bool:
        """Check if Bedrock is available."""
        return self._available

    def get_model_name(self) -> str:
        """Get the model name."""
        return self._model_id or "none"


class BedrockRAGProvider(IAIProvider):
    """AI provider with RAG using Bedrock - delegates to BedrockAIProvider."""

    def __init__(self, region: str = "ap-southeast-1"):
        self._provider = BedrockAIProvider(region=region)

    def generate_response(self, prompt: Prompt) -> AIResponse:
        return self._provider.generate_response(prompt)

    def is_available(self) -> bool:
        return self._provider.is_available()

    def get_model_name(self) -> str:
        return self._provider.get_model_name()
