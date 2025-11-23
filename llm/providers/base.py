"""
Base LLM Provider Interface

Abstract base class for all LLM providers
"""

from abc import ABC, abstractmethod
from typing import List, Dict, Any

from llm.client import LLMResponse
from llm.config import LLMConfig


class BaseLLMProvider(ABC):
    """
    Abstract base class for LLM providers
    
    All providers must implement:
    - chat_completion: Generate chat completion
    - close: Cleanup resources
    """
    
    def __init__(self, config: LLMConfig):
        """
        Initialize provider
        
        Args:
            config: LLM configuration
        """
        self.config = config
    
    @abstractmethod
    async def chat_completion(
        self,
        messages: List[Dict[str, str]],
        **kwargs
    ) -> LLMResponse:
        """
        Generate chat completion
        
        Args:
            messages: List of messages
            **kwargs: Provider-specific parameters
        
        Returns:
            LLMResponse
        """
        pass
    
    @abstractmethod
    async def close(self):
        """Close connections and cleanup resources"""
        pass
    
    def calculate_cost(
        self,
        prompt_tokens: int,
        completion_tokens: int
    ) -> float:
        """
        Calculate cost in USD
        
        Args:
            prompt_tokens: Number of prompt tokens
            completion_tokens: Number of completion tokens
        
        Returns:
            Cost in USD
        """
        prompt_cost = (prompt_tokens / 1000) * self.config.cost_per_1k_prompt_tokens
        completion_cost = (completion_tokens / 1000) * self.config.cost_per_1k_completion_tokens
        return prompt_cost + completion_cost
