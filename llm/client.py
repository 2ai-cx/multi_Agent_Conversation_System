"""
Centralized LLM Client

Single entry point for all LLM interactions with:
- Automatic Opik tracing
- Rate limiting
- Error handling with retries
- Cost tracking
- Response caching
"""

import time
import hashlib
import json
from typing import List, Dict, Any, Optional
from dataclasses import dataclass, field
from datetime import datetime

from llm.config import LLMConfig


@dataclass
class LLMResponse:
    """Response from LLM with metadata"""
    content: str
    model: str
    prompt_tokens: int
    completion_tokens: int
    total_tokens: int
    latency_ms: float
    cost_usd: float
    cached: bool = False
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for logging/storage"""
        return {
            "content": self.content,
            "model": self.model,
            "prompt_tokens": self.prompt_tokens,
            "completion_tokens": self.completion_tokens,
            "total_tokens": self.total_tokens,
            "latency_ms": self.latency_ms,
            "cost_usd": self.cost_usd,
            "cached": self.cached,
            "metadata": self.metadata
        }


class LLMClient:
    """
    Centralized LLM client with best practices
    
    Features:
    - Provider abstraction (OpenAI, Anthropic, Azure)
    - Automatic Opik tracing
    - Multi-level rate limiting
    - Error handling with retries
    - Response caching
    - Token usage tracking
    - Cost attribution
    
    Usage:
        config = LLMConfig()
        client = LLMClient(config)
        
        response = await client.chat_completion(
            messages=[{"role": "user", "content": "Hello!"}],
            tenant_id="tenant-123",
            user_id="user-456"
        )
    """
    
    def __init__(self, config: LLMConfig):
        """
        Initialize LLM client
        
        Args:
            config: LLM configuration
        """
        self.config = config
        
        # Validate configuration
        self.config.validate_config()
        
        # Initialize components (lazy loading)
        self._provider = None
        self._rate_limiter = None
        self._error_handler = None
        self._opik_tracker = None
        self._cache = None
        self._tenant_key_manager = None
        
        # Initialize logger
        import logging
        self.logger = logging.getLogger(__name__)
        self.logger.setLevel(getattr(logging, config.log_level.upper()))
    
    @property
    def provider(self):
        """Lazy load provider"""
        if self._provider is None:
            # Use OpenRouter if feature flag enabled
            if self.config.use_openrouter:
                from llm.providers.openrouter import OpenRouterProvider
                self._provider = OpenRouterProvider(self.config)
                self.logger.info("Using OpenRouter provider")
            elif self.config.provider == "openai":
                from llm.providers.openai import OpenAIProvider
                self._provider = OpenAIProvider(self.config)
            elif self.config.provider == "anthropic":
                # Future: from llm.providers.anthropic import AnthropicProvider
                raise NotImplementedError("Anthropic provider not yet implemented")
            elif self.config.provider == "azure-openai":
                # Future: from llm.providers.azure import AzureOpenAIProvider
                raise NotImplementedError("Azure OpenAI provider not yet implemented")
            else:
                raise ValueError(f"Unknown provider: {self.config.provider}")
        
        return self._provider
    
    @property
    def rate_limiter(self):
        """Lazy load rate limiter (v1 or v2 based on config)"""
        if self._rate_limiter is None:
            if self.config.use_improved_rate_limiter:
                try:
                    from llm.rate_limiter_v2 import RateLimiterV2
                    self._rate_limiter = RateLimiterV2(self.config)
                    self.logger.info("Using improved rate limiter v2 (pyrate_limiter)")
                except ImportError:
                    self.logger.warning(
                        "pyrate_limiter not installed, falling back to v1. "
                        "Install with: pip install pyrate-limiter"
                    )
                    from llm.rate_limiter import RateLimiter
                    self._rate_limiter = RateLimiter(self.config)
            else:
                from llm.rate_limiter import RateLimiter
                self._rate_limiter = RateLimiter(self.config)
                self.logger.info("Using standard rate limiter v1")
        return self._rate_limiter
    
    @property
    def error_handler(self):
        """Lazy load error handler"""
        if self._error_handler is None and self.config.retry_enabled:
            from llm.error_handler import ErrorHandler
            self._error_handler = ErrorHandler(self.config)
        return self._error_handler
    
    @property
    def opik_tracker(self):
        """Lazy load Opik tracker"""
        if self._opik_tracker is None and self.config.opik_enabled:
            from llm.opik_tracker import OpikTracker
            self._opik_tracker = OpikTracker(self.config)
        return self._opik_tracker
    
    @property
    def cache(self):
        """Lazy load cache (always in-memory now)"""
        if self._cache is None and self.config.cache_enabled:
            from llm.cache import ResponseCache
            self._cache = ResponseCache(self.config)
        return self._cache
    
    @property
    def tenant_key_manager(self):
        """Lazy load tenant key manager (only for OpenRouter)"""
        if self._tenant_key_manager is None and self.config.use_openrouter:
            if self.config.openrouter_provisioning_key:
                from llm.tenant_key_manager import TenantKeyManager
                self._tenant_key_manager = TenantKeyManager(
                    provisioning_key=self.config.openrouter_provisioning_key
                )
                self.logger.info("Tenant key manager initialized")
        return self._tenant_key_manager
    
    async def generate(
        self,
        prompt: str,
        tenant_id: Optional[str] = None,
        user_id: Optional[str] = None,
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
        **kwargs
    ) -> str:
        """
        Generate text from a prompt (convenience method)
        
        Args:
            prompt: Text prompt
            tenant_id: Tenant ID for rate limiting and cost tracking
            user_id: User ID for rate limiting and cost tracking
            temperature: Override default temperature
            max_tokens: Override default max_tokens
            **kwargs: Additional provider-specific parameters
        
        Returns:
            Generated text content
        
        Raises:
            RateLimitExceeded: If rate limit exceeded
            LLMError: If LLM call fails after retries
        """
        messages = [{"role": "user", "content": prompt}]
        response = await self.chat_completion(
            messages=messages,
            tenant_id=tenant_id,
            user_id=user_id,
            temperature=temperature,
            max_tokens=max_tokens,
            **kwargs
        )
        return response.content
    
    async def chat_completion(
        self,
        messages: List[Dict[str, str]],
        tenant_id: Optional[str] = None,
        user_id: Optional[str] = None,
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
        **kwargs
    ) -> LLMResponse:
        """
        Generate chat completion
        
        Args:
            messages: List of messages [{"role": "user", "content": "..."}]
            tenant_id: Tenant ID for rate limiting and cost tracking
            user_id: User ID for rate limiting and cost tracking
            temperature: Override default temperature
            max_tokens: Override default max_tokens
            **kwargs: Additional provider-specific parameters
        
        Returns:
            LLMResponse with content and metadata
        
        Raises:
            RateLimitExceeded: If rate limit exceeded
            LLMError: If LLM call fails after retries
        """
        start_time = time.time()
        
        # Check cache first
        if self.cache:
            cache_key = self._generate_cache_key(messages, temperature, max_tokens)
            cached_response = await self.cache.get(cache_key)
            if cached_response:
                self.logger.info(f"Cache hit for key: {cache_key[:16]}...")
                cached_response.cached = True
                
                # Track cached response in Opik
                if self.opik_tracker:
                    await self.opik_tracker.log_completion(
                        messages=messages,
                        response=cached_response,
                        tenant_id=tenant_id,
                        user_id=user_id,
                        cached=True
                    )
                
                return cached_response
        
        # Rate limiting
        if self.rate_limiter:
            await self.rate_limiter.acquire(tenant_id, user_id)
        
        # Prepare parameters
        params = {
            "messages": messages,
            "temperature": temperature or self.config.openai_temperature,
            "max_tokens": max_tokens or self.config.openai_max_tokens,
            **kwargs
        }
        
        # Log request (without PII if configured)
        if self.config.log_prompts:
            self.logger.debug(f"LLM request: {json.dumps(params, indent=2)}")
        else:
            self.logger.info(f"LLM request: {len(messages)} messages, model={self.config.get_model()}")
        
        # Get tenant API key if using OpenRouter
        tenant_api_key = None
        if self.config.use_openrouter and tenant_id and self.tenant_key_manager:
            try:
                tenant_api_key = await self.tenant_key_manager.get_or_create_key(tenant_id)
                self.logger.debug(f"Using tenant-specific OpenRouter key for {tenant_id}")
            except Exception as e:
                self.logger.warning(f"Failed to get tenant key, using default: {e}")
        
        # Call LLM with error handling
        try:
            if self.error_handler:
                response = await self.error_handler.execute_with_retry(
                    self._call_provider,
                    api_key=tenant_api_key,
                    **params
                )
            else:
                response = await self._call_provider(api_key=tenant_api_key, **params)
        
        except Exception as e:
            self.logger.error(f"LLM call failed: {e}")
            
            # Try fallback model if enabled
            if self.config.fallback_enabled:
                self.logger.warning(f"Attempting fallback to {self.config.fallback_model}")
                try:
                    params["model"] = self.config.fallback_model
                    response = await self._call_provider(**params)
                except Exception as fallback_error:
                    self.logger.error(f"Fallback also failed: {fallback_error}")
                    raise
            else:
                raise
        
        # Calculate latency
        latency_ms = (time.time() - start_time) * 1000
        response.latency_ms = latency_ms
        
        # Log response (without PII if configured)
        if self.config.log_responses:
            self.logger.debug(f"LLM response: {response.content[:100]}...")
        else:
            self.logger.info(
                f"LLM response: {response.total_tokens} tokens, "
                f"{latency_ms:.0f}ms, ${response.cost_usd:.4f}"
            )
        
        # Track in Opik
        if self.opik_tracker:
            await self.opik_tracker.log_completion(
                messages=messages,
                response=response,
                tenant_id=tenant_id,
                user_id=user_id,
                cached=False
            )
        
        # Store in cache
        if self.cache:
            cache_key = self._generate_cache_key(messages, temperature, max_tokens)
            await self.cache.set(cache_key, response)
        
        return response
    
    async def _call_provider(self, api_key: Optional[str] = None, **params) -> LLMResponse:
        """
        Call the LLM provider
        
        Args:
            api_key: Tenant-specific API key (for OpenRouter)
            **params: Provider-specific parameters
        
        Returns:
            LLMResponse
        """
        # Pass tenant API key to OpenRouter provider
        if api_key and self.config.use_openrouter:
            return await self.provider.chat_completion(api_key=api_key, **params)
        else:
            return await self.provider.chat_completion(**params)
    
    def _generate_cache_key(
        self,
        messages: List[Dict[str, str]],
        temperature: Optional[float],
        max_tokens: Optional[int]
    ) -> str:
        """
        Generate cache key from request parameters
        
        Args:
            messages: Chat messages
            temperature: Temperature parameter
            max_tokens: Max tokens parameter
        
        Returns:
            Cache key (hash)
        """
        # Create deterministic string from parameters
        cache_input = {
            "messages": messages,
            "model": self.config.get_model(),
            "temperature": temperature or self.config.openai_temperature,
            "max_tokens": max_tokens or self.config.openai_max_tokens
        }
        
        # Hash to create cache key
        cache_str = json.dumps(cache_input, sort_keys=True)
        cache_key = hashlib.sha256(cache_str.encode()).hexdigest()
        
        return cache_key
    
    async def close(self):
        """Close connections and cleanup resources"""
        if self._rate_limiter:
            await self._rate_limiter.close()
        
        if self._cache:
            await self._cache.close()
        
        if self._provider:
            await self._provider.close()
        
        if self._tenant_key_manager:
            # Tenant key manager doesn't need explicit close
            pass
        
        self.logger.info("LLM client closed")


# Convenience function for quick usage
async def create_llm_client(config_file: Optional[str] = None) -> LLMClient:
    """
    Create LLM client from configuration
    
    Args:
        config_file: Path to .env file (optional)
    
    Returns:
        Configured LLMClient
    
    Example:
        client = await create_llm_client()
        response = await client.chat_completion(
            messages=[{"role": "user", "content": "Hello!"}]
        )
    """
    if config_file:
        config = LLMConfig(_env_file=config_file)
    else:
        config = LLMConfig()
    
    return LLMClient(config)


# Global LLM client instance (singleton pattern)
_global_llm_client: Optional[LLMClient] = None


def get_llm_client() -> LLMClient:
    """
    Get or create the global LLM client instance (singleton)
    
    Returns:
        Global LLMClient instance
    
    Example:
        client = get_llm_client()
        response = await client.chat_completion(
            messages=[{"role": "user", "content": "Hello!"}]
        )
    """
    global _global_llm_client
    
    if _global_llm_client is None:
        config = LLMConfig()
        _global_llm_client = LLMClient(config)
    
    return _global_llm_client
