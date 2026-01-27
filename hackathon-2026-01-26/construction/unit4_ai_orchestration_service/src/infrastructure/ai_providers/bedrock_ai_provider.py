"""Amazon Bedrock AI Provider using Amazon Nova Lite"""
import json
from typing import Optional
import boto3
from botocore.exceptions import ClientError, NoCredentialsError

from .mock_ai_provider import IAIProvider
from ...domain.value_objects import Prompt, AIResponse


class BedrockAIProvider(IAIProvider):
    """AI provider using Amazon Bedrock with Amazon Nova Lite in ap-southeast-1."""

    # Amazon Nova models via APAC inference profiles
    MODELS = [
        "apac.amazon.nova-lite-v1:0",   # APAC Nova Lite - fast and efficient
        "apac.amazon.nova-micro-v1:0",  # APAC Nova Micro - smallest/fastest
        "apac.amazon.nova-pro-v1:0",    # APAC Nova Pro - most capable
    ]
    
    def __init__(self, region: str = "ap-southeast-1"):
        self._region = region
        self._client = None
        self._available = False
        self._model_id = None
        self._initialize()

    def _initialize(self):
        """Initialize Bedrock client and find working model."""
        try:
            self._client = boto3.client(
                'bedrock-runtime',
                region_name=self._region
            )
            
            # Try each model until one works
            for model_id in self.MODELS:
                try:
                    print(f"[Bedrock AI] Trying model: {model_id}")
                    self._test_model(model_id)
                    self._model_id = model_id
                    self._available = True
                    print(f"[Bedrock AI] ✓ Connected using: {model_id}")
                    return
                except ClientError as e:
                    error_code = e.response.get('Error', {}).get('Code', '')
                    error_msg = e.response.get('Error', {}).get('Message', '')
                    print(f"[Bedrock AI] ✗ {model_id}: {error_code} - {error_msg}")
                    continue
            
            print("[Bedrock AI] No working model found")
            self._available = False
            
        except NoCredentialsError:
            print("[Bedrock AI] AWS credentials not found")
            self._available = False
        except Exception as e:
            print(f"[Bedrock AI] Error initializing: {e}")
            self._available = False

    def _test_model(self, model_id: str):
        """Test if a model works using Amazon Nova format."""
        # Amazon Nova uses the Converse API format
        body = {
            "messages": [
                {
                    "role": "user",
                    "content": [{"text": "Hi"}]
                }
            ],
            "inferenceConfig": {
                "maxTokens": 10,
                "temperature": 0.1
            }
        }
        
        self._client.invoke_model(
            modelId=model_id,
            body=json.dumps(body),
            contentType="application/json",
            accept="application/json"
        )

    def _invoke_model(self, prompt_text: str, system_prompt: str = "", max_tokens: int = 1000, temperature: float = 0.3) -> dict:
        """Invoke the Amazon Nova model."""
        # Amazon Nova uses the Converse API format
        body = {
            "messages": [
                {
                    "role": "user",
                    "content": [{"text": prompt_text}]
                }
            ],
            "inferenceConfig": {
                "maxTokens": max_tokens,
                "temperature": temperature
            }
        }
        
        # Add system prompt if provided
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
        """Generate a response using Amazon Bedrock Nova."""
        if not self._available:
            return self._fallback_response(prompt)

        try:
            # Build the full prompt
            full_prompt = self._build_nova_prompt(prompt)
            
            # Call Bedrock
            response = self._invoke_model(
                full_prompt,
                system_prompt=prompt.system_prompt,
                max_tokens=prompt.max_tokens,
                temperature=prompt.temperature
            )

            # Extract content from Nova response format
            # Nova returns: {"output": {"message": {"content": [{"text": "..."}]}}, "usage": {...}}
            output = response.get("output", {})
            message = output.get("message", {})
            content_list = message.get("content", [])
            content = content_list[0].get("text", "") if content_list else ""
            
            # Get token usage
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

    def _build_nova_prompt(self, prompt: Prompt) -> str:
        """Build a prompt optimized for Amazon Nova."""
        parts = []
        
        # Conversation context if available
        if prompt.context:
            parts.append("Previous conversation context:")
            for ctx in prompt.context:
                parts.append(ctx)
            parts.append("")
        
        # User query
        parts.append(f"User question: {prompt.user_prompt}")
        
        # Instructions for response format
        parts.append("""
Please provide a helpful, accurate response based on the context provided. 
If you reference documentation, mention it naturally in your response.
Be concise but thorough. Use bullet points for steps or lists.
If you're not sure about something, say so and suggest escalating to human support.""")
        
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
