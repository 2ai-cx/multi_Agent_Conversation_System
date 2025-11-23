"""
LLM Best Practices - Centralized LLM Client

This package provides a centralized, observable, and resilient LLM client
following industry best practices.

Key Features:
- Centralized LLM client for all interactions
- Environment-based configuration (no hardcoding)
- Automatic Opik tracing for observability
- Multi-level rate limiting (global, tenant, user)
- Hardened error handling with retries and fallbacks
- Token usage tracking and cost attribution
- Response caching for cost optimization

Usage:
    from llm.client import LLMClient
    from llm.config import LLMConfig
    
    config = LLMConfig()
    client = LLMClient(config)
    
    response = await client.chat_completion(
        messages=[{"role": "user", "content": "Hello!"}],
        tenant_id="tenant-123",
        user_id="user-456"
    )
"""

__version__ = "1.0.0"

from llm.config import LLMConfig
from llm.client import LLMClient, LLMResponse

__all__ = ["LLMConfig", "LLMClient", "LLMResponse"]
