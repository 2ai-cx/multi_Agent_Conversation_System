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
- JSON minification for 30-50% token savings
- RAG (Retrieval-Augmented Generation) with vector stores (NEW)
- Long-term memory management (NEW)

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
    
    # JSON minification
    minified = client.minify_json_data(data)
    expanded = client.expand_json_response(llm_response)
"""

__version__ = "1.2.0"  # ➕ Updated for RAG support

from llm.config import LLMConfig
from llm.client import LLMClient, LLMResponse
from llm.json_minifier import minify_for_llm, expand_from_llm, get_minification_instruction

# ➕ NEW: RAG components (lazy import to avoid dependencies if not used)
def _get_memory_manager():
    from llm.memory import LLMMemoryManager
    return LLMMemoryManager

def _get_embeddings_provider():
    from llm.embeddings import EmbeddingsProvider
    return EmbeddingsProvider

__all__ = [
    # Core components
    "LLMConfig",
    "LLMClient", 
    "LLMResponse",
    
    # JSON minification
    "minify_for_llm",
    "expand_from_llm",
    "get_minification_instruction",
    
    # ➕ NEW: RAG components (lazy loaded)
    # Import these only if RAG is enabled:
    # from llm.memory import LLMMemoryManager
    # from llm.embeddings import EmbeddingsProvider
]
