"""
OpenAI Provider

Implementation of OpenAI API provider
"""

from typing import List, Dict, Any
import logging

from llm.providers.base import BaseLLMProvider
from llm.client import LLMResponse
from llm.config import LLMConfig

logger = logging.getLogger(__name__)


class OpenAIProvider(BaseLLMProvider):
    """
    OpenAI API provider
    
    Supports:
    - GPT-4, GPT-4 Turbo
    - GPT-3.5 Turbo
    - Chat completions
    - Streaming (future)
    """
    
    def __init__(self, config: LLMConfig):
        """
        Initialize OpenAI provider
        
        Args:
            config: LLM configuration
        """
        super().__init__(config)
        
        # Initialize OpenAI client (lazy loading)
        self._client = None
        
        logger.info(f"OpenAI provider initialized with model: {config.openai_model}")
    
    @property
    def client(self):
        """Lazy load OpenAI client"""
        if self._client is None:
            try:
                from openai import AsyncOpenAI
                
                self._client = AsyncOpenAI(
                    api_key=self.config.openai_api_key,
                    timeout=self.config.openai_timeout
                )
                
                logger.debug("OpenAI client created")
            except ImportError:
                raise ImportError(
                    "OpenAI package not installed. "
                    "Install with: pip install openai>=1.0.0"
                )
        
        return self._client
    
    async def chat_completion(
        self,
        messages: List[Dict[str, str]],
        temperature: float = None,
        max_tokens: int = None,
        top_p: float = None,
        model: str = None,
        **kwargs
    ) -> LLMResponse:
        """
        Generate chat completion using OpenAI API
        
        Args:
            messages: List of messages
            temperature: Sampling temperature
            max_tokens: Maximum tokens in response
            top_p: Nucleus sampling parameter
            model: Model name (override config)
            **kwargs: Additional OpenAI parameters
        
        Returns:
            LLMResponse
        """
        # Prepare parameters
        params = {
            "model": model or self.config.openai_model,
            "messages": messages,
            "temperature": temperature if temperature is not None else self.config.openai_temperature,
            "max_tokens": max_tokens or self.config.openai_max_tokens,
            "top_p": top_p if top_p is not None else self.config.openai_top_p,
            **kwargs
        }
        
        logger.debug(f"Calling OpenAI API with model: {params['model']}")
        
        try:
            # Call OpenAI API
            response = await self.client.chat.completions.create(**params)
            
            # Extract response data
            content = response.choices[0].message.content
            model_used = response.model
            prompt_tokens = response.usage.prompt_tokens
            completion_tokens = response.usage.completion_tokens
            total_tokens = response.usage.total_tokens
            
            # Calculate cost
            cost_usd = self.calculate_cost(prompt_tokens, completion_tokens)
            
            logger.info(
                f"OpenAI API success: {total_tokens} tokens, ${cost_usd:.4f}"
            )
            
            # Create response
            return LLMResponse(
                content=content,
                model=model_used,
                prompt_tokens=prompt_tokens,
                completion_tokens=completion_tokens,
                total_tokens=total_tokens,
                latency_ms=0.0,  # Will be set by client
                cost_usd=cost_usd,
                cached=False,
                metadata={
                    "finish_reason": response.choices[0].finish_reason,
                    "response_id": response.id
                }
            )
        
        except Exception as e:
            logger.error(f"OpenAI API error: {e}")
            raise
    
    async def close(self):
        """Close OpenAI client"""
        if self._client:
            await self._client.close()
            logger.debug("OpenAI client closed")
