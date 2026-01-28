"""Amazon Bedrock AI Provider - Claude preferred, Nova fallback"""
import json
import base64
import requests
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

    def _invoke_claude(
        self, 
        prompt_text: str, 
        system_prompt: str = "", 
        max_tokens: int = 1000, 
        temperature: float = 0.3,
        image_base64: Optional[str] = None,
        image_media_type: Optional[str] = None
    ) -> dict:
        """Invoke Claude model with optional image for vision."""
        # Build message content
        content = []
        
        # Add image first if provided (Claude expects image before text)
        if image_base64 and image_media_type:
            print(f"[Bedrock AI] Including image in request ({image_media_type})")
            content.append({
                "type": "image",
                "source": {
                    "type": "base64",
                    "media_type": image_media_type,
                    "data": image_base64
                }
            })
        
        # Add text content
        content.append({
            "type": "text",
            "text": prompt_text
        })
        
        messages = [{"role": "user", "content": content}]
        
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
            
            # Get image data if available
            image_base64 = None
            image_media_type = None
            
            if prompt.has_image():
                image_base64, image_media_type = self._get_image_data(prompt)
            
            # Call appropriate model
            if self._model_type == "claude":
                response = self._invoke_claude(
                    user_prompt,
                    system_prompt=prompt.system_prompt,
                    max_tokens=prompt.max_tokens,
                    temperature=prompt.temperature,
                    image_base64=image_base64,
                    image_media_type=image_media_type
                )
                # Claude response format
                content = response.get("content", [{}])[0].get("text", "")
                tokens_used = response.get("usage", {}).get("output_tokens", 0)
            else:
                # Nova doesn't support vision in the same way
                if image_base64:
                    print("[Bedrock AI] Warning: Nova model doesn't support vision, ignoring image")
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
            import traceback
            traceback.print_exc()
            return self._fallback_response(prompt)

    def _get_image_data(self, prompt: Prompt) -> tuple[Optional[str], Optional[str]]:
        """Get image data from prompt (base64 or fetch from URL)."""
        # If base64 already provided, use it
        if prompt.image_base64:
            media_type = prompt.image_media_type or "image/png"
            return prompt.image_base64, media_type
        
        # If URL provided, fetch and encode
        if prompt.image_url:
            try:
                print(f"[Bedrock AI] Fetching image from: {prompt.image_url}")
                response = requests.get(prompt.image_url, timeout=10)
                if response.status_code == 200:
                    image_data = base64.b64encode(response.content).decode('utf-8')
                    # Detect media type from content-type header or URL
                    content_type = response.headers.get('content-type', '')
                    if 'png' in content_type or prompt.image_url.lower().endswith('.png'):
                        media_type = 'image/png'
                    elif 'jpeg' in content_type or 'jpg' in content_type or prompt.image_url.lower().endswith(('.jpg', '.jpeg')):
                        media_type = 'image/jpeg'
                    elif 'gif' in content_type or prompt.image_url.lower().endswith('.gif'):
                        media_type = 'image/gif'
                    elif 'webp' in content_type or prompt.image_url.lower().endswith('.webp'):
                        media_type = 'image/webp'
                    else:
                        media_type = 'image/png'  # Default
                    
                    print(f"[Bedrock AI] Image fetched successfully ({media_type}, {len(image_data)} chars)")
                    return image_data, media_type
                else:
                    print(f"[Bedrock AI] Failed to fetch image: HTTP {response.status_code}")
            except Exception as e:
                print(f"[Bedrock AI] Error fetching image: {e}")
        
        return None, None

    def _build_user_prompt(self, prompt: Prompt) -> str:
        """Build user prompt with context."""
        parts = []
        
        # Conversation context if available
        if prompt.context:
            parts.append("Previous conversation:")
            for ctx in prompt.context:
                parts.append(ctx)
            parts.append("")
        
        # User query
        parts.append(prompt.user_prompt)
        
        # Add note about image if present
        if prompt.has_image():
            parts.append("\n[Note: A screenshot has been attached. Please analyze it along with the question above.]")
        
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
