"""
In-Memory Rate Limiter

Multi-level rate limiting for LLM calls using in-memory sliding window:
- Global: requests per second (per container)
- Per-tenant: requests per minute (per container)
- Per-user: requests per minute (per container)

Note: This is NOT distributed across containers. Each container maintains
its own rate limits. For distributed rate limiting, use OpenRouter's
per-tenant API keys with credit limits.
"""

import time
import logging
from typing import Optional
from collections import deque, defaultdict

from llm.config import LLMConfig

logger = logging.getLogger(__name__)


class RateLimitExceeded(Exception):
    """Raised when rate limit is exceeded"""
    
    def __init__(self, message: str, retry_after: Optional[float] = None):
        super().__init__(message)
        self.retry_after = retry_after


class InMemoryRateLimiter:
    """
    In-memory rate limiter using sliding window algorithm
    
    Implements:
    - Global rate limiting (requests per second, per container)
    - Per-tenant rate limiting (requests per minute, per container)
    - Per-user rate limiting (requests per minute, per container)
    
    Trade-offs:
    - ✅ Much simpler than Redis (no external dependency)
    - ✅ Faster (no network calls)
    - ✅ Lower memory usage
    - ⚠️ Not distributed (each container has independent limits)
    - ⚠️ Lost on container restart (acceptable for rate limiting)
    
    For distributed per-tenant cost limits, use OpenRouter API keys.
    """
    
    def __init__(self, config: LLMConfig):
        """
        Initialize in-memory rate limiter
        
        Args:
            config: LLM configuration
        """
        self.config = config
        
        # Sliding window queues (store timestamps)
        self.global_requests = deque()  # Global requests (per-second)
        self.tenant_requests = defaultdict(deque)  # Per-tenant requests (per-minute)
        self.user_requests = defaultdict(deque)  # Per-user requests (per-minute)
        
        # Statistics
        self.total_requests = 0
        self.total_rate_limited = 0
        
        logger.info(
            f"In-memory rate limiter initialized: "
            f"global={config.max_requests_per_second} RPS, "
            f"tenant={config.max_requests_per_minute_per_tenant} RPM, "
            f"user={config.max_requests_per_minute_per_user} RPM"
        )
    
    async def acquire(
        self,
        tenant_id: Optional[str] = None,
        user_id: Optional[str] = None,
        estimated_tokens: int = 0
    ):
        """
        Acquire rate limit tokens
        
        Args:
            tenant_id: Tenant ID
            user_id: User ID
            estimated_tokens: Estimated tokens (ignored in in-memory version)
        
        Raises:
            RateLimitExceeded: If rate limit exceeded
        """
        now = time.time()
        self.total_requests += 1
        
        # Check global rate limit (per-second)
        await self._check_global_rate_limit(now)
        
        # Check per-tenant rate limit (per-minute)
        if tenant_id:
            await self._check_tenant_rate_limit(tenant_id, now)
        
        # Check per-user rate limit (per-minute)
        if user_id:
            await self._check_user_rate_limit(user_id, now)
        
        logger.debug(
            f"Rate limit acquired: tenant={tenant_id}, user={user_id}, "
            f"global={len(self.global_requests)}/{self.config.max_requests_per_second}"
        )
    
    async def _check_global_rate_limit(self, now: float):
        """
        Check global rate limit (requests per second)
        
        Args:
            now: Current timestamp
        
        Raises:
            RateLimitExceeded: If global limit exceeded
        """
        # Clean old requests (older than 1 second)
        self._clean_old_requests(self.global_requests, now, window_seconds=1)
        
        # Check if limit exceeded
        if len(self.global_requests) >= self.config.max_requests_per_second:
            self.total_rate_limited += 1
            logger.warning(
                f"Global rate limit exceeded: "
                f"{len(self.global_requests)}/{self.config.max_requests_per_second} RPS"
            )
            raise RateLimitExceeded(
                f"Global rate limit exceeded ({self.config.max_requests_per_second} RPS)",
                retry_after=1.0
            )
        
        # Add current request
        self.global_requests.append(now)
    
    async def _check_tenant_rate_limit(self, tenant_id: str, now: float):
        """
        Check per-tenant rate limit (requests per minute)
        
        Args:
            tenant_id: Tenant ID
            now: Current timestamp
        
        Raises:
            RateLimitExceeded: If tenant limit exceeded
        """
        # Clean old requests (older than 60 seconds)
        self._clean_old_requests(
            self.tenant_requests[tenant_id],
            now,
            window_seconds=60
        )
        
        # Check if limit exceeded
        tenant_count = len(self.tenant_requests[tenant_id])
        if tenant_count >= self.config.max_requests_per_minute_per_tenant:
            self.total_rate_limited += 1
            logger.warning(
                f"Tenant rate limit exceeded: tenant={tenant_id}, "
                f"{tenant_count}/{self.config.max_requests_per_minute_per_tenant} RPM"
            )
            raise RateLimitExceeded(
                f"Tenant {tenant_id} rate limit exceeded "
                f"({self.config.max_requests_per_minute_per_tenant} RPM)",
                retry_after=60.0
            )
        
        # Add current request
        self.tenant_requests[tenant_id].append(now)
    
    async def _check_user_rate_limit(self, user_id: str, now: float):
        """
        Check per-user rate limit (requests per minute)
        
        Args:
            user_id: User ID
            now: Current timestamp
        
        Raises:
            RateLimitExceeded: If user limit exceeded
        """
        # Clean old requests (older than 60 seconds)
        self._clean_old_requests(
            self.user_requests[user_id],
            now,
            window_seconds=60
        )
        
        # Check if limit exceeded
        user_count = len(self.user_requests[user_id])
        if user_count >= self.config.max_requests_per_minute_per_user:
            self.total_rate_limited += 1
            logger.warning(
                f"User rate limit exceeded: user={user_id}, "
                f"{user_count}/{self.config.max_requests_per_minute_per_user} RPM"
            )
            raise RateLimitExceeded(
                f"User {user_id} rate limit exceeded "
                f"({self.config.max_requests_per_minute_per_user} RPM)",
                retry_after=60.0
            )
        
        # Add current request
        self.user_requests[user_id].append(now)
    
    def _clean_old_requests(
        self,
        queue: deque,
        now: float,
        window_seconds: int
    ):
        """
        Remove requests older than window
        
        Args:
            queue: Request queue (deque of timestamps)
            now: Current timestamp
            window_seconds: Window size in seconds
        """
        cutoff = now - window_seconds
        while queue and queue[0] < cutoff:
            queue.popleft()
    
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
            "total_rate_limited": self.total_rate_limited,
            "rate_limit_percentage": (
                (self.total_rate_limited / self.total_requests * 100)
                if self.total_requests > 0 else 0.0
            ),
            "global_requests_last_second": len(self.global_requests),
            "total_tenants_tracked": len(self.tenant_requests),
            "total_users_tracked": len(self.user_requests),
            "config": {
                "max_requests_per_second": self.config.max_requests_per_second,
                "max_requests_per_minute_per_tenant": self.config.max_requests_per_minute_per_tenant,
                "max_requests_per_minute_per_user": self.config.max_requests_per_minute_per_user,
            }
        }
    
    async def close(self):
        """Close connections (no-op for in-memory)"""
        logger.debug("In-memory rate limiter closed")
        
        # Log final stats
        stats = self.get_stats()
        logger.info(
            f"Rate limiter stats: "
            f"total={stats['total_requests']}, "
            f"limited={stats['total_rate_limited']} "
            f"({stats['rate_limit_percentage']:.2f}%)"
        )


# Alias for backward compatibility
RateLimiter = InMemoryRateLimiter
