"""
In-Memory Response Cache

LRU cache for LLM responses with TTL-based expiration:
- Least Recently Used (LRU) eviction
- TTL-based expiration
- Size limits
- Hit/miss tracking

Note: This is NOT distributed across containers. Each container maintains
its own cache. For distributed caching, use OpenRouter's prompt caching.
"""

import time
import logging
import hashlib
import json
from typing import Optional, Dict, OrderedDict
from collections import OrderedDict
from dataclasses import asdict

from llm.config import LLMConfig
from llm.client import LLMResponse

logger = logging.getLogger(__name__)


class CacheEntry:
    """Cache entry with TTL"""
    
    def __init__(self, response: LLMResponse, ttl: int):
        self.response = response
        self.expires_at = time.time() + ttl
        self.created_at = time.time()
    
    def is_expired(self) -> bool:
        """Check if entry is expired"""
        return time.time() > self.expires_at


class InMemoryCache:
    """
    In-memory LRU cache with TTL
    
    Features:
    - LRU eviction (least recently used)
    - TTL-based expiration
    - Size limits (max entries)
    - Hit/miss tracking
    - Cost savings calculation
    
    Trade-offs:
    - ✅ Much simpler than Redis (no external dependency)
    - ✅ Faster (no network calls)
    - ✅ Lower memory usage
    - ⚠️ Not distributed (each container has independent cache)
    - ⚠️ Lost on container restart (acceptable for caching)
    
    For distributed caching, use OpenRouter's prompt caching.
    """
    
    def __init__(self, config: LLMConfig):
        """
        Initialize in-memory cache
        
        Args:
            config: LLM configuration
        """
        self.config = config
        
        # LRU cache: OrderedDict maintains insertion order
        # Most recently accessed items are moved to end
        self.cache: OrderedDict[str, CacheEntry] = OrderedDict()
        
        # Calculate max entries based on size limit
        # Assume ~10KB per cached response
        self.max_entries = (config.cache_max_size_mb * 1024 * 1024) // 10240
        
        # Cache statistics
        self.hits = 0
        self.misses = 0
        self.evictions = 0
        self.expirations = 0
        self.total_cost_saved = 0.0
        
        logger.info(
            f"In-memory cache initialized: "
            f"enabled={config.cache_enabled}, "
            f"TTL={config.cache_ttl}s, "
            f"max_entries={self.max_entries}"
        )
    
    async def get(self, key: str) -> Optional[LLMResponse]:
        """
        Get cached response
        
        Args:
            key: Cache key (hash of prompt + model + params)
        
        Returns:
            Cached LLMResponse or None
        """
        if not self.config.cache_enabled:
            return None
        
        # Check if key exists
        if key not in self.cache:
            self.misses += 1
            logger.debug(f"Cache MISS: key={key[:16]}...")
            return None
        
        # Get entry
        entry = self.cache[key]
        
        # Check if expired
        if entry.is_expired():
            # Remove expired entry
            del self.cache[key]
            self.expirations += 1
            self.misses += 1
            logger.debug(f"Cache EXPIRED: key={key[:16]}...")
            return None
        
        # Move to end (mark as recently used)
        self.cache.move_to_end(key)
        
        # Update statistics
        self.hits += 1
        self.total_cost_saved += entry.response.cost_usd
        
        # Mark response as cached
        response = entry.response
        response.cached = True
        
        logger.debug(
            f"Cache HIT: key={key[:16]}..., "
            f"saved=${response.cost_usd:.4f}, "
            f"age={time.time() - entry.created_at:.1f}s"
        )
        
        return response
    
    async def set(self, key: str, response: LLMResponse):
        """
        Store response in cache
        
        Args:
            key: Cache key
            response: LLM response to cache
        """
        if not self.config.cache_enabled:
            return
        
        # Check if we need to evict (LRU)
        if len(self.cache) >= self.max_entries:
            # Remove oldest (least recently used) entry
            oldest_key = next(iter(self.cache))
            del self.cache[oldest_key]
            self.evictions += 1
            logger.debug(f"Cache EVICT (LRU): key={oldest_key[:16]}...")
        
        # Store entry
        entry = CacheEntry(response, self.config.cache_ttl)
        self.cache[key] = entry
        
        logger.debug(
            f"Cache SET: key={key[:16]}..., "
            f"size={len(self.cache)}/{self.max_entries}"
        )
    
    async def delete(self, key: str):
        """
        Delete cached response
        
        Args:
            key: Cache key
        """
        if key in self.cache:
            del self.cache[key]
            logger.debug(f"Cache DELETE: key={key[:16]}...")
    
    async def clear(self):
        """Clear all cached responses"""
        count = len(self.cache)
        self.cache.clear()
        logger.info(f"Cache CLEAR: removed {count} entries")
    
    def _cleanup_expired(self):
        """Remove all expired entries (called periodically)"""
        now = time.time()
        expired_keys = [
            key for key, entry in self.cache.items()
            if entry.is_expired()
        ]
        
        for key in expired_keys:
            del self.cache[key]
            self.expirations += 1
        
        if expired_keys:
            logger.debug(f"Cache cleanup: removed {len(expired_keys)} expired entries")
    
    def get_stats(self) -> dict:
        """
        Get cache statistics
        
        Returns:
            Dictionary with stats
        """
        total_requests = self.hits + self.misses
        hit_rate = (self.hits / total_requests * 100) if total_requests > 0 else 0.0
        
        # Cleanup expired entries before reporting stats
        self._cleanup_expired()
        
        return {
            "enabled": self.config.cache_enabled,
            "hits": self.hits,
            "misses": self.misses,
            "total_requests": total_requests,
            "hit_rate_percentage": hit_rate,
            "evictions": self.evictions,
            "expirations": self.expirations,
            "current_entries": len(self.cache),
            "max_entries": self.max_entries,
            "total_cost_saved_usd": self.total_cost_saved,
            "config": {
                "ttl_seconds": self.config.cache_ttl,
                "max_size_mb": self.config.cache_max_size_mb,
            }
        }
    
    async def close(self):
        """Close cache (cleanup)"""
        stats = self.get_stats()
        logger.info(
            f"Cache closed: "
            f"hits={stats['hits']}, "
            f"misses={stats['misses']}, "
            f"hit_rate={stats['hit_rate_percentage']:.1f}%, "
            f"saved=${stats['total_cost_saved_usd']:.2f}"
        )
        self.cache.clear()


def generate_cache_key(
    messages: list,
    model: str,
    temperature: float = 0.7,
    max_tokens: int = 2000,
    **kwargs
) -> str:
    """
    Generate cache key from request parameters
    
    Args:
        messages: Chat messages
        model: Model name
        temperature: Temperature
        max_tokens: Max tokens
        **kwargs: Additional parameters
    
    Returns:
        Cache key (SHA256 hash)
    """
    # Create deterministic key from parameters
    key_data = {
        "messages": messages,
        "model": model,
        "temperature": temperature,
        "max_tokens": max_tokens,
        # Include other relevant kwargs
        "top_p": kwargs.get("top_p"),
        "frequency_penalty": kwargs.get("frequency_penalty"),
        "presence_penalty": kwargs.get("presence_penalty"),
    }
    
    # Serialize to JSON (sorted keys for consistency)
    key_json = json.dumps(key_data, sort_keys=True)
    
    # Hash to fixed-length key
    return hashlib.sha256(key_json.encode()).hexdigest()


# Alias for backward compatibility
ResponseCache = InMemoryCache
