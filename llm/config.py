"""
LLM Configuration Management

All LLM settings controlled by environment variables.
No hardcoded values - everything configurable via .env
"""

from typing import Optional
from pydantic import Field
from pydantic_settings import BaseSettings


class LLMConfig(BaseSettings):
    """
    LLM configuration from environment variables
    
    All settings have sensible defaults and can be overridden via .env
    
    Example .env:
        LLM_PROVIDER=openai
        OPENAI_MODEL=gpt-4-turbo-preview
        OPENAI_TEMPERATURE=0.7
        LLM_MAX_RPS=100
        OPIK_ENABLED=true
    """
    
    # ===== Provider Configuration =====
    provider: str = Field(
        default="openai",
        description="LLM provider (openai, anthropic, azure-openai)"
    )
    
    # ===== OpenAI Configuration =====
    openai_api_key: Optional[str] = Field(
        default=None,
        description="OpenAI API key"
    )
    openai_model: str = Field(
        default="gpt-4",
        description="OpenAI model name"
    )
    openai_temperature: float = Field(
        default=0.7,
        ge=0.0,
        le=2.0,
        description="Temperature for response randomness"
    )
    openai_max_tokens: int = Field(
        default=2000,
        gt=0,
        description="Maximum tokens in response"
    )
    openai_timeout: int = Field(
        default=30,
        gt=0,
        description="Request timeout in seconds"
    )
    openai_top_p: float = Field(
        default=1.0,
        ge=0.0,
        le=1.0,
        description="Nucleus sampling parameter"
    )
    
    # ===== Anthropic Configuration (Optional) =====
    anthropic_api_key: Optional[str] = Field(
        default=None,
        description="Anthropic API key"
    )
    anthropic_model: str = Field(
        default="claude-3-sonnet-20240229",
        description="Anthropic model name"
    )
    
    # ===== Azure OpenAI Configuration (Optional) =====
    azure_openai_endpoint: Optional[str] = Field(
        default=None,
        description="Azure OpenAI endpoint URL"
    )
    azure_openai_api_key: Optional[str] = Field(
        default=None,
        description="Azure OpenAI API key"
    )
    azure_openai_deployment: Optional[str] = Field(
        default=None,
        description="Azure OpenAI deployment name"
    )
    azure_openai_api_version: str = Field(
        default="2024-02-15-preview",
        description="Azure OpenAI API version"
    )
    
    # ===== OpenRouter Configuration =====
    openrouter_api_key: Optional[str] = Field(
        default=None,
        description="OpenRouter API key (for direct usage)"
    )
    openrouter_provisioning_key: Optional[str] = Field(
        default=None,
        description="OpenRouter provisioning API key (for creating tenant keys)"
    )
    openrouter_model: str = Field(
        default="openai/gpt-4-turbo",
        description="Default OpenRouter model"
    )
    app_url: str = Field(
        default="https://unified-temporal-worker.azurecontainerapps.io",
        description="Application URL for OpenRouter attribution"
    )
    use_openrouter: bool = Field(
        default=False,
        description="Use OpenRouter instead of direct providers (feature flag)"
    )
    
    # ===== Fallback Configuration =====
    fallback_enabled: bool = Field(
        default=True,
        description="Enable fallback to alternative model on failure"
    )
    fallback_model: str = Field(
        default="gpt-3.5-turbo",
        description="Fallback model name"
    )
    
    # ===== Rate Limiting Configuration =====
    use_improved_rate_limiter: bool = Field(
        default=True,
        description="Use improved rate limiter v2 with pyrate_limiter (better async handling)"
    )
    max_requests_per_second: int = Field(
        default=100,
        gt=0,
        description="Global rate limit (requests per second)"
    )
    max_concurrent_requests: int = Field(
        default=50,
        gt=0,
        description="Maximum concurrent requests"
    )
    max_requests_per_minute_per_tenant: int = Field(
        default=100,
        gt=0,
        description="Per-tenant rate limit (requests per minute)"
    )
    max_tokens_per_day_per_tenant: int = Field(
        default=1000000,
        gt=0,
        description="Per-tenant token quota (tokens per day)"
    )
    max_cost_per_day_per_tenant_usd: float = Field(
        default=100.0,
        gt=0.0,
        description="Per-tenant cost quota (USD per day)"
    )
    max_requests_per_minute_per_user: int = Field(
        default=10,
        gt=0,
        description="Per-user rate limit (requests per minute)"
    )
    
    # ===== Redis Configuration (for rate limiting & caching) =====
    redis_url: str = Field(
        default="redis://localhost:6379/0",
        description="Redis connection URL"
    )
    redis_enabled: bool = Field(
        default=True,
        description="Enable Redis for rate limiting and caching"
    )
    
    # ===== Opik Configuration =====
    opik_enabled: bool = Field(
        default=True,
        description="Enable Opik tracing for all LLM calls"
    )
    opik_project_name: str = Field(
        default="unified-temporal-worker",
        description="Opik project name"
    )
    opik_workspace: Optional[str] = Field(
        default=None,
        description="Opik workspace name"
    )
    opik_api_key: Optional[str] = Field(
        default=None,
        description="Opik API key (if using cloud)"
    )
    
    # ===== Caching Configuration =====
    cache_enabled: bool = Field(
        default=True,
        description="Enable response caching"
    )
    cache_ttl: int = Field(
        default=3600,
        gt=0,
        description="Cache TTL in seconds (default: 1 hour)"
    )
    cache_max_size_mb: int = Field(
        default=100,
        gt=0,
        description="Maximum cache size in MB"
    )
    
    # ===== Retry Configuration =====
    retry_enabled: bool = Field(
        default=True,
        description="Enable retry logic"
    )
    retry_max_attempts: int = Field(
        default=3,
        gt=0,
        description="Maximum retry attempts"
    )
    retry_min_wait_seconds: int = Field(
        default=4,
        gt=0,
        description="Minimum wait between retries (exponential backoff)"
    )
    retry_max_wait_seconds: int = Field(
        default=10,
        gt=0,
        description="Maximum wait between retries"
    )
    
    # ===== Circuit Breaker Configuration =====
    circuit_breaker_enabled: bool = Field(
        default=True,
        description="Enable circuit breaker"
    )
    circuit_breaker_failure_threshold: int = Field(
        default=5,
        gt=0,
        description="Failures before opening circuit"
    )
    circuit_breaker_recovery_timeout: int = Field(
        default=60,
        gt=0,
        description="Seconds before attempting recovery"
    )
    
    # ===== Logging Configuration =====
    log_level: str = Field(
        default="INFO",
        description="Logging level (DEBUG, INFO, WARNING, ERROR)"
    )
    log_prompts: bool = Field(
        default=False,
        description="Log full prompts (may contain PII)"
    )
    log_responses: bool = Field(
        default=False,
        description="Log full responses (may contain PII)"
    )
    
    # ===== Cost Tracking Configuration =====
    track_costs: bool = Field(
        default=True,
        description="Track token usage and costs"
    )
    cost_per_1k_prompt_tokens: float = Field(
        default=0.01,
        ge=0.0,
        description="Cost per 1K prompt tokens (USD) - GPT-4 default"
    )
    cost_per_1k_completion_tokens: float = Field(
        default=0.03,
        ge=0.0,
        description="Cost per 1K completion tokens (USD) - GPT-4 default"
    )
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False
        # Map environment variables to fields
        env_prefix = ""
        
        # Allow extra fields for forward compatibility
        extra = "ignore"
    
    def get_api_key(self) -> str:
        """Get API key for current provider"""
        if self.provider == "openai":
            if not self.openai_api_key:
                raise ValueError("OPENAI_API_KEY not set in environment")
            return self.openai_api_key
        elif self.provider == "anthropic":
            if not self.anthropic_api_key:
                raise ValueError("ANTHROPIC_API_KEY not set in environment")
            return self.anthropic_api_key
        elif self.provider == "azure-openai":
            if not self.azure_openai_api_key:
                raise ValueError("AZURE_OPENAI_API_KEY not set in environment")
            return self.azure_openai_api_key
        else:
            raise ValueError(f"Unknown provider: {self.provider}")
    
    def get_model(self) -> str:
        """Get model name for current provider"""
        if self.provider == "openai":
            return self.openai_model
        elif self.provider == "anthropic":
            return self.anthropic_model
        elif self.provider == "azure-openai":
            if not self.azure_openai_deployment:
                raise ValueError("AZURE_OPENAI_DEPLOYMENT not set")
            return self.azure_openai_deployment
        else:
            raise ValueError(f"Unknown provider: {self.provider}")
    
    def validate_config(self) -> None:
        """Validate configuration on startup"""
        # If using OpenRouter, skip standard provider validation
        if self.use_openrouter:
            if not self.openrouter_api_key:
                raise ValueError("OPENROUTER_API_KEY not set but use_openrouter=True")
            return
        
        # Validate provider
        valid_providers = ["openai", "anthropic", "azure-openai"]
        if self.provider not in valid_providers:
            raise ValueError(f"Invalid provider: {self.provider}. Must be one of {valid_providers}")
        
        # Validate API key exists
        try:
            self.get_api_key()
        except ValueError as e:
            raise ValueError(f"Configuration error: {e}")
        
        # Validate Redis if enabled
        if self.redis_enabled and not self.redis_url:
            raise ValueError("REDIS_URL not set but redis_enabled=True")
        
        # Validate rate limits
        if self.max_requests_per_second <= 0:
            raise ValueError("max_requests_per_second must be > 0")
        
        # Validate retry config
        if self.retry_min_wait_seconds >= self.retry_max_wait_seconds:
            raise ValueError("retry_min_wait_seconds must be < retry_max_wait_seconds")
    
    # ==========================================
    # RAG (Retrieval-Augmented Generation) Configuration
    # ==========================================
    
    rag_enabled: bool = Field(
        default=False,
        description="Enable RAG (Retrieval-Augmented Generation) with vector store"
    )
    
    # Vector Database Configuration
    vector_db_provider: str = Field(
        default="pinecone",
        description="Vector database provider (pinecone, weaviate, qdrant)"
    )
    pinecone_api_key: Optional[str] = Field(
        default=None,
        description="Pinecone API key"
    )
    pinecone_environment: str = Field(
        default="us-east-1-aws",
        description="Pinecone environment"
    )
    pinecone_index_name: str = Field(
        default="timesheet-memory",
        description="Pinecone index name"
    )
    
    # Qdrant Configuration
    qdrant_url: Optional[str] = Field(
        default=None,
        description="Qdrant server URL (e.g., http://localhost:6333 or cloud URL)"
    )
    qdrant_api_key: Optional[str] = Field(
        default=None,
        description="Qdrant API key (for cloud deployment)"
    )
    qdrant_collection_name: str = Field(
        default="timesheet_memory",
        description="Qdrant collection name"
    )
    
    # Weaviate Configuration
    weaviate_url: Optional[str] = Field(
        default=None,
        description="Weaviate server URL (e.g., http://localhost:8080)"
    )
    weaviate_api_key: Optional[str] = Field(
        default=None,
        description="Weaviate API key (if authentication enabled)"
    )
    
    # Embeddings Configuration
    embeddings_provider: str = Field(
        default="openai",
        description="Embeddings provider (openai, cohere, huggingface)"
    )
    embeddings_model: str = Field(
        default="text-embedding-3-small",
        description="Embeddings model name"
    )
    embeddings_dimension: int = Field(
        default=1536,
        description="Embedding vector dimension"
    )
    
    # Memory Retrieval Configuration
    memory_retrieval_k: int = Field(
        default=10,
        gt=0,
        description="Number of relevant memories to retrieve (increased from 5 to improve recall)"
    )
    memory_retrieval_method: str = Field(
        default="mmr",
        description="Retrieval method (similarity, mmr, similarity_score_threshold)"
    )
    memory_mmr_diversity: float = Field(
        default=0.5,
        ge=0.0,
        le=1.0,
        description="MMR diversity parameter (0=diverse, 1=relevant)"
    )
    
    # ==========================================
    # Tool Registry Configuration
    # ==========================================
    
    tool_registry_enabled: bool = Field(
        default=False,
        description="Enable unified tool registry"
    )
    tool_registry_cache_ttl: int = Field(
        default=3600,
        gt=0,
        description="Tool registry cache TTL in seconds"
    )
    tool_credentials_encryption_key: Optional[str] = Field(
        default=None,
        description="Fernet encryption key for tool credentials"
    )
