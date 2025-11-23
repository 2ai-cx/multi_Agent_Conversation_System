"""
Improved In-Memory Rate Limiter using pyrate_limiter

Multi-level rate limiting for LLM calls with better async handling:
- Global: requests per second (per container)
- Per-tenant: requests per minute (per container)
- Per-user: requests per minute (per container)

Improvements over v1:
- ✅ Non-blocking waits (uses pyrate_limiter's async queuing)
- ✅ Automatic retry with fair ordering (FIFO)
- ✅ Better handling of burst traffic
- ✅ Simpler code (no manual exception handling)
- ✅ Same API as v1 (drop-in replacement)

Note: This is NOT distributed across containers. Each container maintains
its own rate limits. For distributed rate limiting, use OpenRouter's
per-tenant API keys with credit limits.
"""

import logging
from typing import Optional

from pyrate_limiter import Duration
from pyrate_limiter.limiter_factory import create_inmemory_limiter

from llm.config import LLMConfig

logger = logging.getLogger(__name__)


class RateLimitExceeded(Exception):
    """Raised when rate limit is exceeded (kept for backward compatibility)"""
    
    def __init__(self, message: str, retry_after: Optional[float] = None):
        super().__init__(message)
        self.retry_after = retry_after


class InMemoryRateLimiterV2:
    """
    Improved in-memory rate limiter using pyrate_limiter
    
    Implements:
    - Global rate limiting (requests per second, per container)
    - Per-tenant rate limiting (requests per minute, per container)
    - Per-user rate limiting (requests per minute, per container)
    
    Key Features:
    - ✅ Non-blocking async waits (doesn't block event loop)
    - ✅ Automatic queuing and retry
    - ✅ Fair ordering (FIFO)
    - ✅ Better burst handling
    
    Trade-offs:
    - ✅ Much simpler than Redis (no external dependency)
    - ✅ Faster (no network calls)
    - ✅ Better async handling than v1
    - ⚠️ Not distributed (each container has independent limits)
    - ⚠️ Lost on container restart (acceptable for rate limiting)
    
    For distributed per-tenant cost limits, use OpenRouter API keys.
    """
    
    def __init__(self, config: LLMConfig):
        """
        Initialize improved rate limiter
        
        Args:
            config: LLM configuration
        """
        self.config = config
        
        # Create limiters for each level
        # Global: requests per second
        self.global_limiter = create_inmemory_limiter(
            rate_per_duration=config.max_requests_per_second,
            duration=Duration.SECOND,
            async_wrapper=True
        )
        
        # Per-tenant: requests per minute
        # We'll create these on-demand
        self.tenant_limiters = {}
        
        # Per-user: requests per minute
        # We'll create these on-demand
        self.user_limiters = {}
        
        # Statistics
        self.total_requests = 0
        self.total_rate_limited = 0  # Not used with pyrate_limiter (auto-waits)
        
        logger.info(
            f"Improved rate limiter (v2) initialized: "
            f"global={config.max_requests_per_second} RPS, "
            f"tenant={config.max_requests_per_minute_per_tenant} RPM, "
            f"user={config.max_requests_per_minute_per_user} RPM"
        )
    
    def _get_tenant_limiter(self, tenant_id: str):
        """Get or create limiter for tenant"""
        if tenant_id not in self.tenant_limiters:
            self.tenant_limiters[tenant_id] = create_inmemory_limiter(
                rate_per_duration=self.config.max_requests_per_minute_per_tenant,
                duration=Duration.MINUTE,
                async_wrapper=True
            )
        return self.tenant_limiters[tenant_id]
    
    def _get_user_limiter(self, user_id: str):
        """Get or create limiter for user"""
        if user_id not in self.user_limiters:
            self.user_limiters[user_id] = create_inmemory_limiter(
                rate_per_duration=self.config.max_requests_per_minute_per_user,
                duration=Duration.MINUTE,
                async_wrapper=True
            )
        return self.user_limiters[user_id]
    
    async def acquire(
        self,
        tenant_id: Optional[str] = None,
        user_id: Optional[str] = None,
        estimated_tokens: int = 0
    ):
        """
        Acquire rate limit tokens (with automatic waiting)
        
        This method will automatically wait if rate limits are exceeded,
        without raising exceptions. The wait is non-blocking.
        
        Args:
            tenant_id: Tenant ID
            user_id: User ID
            estimated_tokens: Estimated tokens (ignored in in-memory version)
        
        Note: Unlike v1, this does NOT raise RateLimitExceeded.
              It waits automatically until capacity is available.
        """
        self.total_requests += 1
        
        # Acquire global rate limit (waits if needed)
        await self.global_limiter.try_acquire_async("global", 1)
        
        # Acquire per-tenant rate limit (waits if needed)
        if tenant_id:
            tenant_limiter = self._get_tenant_limiter(tenant_id)
            await tenant_limiter.try_acquire_async(f"tenant:{tenant_id}", 1)
        
        # Acquire per-user rate limit (waits if needed)
        if user_id:
            user_limiter = self._get_user_limiter(user_id)
            await user_limiter.try_acquire_async(f"user:{user_id}", 1)
        
        logger.debug(
            f"Rate limit acquired: tenant={tenant_id}, user={user_id}"
        )
    
    async def record_tokens(
        self,
        tenant_id: Optional[str] = None,
        tokens: int = 0,
        cost_usd: float = 0.0
    ):
        """
        Record token usage (no-op in in-memory version)
        
        Token quotas are enforced by OpenRouter API keys, not locally.
        
        Args:
            tenant_id: Tenant ID
            tokens: Number of tokens used
            cost_usd: Cost in USD
        """
        # No-op: OpenRouter handles token/cost quotas via API keys
        logger.debug(
            f"Token usage recorded (informational only): "
            f"tenant={tenant_id}, tokens={tokens}, cost=${cost_usd:.4f}"
        )
    
    def get_stats(self) -> dict:
        """
        Get rate limiter statistics
        
        Returns:
            Dictionary with stats
        """
        return {
            "total_requests": self.total_requests,
            "total_rate_limited": 0,  # pyrate_limiter auto-waits, no rejections
            "rate_limit_percentage": 0.0,
            "total_tenants_tracked": len(self.tenant_limiters),
            "total_users_tracked": len(self.user_limiters),
            "config": {
                "max_requests_per_second": self.config.max_requests_per_second,
                "max_requests_per_minute_per_tenant": self.config.max_requests_per_minute_per_tenant,
                "max_requests_per_minute_per_user": self.config.max_requests_per_minute_per_user,
            },
            "version": "v2 (pyrate_limiter)"
        }
    
    async def close(self):
        """Close connections (no-op for in-memory)"""
        logger.debug("Improved rate limiter (v2) closed")
        
        # Log final stats
        stats = self.get_stats()
        logger.info(
            f"Rate limiter stats: "
            f"total={stats['total_requests']}, "
            f"tenants={stats['total_tenants_tracked']}, "
            f"users={stats['total_users_tracked']}"
        )


# Alias for backward compatibility
RateLimiterV2 = InMemoryRateLimiterV2
