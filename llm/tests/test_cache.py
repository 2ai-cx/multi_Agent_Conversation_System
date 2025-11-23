"""
Tests for In-Memory Cache

Tests cover:
- Cache get/set operations
- LRU eviction
- TTL expiration
- Cache key generation
- Statistics tracking
"""

import pytest
import asyncio
import time
from llm.cache import InMemoryCache, CacheEntry, generate_cache_key
from llm.client import LLMResponse
from llm.config import LLMConfig


@pytest.fixture
def config():
    """Create test configuration"""
    return LLMConfig(
        cache_enabled=True,
        cache_ttl=2,  # 2 seconds for faster testing
        cache_max_size_mb=1  # Small cache for testing eviction
    )


@pytest.fixture
def cache(config):
    """Create cache instance"""
    return InMemoryCache(config)


@pytest.fixture
def sample_response():
    """Create sample LLM response"""
    return LLMResponse(
        content="Hello, world!",
        model="gpt-4",
        prompt_tokens=10,
        completion_tokens=5,
        total_tokens=15,
        latency_ms=100.0,
        cost_usd=0.001,
        cached=False
    )


class TestCacheOperations:
    """Test basic cache operations"""
    
    @pytest.mark.asyncio
    async def test_cache_miss(self, cache):
        """Test cache miss returns None"""
        result = await cache.get("nonexistent-key")
        assert result is None
        assert cache.misses == 1
        assert cache.hits == 0
    
    @pytest.mark.asyncio
    async def test_cache_set_and_get(self, cache, sample_response):
        """Test setting and getting from cache"""
        key = "test-key"
        
        # Set in cache
        await cache.set(key, sample_response)
        
        # Get from cache
        result = await cache.get(key)
        
        assert result is not None
        assert result.content == sample_response.content
        assert result.cached == True  # Should be marked as cached
        assert cache.hits == 1
        assert cache.misses == 0
    
    @pytest.mark.asyncio
    async def test_cache_delete(self, cache, sample_response):
        """Test deleting from cache"""
        key = "test-key"
        
        # Set in cache
        await cache.set(key, sample_response)
        
        # Delete from cache
        await cache.delete(key)
        
        # Should be gone
        result = await cache.get(key)
        assert result is None
    
    @pytest.mark.asyncio
    async def test_cache_clear(self, cache, sample_response):
        """Test clearing entire cache"""
        # Add multiple entries
        for i in range(5):
            await cache.set(f"key-{i}", sample_response)
        
        # Clear cache
        await cache.clear()
        
        # All should be gone
        for i in range(5):
            result = await cache.get(f"key-{i}")
            assert result is None


class TestLRUEviction:
    """Test LRU eviction algorithm"""
    
    @pytest.mark.asyncio
    async def test_lru_eviction_when_full(self, cache, sample_response):
        """Test that oldest entry is evicted when cache is full"""
        max_entries = cache.max_entries
        
        # Fill cache to capacity
        for i in range(max_entries):
            await cache.set(f"key-{i}", sample_response)
        
        # Add one more (should evict key-0)
        await cache.set("key-new", sample_response)
        
        # key-0 should be evicted
        result = await cache.get("key-0")
        assert result is None
        
        # key-new should exist
        result = await cache.get("key-new")
        assert result is not None
        
        # Should have recorded eviction
        assert cache.evictions == 1
    
    @pytest.mark.asyncio
    async def test_lru_access_updates_order(self, cache, sample_response):
        """Test that accessing an entry moves it to end (most recent)"""
        max_entries = cache.max_entries
        
        # Fill cache
        for i in range(max_entries):
            await cache.set(f"key-{i}", sample_response)
        
        # Access key-0 (should move to end)
        await cache.get("key-0")
        
        # Add new entry (should evict key-1, not key-0)
        await cache.set("key-new", sample_response)
        
        # key-0 should still exist (was accessed recently)
        result = await cache.get("key-0")
        assert result is not None
        
        # key-1 should be evicted (was oldest)
        result = await cache.get("key-1")
        assert result is None


class TestTTLExpiration:
    """Test TTL-based expiration"""
    
    @pytest.mark.asyncio
    async def test_entry_expires_after_ttl(self, cache, sample_response):
        """Test that entries expire after TTL"""
        key = "test-key"
        
        # Set in cache (TTL = 2 seconds)
        await cache.set(key, sample_response)
        
        # Should exist immediately
        result = await cache.get(key)
        assert result is not None
        
        # Wait for TTL to expire
        await asyncio.sleep(2.1)
        
        # Should be expired
        result = await cache.get(key)
        assert result is None
        assert cache.expirations == 1
    
    @pytest.mark.asyncio
    async def test_entry_not_expired_before_ttl(self, cache, sample_response):
        """Test that entries don't expire before TTL"""
        key = "test-key"
        
        # Set in cache (TTL = 2 seconds)
        await cache.set(key, sample_response)
        
        # Wait 1 second (less than TTL)
        await asyncio.sleep(1.0)
        
        # Should still exist
        result = await cache.get(key)
        assert result is not None
        assert cache.expirations == 0
    
    @pytest.mark.asyncio
    async def test_cleanup_expired_entries(self, cache, sample_response):
        """Test that cleanup removes expired entries"""
        # Add multiple entries
        for i in range(5):
            await cache.set(f"key-{i}", sample_response)
        
        # Wait for expiration
        await asyncio.sleep(2.1)
        
        # Run cleanup
        cache._cleanup_expired()
        
        # All should be expired
        assert cache.expirations == 5
        assert len(cache.cache) == 0


class TestCacheKeyGeneration:
    """Test cache key generation"""
    
    def test_same_inputs_same_key(self):
        """Test that same inputs produce same key"""
        messages = [{"role": "user", "content": "Hello"}]
        model = "gpt-4"
        
        key1 = generate_cache_key(messages, model, temperature=0.7, max_tokens=100)
        key2 = generate_cache_key(messages, model, temperature=0.7, max_tokens=100)
        
        assert key1 == key2
    
    def test_different_messages_different_key(self):
        """Test that different messages produce different keys"""
        model = "gpt-4"
        
        key1 = generate_cache_key(
            [{"role": "user", "content": "Hello"}],
            model, temperature=0.7, max_tokens=100
        )
        key2 = generate_cache_key(
            [{"role": "user", "content": "Goodbye"}],
            model, temperature=0.7, max_tokens=100
        )
        
        assert key1 != key2
    
    def test_different_model_different_key(self):
        """Test that different models produce different keys"""
        messages = [{"role": "user", "content": "Hello"}]
        
        key1 = generate_cache_key(messages, "gpt-4", temperature=0.7, max_tokens=100)
        key2 = generate_cache_key(messages, "gpt-3.5-turbo", temperature=0.7, max_tokens=100)
        
        assert key1 != key2
    
    def test_different_temperature_different_key(self):
        """Test that different temperatures produce different keys"""
        messages = [{"role": "user", "content": "Hello"}]
        model = "gpt-4"
        
        key1 = generate_cache_key(messages, model, temperature=0.7, max_tokens=100)
        key2 = generate_cache_key(messages, model, temperature=0.9, max_tokens=100)
        
        assert key1 != key2


class TestStatistics:
    """Test statistics tracking"""
    
    @pytest.mark.asyncio
    async def test_hit_rate_calculation(self, cache, sample_response):
        """Test hit rate percentage calculation"""
        key = "test-key"
        
        # Set in cache
        await cache.set(key, sample_response)
        
        # 3 hits
        for i in range(3):
            await cache.get(key)
        
        # 2 misses
        for i in range(2):
            await cache.get("nonexistent")
        
        stats = cache.get_stats()
        
        # 3 hits, 2 misses = 60% hit rate
        assert stats['hits'] == 3
        assert stats['misses'] == 2
        assert stats['total_requests'] == 5
        assert abs(stats['hit_rate_percentage'] - 60.0) < 0.1
    
    @pytest.mark.asyncio
    async def test_cost_savings_tracking(self, cache, sample_response):
        """Test that cost savings are tracked"""
        key = "test-key"
        
        # Set in cache (cost = $0.001)
        await cache.set(key, sample_response)
        
        # Get 5 times (should save 5 * $0.001 = $0.005)
        for i in range(5):
            await cache.get(key)
        
        stats = cache.get_stats()
        assert abs(stats['total_cost_saved_usd'] - 0.005) < 0.0001
    
    @pytest.mark.asyncio
    async def test_stats_include_config(self, cache):
        """Test that stats include configuration"""
        stats = cache.get_stats()
        
        assert stats['enabled'] == True
        assert stats['config']['ttl_seconds'] == 2
        assert stats['config']['max_size_mb'] == 1


class TestCacheDisabled:
    """Test cache when disabled"""
    
    @pytest.mark.asyncio
    async def test_cache_disabled_returns_none(self, sample_response):
        """Test that disabled cache always returns None"""
        config = LLMConfig(cache_enabled=False)
        cache = InMemoryCache(config)
        
        # Set should be no-op
        await cache.set("key", sample_response)
        
        # Get should return None
        result = await cache.get("key")
        assert result is None


class TestCacheEntry:
    """Test CacheEntry class"""
    
    def test_cache_entry_creation(self, sample_response):
        """Test creating cache entry"""
        entry = CacheEntry(sample_response, ttl=60)
        
        assert entry.response == sample_response
        assert entry.expires_at > time.time()
        assert entry.created_at <= time.time()
    
    def test_cache_entry_not_expired(self, sample_response):
        """Test entry not expired before TTL"""
        entry = CacheEntry(sample_response, ttl=60)
        assert entry.is_expired() == False
    
    def test_cache_entry_expired(self, sample_response):
        """Test entry expired after TTL"""
        entry = CacheEntry(sample_response, ttl=0)
        time.sleep(0.1)
        assert entry.is_expired() == True


class TestClose:
    """Test cleanup"""
    
    @pytest.mark.asyncio
    async def test_close_logs_stats(self, cache, sample_response):
        """Test that close logs final statistics"""
        # Make some cache operations
        await cache.set("key", sample_response)
        await cache.get("key")
        
        # Close should not raise errors
        await cache.close()
        
        # Cache should be cleared
        assert len(cache.cache) == 0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
