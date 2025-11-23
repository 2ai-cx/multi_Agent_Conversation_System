"""
OpenRouter LLM Provider

Routes LLM requests through OpenRouter API for:
- Unified access to multiple providers (OpenAI, Anthropic, etc.)
- Built-in rate limiting via tenant API keys
- Provider-level prompt caching
- Usage tracking and cost management
"""

import time
import httpx
from typing import List, Dict, Any, Optional

from llm.providers.base import BaseLLMProvider
from llm.client import LLMResponse
from llm.config import LLMConfig


class OpenRouterProvider(BaseLLMProvider):
    """
    OpenRouter LLM provider
    
    Routes requests through OpenRouter API with:
    - Tenant-specific API keys
    - Automatic rate limiting
    - Provider-level caching
    - Multi-provider support
    
    Usage:
        provider = OpenRouterProvider(config)
        response = await provider.chat_completion(
            messages=[{"role": "user", "content": "Hello!"}],
            api_key="tenant-specific-key"
        )
    """
    
    def __init__(self, config: LLMConfig):
        """
        Initialize OpenRouter provider
        
        Args:
            config: LLM configuration
        """
        super().__init__(config)
        self.base_url = "https://openrouter.ai/api/v1"
        self.client = None
        
        # Initialize logger
        import logging
        self.logger = logging.getLogger(__name__)
    
    async def chat_completion(
        self,
        messages: List[Dict[str, str]],
        api_key: Optional[str] = None,
        **kwargs
    ) -> LLMResponse:
        """
        Generate chat completion via OpenRouter
        
        Args:
            messages: List of messages [{"role": "user", "content": "..."}]
            api_key: Tenant-specific OpenRouter API key (optional)
            **kwargs: Additional parameters (temperature, max_tokens, etc.)
        
        Returns:
            LLMResponse with content, tokens, cost, latency
        
        Raises:
            httpx.HTTPError: If API request fails
        """
        start_time = time.time()
        
        # Use tenant key or fallback to config key
        auth_key = api_key or self.config.openrouter_api_key
        if not auth_key:
            raise ValueError("OpenRouter API key required (tenant key or config key)")
        
        # Prepare request
        headers = {
            "Authorization": f"Bearer {auth_key}",
            "HTTP-Referer": self.config.app_url or "https://unified-temporal-worker.azurecontainerapps.io",
            "X-Title": "Unified Temporal Worker",
            "Content-Type": "application/json"
        }
        
        payload = {
            "model": kwargs.get("model") or self.config.openrouter_model or "openai/gpt-4-turbo",
            "messages": messages,
            "temperature": kwargs.get("temperature", self.config.openai_temperature),
            "max_tokens": kwargs.get("max_tokens", self.config.openai_max_tokens),
            "top_p": kwargs.get("top_p", self.config.openai_top_p),
        }
        
        # Make request
        async with httpx.AsyncClient(timeout=self.config.openai_timeout) as client:
            try:
                response = await client.post(
                    f"{self.base_url}/chat/completions",
                    headers=headers,
                    json=payload
                )
                response.raise_for_status()
                data = response.json()
                
            except httpx.HTTPStatusError as e:
                self.logger.error(f"OpenRouter API error: {e.response.status_code} - {e.response.text}")
                raise
            except httpx.RequestError as e:
                self.logger.error(f"OpenRouter request error: {str(e)}")
                raise
        
        # Calculate latency
        latency_ms = (time.time() - start_time) * 1000
        
        # Extract response data
        choice = data["choices"][0]
        usage = data.get("usage", {})
        
        # Calculate cost (OpenRouter provides this in some cases)
        cost_usd = self._extract_cost(data, usage)
        
        # Build response
        return LLMResponse(
            content=choice["message"]["content"],
            model=data.get("model", payload["model"]),
            prompt_tokens=usage.get("prompt_tokens", 0),
            completion_tokens=usage.get("completion_tokens", 0),
            total_tokens=usage.get("total_tokens", 0),
            latency_ms=latency_ms,
            cost_usd=cost_usd,
            cached=False,  # Will be updated by cache layer
            metadata={
                "provider": "openrouter",
                "finish_reason": choice.get("finish_reason"),
                "openrouter_id": data.get("id"),
            }
        )
    
    def _extract_cost(self, data: Dict[str, Any], usage: Dict[str, Any]) -> float:
        """
        Extract or calculate cost from response
        
        OpenRouter may provide cost directly in some responses.
        Otherwise, calculate based on token usage and model pricing.
        
        Args:
            data: Full API response
            usage: Usage data from response
        
        Returns:
            Cost in USD
        """
        # Check if OpenRouter provided cost directly
        if "cost" in usage:
            return float(usage["cost"])
        
        # Fallback: calculate from tokens
        prompt_tokens = usage.get("prompt_tokens", 0)
        completion_tokens = usage.get("completion_tokens", 0)
        
        return self.calculate_cost(prompt_tokens, completion_tokens)
    
    async def close(self):
        """Close connections and cleanup resources"""
        # httpx.AsyncClient is used as context manager, so no cleanup needed
        self.logger.debug("OpenRouter provider closed")


class OpenRouterError(Exception):
    """Base exception for OpenRouter-specific errors"""
    pass


class OpenRouterRateLimitError(OpenRouterError):
    """Raised when OpenRouter rate limit is exceeded"""
    
    def __init__(self, message: str, retry_after: Optional[float] = None):
        super().__init__(message)
        self.retry_after = retry_after


class OpenRouterAuthError(OpenRouterError):
    """Raised when OpenRouter authentication fails"""
    pass
