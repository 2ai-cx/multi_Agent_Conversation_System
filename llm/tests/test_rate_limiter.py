"""
Tests for In-Memory Rate Limiter

Tests cover:
- Global rate limiting
- Per-tenant rate limiting
- Per-user rate limiting
- Sliding window cleanup
- Statistics tracking
"""

import pytest
import asyncio
import time
from llm.rate_limiter import InMemoryRateLimiter, RateLimitExceeded
from llm.config import LLMConfig


@pytest.fixture
def config():
    """Create test configuration"""
    return LLMConfig(
        max_requests_per_second=100,  # High enough to not interfere with tenant/user tests
        max_requests_per_minute_per_tenant=10,
        max_requests_per_minute_per_user=3
    )


@pytest.fixture
def rate_limiter(config):
    """Create rate limiter instance"""
    return InMemoryRateLimiter(config)


class TestGlobalRateLimiting:
    """Test global rate limiting (per-second)"""
    
    @pytest.fixture
    def global_config(self):
        """Config with low global limit for testing"""
        return LLMConfig(
            max_requests_per_second=5,
            max_requests_per_minute_per_tenant=100,
            max_requests_per_minute_per_user=100
        )
    
    @pytest.fixture
    def global_limiter(self, global_config):
        """Rate limiter with low global limit"""
        return InMemoryRateLimiter(global_config)
    
    @pytest.mark.asyncio
    async def test_global_limit_not_exceeded(self, global_limiter):
        """Test requests within global limit"""
        # Should allow 5 requests per second
        for i in range(5):
            await global_limiter.acquire()
        
        # All requests should succeed
        assert global_limiter.total_requests == 5
        assert global_limiter.total_rate_limited == 0
    
    @pytest.mark.asyncio
    async def test_global_limit_exceeded(self, global_limiter):
        """Test requests exceeding global limit"""
        # Fill up the limit
        for i in range(5):
            await global_limiter.acquire()
        
        # 6th request should fail
        with pytest.raises(RateLimitExceeded) as exc_info:
            await global_limiter.acquire()
        
        assert "Global rate limit exceeded" in str(exc_info.value)
        assert exc_info.value.retry_after == 1.0
        assert global_limiter.total_rate_limited == 1
    
    @pytest.mark.asyncio
    async def test_global_limit_resets_after_window(self, global_limiter):
        """Test that global limit resets after 1 second"""
        # Fill up the limit
        for i in range(5):
            await global_limiter.acquire()
        
        # Wait for window to pass
        await asyncio.sleep(1.1)
        
        # Should allow new requests
        await global_limiter.acquire()
        assert global_limiter.total_requests == 6


class TestTenantRateLimiting:
    """Test per-tenant rate limiting (per-minute)"""
    
    @pytest.mark.asyncio
    async def test_tenant_limit_not_exceeded(self, rate_limiter):
        """Test requests within tenant limit"""
        tenant_id = "tenant-123"
        
        # Should allow 10 requests per minute
        for i in range(10):
            await rate_limiter.acquire(tenant_id=tenant_id)
        
        assert rate_limiter.total_requests == 10
        assert rate_limiter.total_rate_limited == 0
    
    @pytest.mark.asyncio
    async def test_tenant_limit_exceeded(self, rate_limiter):
        """Test requests exceeding tenant limit"""
        tenant_id = "tenant-123"
        
        # Fill up the limit
        for i in range(10):
            await rate_limiter.acquire(tenant_id=tenant_id)
        
        # 11th request should fail
        with pytest.raises(RateLimitExceeded) as exc_info:
            await rate_limiter.acquire(tenant_id=tenant_id)
        
        assert "tenant-123" in str(exc_info.value)
        assert "rate limit exceeded" in str(exc_info.value).lower()
        assert exc_info.value.retry_after == 60.0
    
    @pytest.mark.asyncio
    async def test_different_tenants_independent(self, rate_limiter):
        """Test that different tenants have independent limits"""
        # Fill up tenant-1
        for i in range(10):
            await rate_limiter.acquire(tenant_id="tenant-1")
        
        # tenant-2 should still work
        await rate_limiter.acquire(tenant_id="tenant-2")
        
        # tenant-1 should be blocked
        with pytest.raises(RateLimitExceeded):
            await rate_limiter.acquire(tenant_id="tenant-1")


class TestUserRateLimiting:
    """Test per-user rate limiting (per-minute)"""
    
    @pytest.mark.asyncio
    async def test_user_limit_not_exceeded(self, rate_limiter):
        """Test requests within user limit"""
        user_id = "user-456"
        
        # Should allow 3 requests per minute
        for i in range(3):
            await rate_limiter.acquire(user_id=user_id)
        
        assert rate_limiter.total_requests == 3
        assert rate_limiter.total_rate_limited == 0
    
    @pytest.mark.asyncio
    async def test_user_limit_exceeded(self, rate_limiter):
        """Test requests exceeding user limit"""
        user_id = "user-456"
        
        # Fill up the limit
        for i in range(3):
            await rate_limiter.acquire(user_id=user_id)
        
        # 4th request should fail
        with pytest.raises(RateLimitExceeded) as exc_info:
            await rate_limiter.acquire(user_id=user_id)
        
        assert "user-456" in str(exc_info.value)
        assert exc_info.value.retry_after == 60.0
    
    @pytest.mark.asyncio
    async def test_different_users_independent(self, rate_limiter):
        """Test that different users have independent limits"""
        # Fill up user-1
        for i in range(3):
            await rate_limiter.acquire(user_id="user-1")
        
        # user-2 should still work
        await rate_limiter.acquire(user_id="user-2")
        
        # user-1 should be blocked
        with pytest.raises(RateLimitExceeded):
            await rate_limiter.acquire(user_id="user-1")


class TestSlidingWindow:
    """Test sliding window algorithm"""
    
    @pytest.fixture
    def sliding_config(self):
        """Config with low global limit for sliding window tests"""
        return LLMConfig(
            max_requests_per_second=5,
            max_requests_per_minute_per_tenant=100,
            max_requests_per_minute_per_user=100
        )
    
    @pytest.fixture
    def sliding_limiter(self, sliding_config):
        """Rate limiter for sliding window tests"""
        return InMemoryRateLimiter(sliding_config)
    
    @pytest.mark.asyncio
    async def test_old_requests_cleaned_up(self, sliding_limiter):
        """Test that old requests are removed from window"""
        # Make some requests
        for i in range(3):
            await sliding_limiter.acquire()
        
        # Wait for window to pass
        await asyncio.sleep(1.1)
        
        # Old requests should be cleaned up automatically on next acquire
        # Make a new request which will trigger cleanup
        await sliding_limiter.acquire()
        
        # Should only have 1 request now (the new one)
        assert len(sliding_limiter.global_requests) == 1
    
    @pytest.mark.asyncio
    async def test_sliding_window_allows_gradual_requests(self, sliding_limiter):
        """Test that sliding window allows gradual requests"""
        # Make 5 requests (fill limit)
        for i in range(5):
            await sliding_limiter.acquire()
        
        # Wait 0.5 seconds
        await asyncio.sleep(0.5)
        
        # Make 2 more requests (should fail - still in window)
        with pytest.raises(RateLimitExceeded):
            await sliding_limiter.acquire()
        
        # Wait another 0.6 seconds (total 1.1s)
        await asyncio.sleep(0.6)
        
        # Should allow new requests now
        await sliding_limiter.acquire()


class TestStatistics:
    """Test statistics tracking"""
    
    @pytest.fixture
    def stats_config(self):
        """Config for statistics tests"""
        return LLMConfig(
            max_requests_per_second=5,
            max_requests_per_minute_per_tenant=100,
            max_requests_per_minute_per_user=100
        )
    
    @pytest.fixture
    def stats_limiter(self, stats_config):
        """Rate limiter for statistics tests"""
        return InMemoryRateLimiter(stats_config)
    
    @pytest.mark.asyncio
    async def test_stats_tracking(self, stats_limiter):
        """Test that statistics are tracked correctly"""
        # Make some successful requests
        for i in range(3):
            await stats_limiter.acquire(tenant_id="tenant-1", user_id="user-1")
        
        # Make more requests to hit limit (only 2 more to stay under 5)
        for i in range(2):
            await stats_limiter.acquire()
        
        # This should fail (6th request)
        try:
            await stats_limiter.acquire()
        except RateLimitExceeded:
            pass
        
        # Check stats
        stats = stats_limiter.get_stats()
        assert stats['total_requests'] == 6
        assert stats['total_rate_limited'] == 1
        assert stats['total_tenants_tracked'] == 1
        assert stats['total_users_tracked'] == 1
    
    @pytest.mark.asyncio
    async def test_rate_limit_percentage(self, stats_limiter):
        """Test rate limit percentage calculation"""
        # Make 5 successful requests
        for i in range(5):
            await stats_limiter.acquire()
        
        # These 2 should fail
        for i in range(2):
            try:
                await stats_limiter.acquire()
            except RateLimitExceeded:
                pass
        
        stats = stats_limiter.get_stats()
        # 2 rate limited out of 7 total = ~28.6%
        assert stats['rate_limit_percentage'] > 25
        assert stats['rate_limit_percentage'] < 30


class TestRecordTokens:
    """Test token recording (no-op in in-memory version)"""
    
    @pytest.mark.asyncio
    async def test_record_tokens_no_op(self, rate_limiter):
        """Test that record_tokens is a no-op"""
        # Should not raise any errors
        await rate_limiter.record_tokens(
            tenant_id="tenant-123",
            tokens=1000,
            cost_usd=0.05
        )
        
        # Should not affect rate limiting
        await rate_limiter.acquire(tenant_id="tenant-123")


class TestClose:
    """Test cleanup"""
    
    @pytest.mark.asyncio
    async def test_close_logs_stats(self, rate_limiter):
        """Test that close logs final statistics"""
        # Make some requests
        for i in range(5):
            await rate_limiter.acquire()
        
        # Close should not raise errors
        await rate_limiter.close()


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
