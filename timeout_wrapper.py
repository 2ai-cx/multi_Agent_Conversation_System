#!/usr/bin/env python3
"""
Timeout Wrapper System for API Calls
Prevents hanging processes when external services don't respond
"""

import asyncio
import functools
import logging
import time
from typing import Any, Callable, Dict, Optional, Union
from contextlib import asynccontextmanager

# Conditional imports to handle Temporal workflow sandbox restrictions
try:
    import requests
    from requests.adapters import HTTPAdapter
    from urllib3.util.retry import Retry
    REQUESTS_AVAILABLE = True
except ImportError:
    # In Temporal workflow sandbox, these imports may be restricted
    REQUESTS_AVAILABLE = False
    requests = None
    HTTPAdapter = None
    Retry = None

logger = logging.getLogger(__name__)

class TimeoutError(Exception):
    """Custom timeout exception"""
    pass

class APITimeoutConfig:
    """Configuration for API timeouts"""
    
    # Default timeouts (in seconds)
    DEFAULT_TIMEOUT = 30
    HARVEST_MCP_TIMEOUT = 45
    SUPABASE_TIMEOUT = 20
    TWILIO_TIMEOUT = 15
    OPENAI_TIMEOUT = 60
    EMAIL_TIMEOUT = 30
    
    # Retry configuration
    MAX_RETRIES = 3
    BACKOFF_FACTOR = 0.3
    RETRY_STATUS_CODES = [500, 502, 503, 504, 429]

def timeout_wrapper(timeout_seconds: Optional[int] = None, 
                   service_name: str = "API",
                   retry_attempts: int = 1,
                   fallback_value: Any = None):
    """
    Decorator to add timeout protection to any function
    
    Args:
        timeout_seconds: Timeout in seconds (uses default if None)
        service_name: Name of service for logging
        retry_attempts: Number of retry attempts
        fallback_value: Value to return on timeout/failure
    """
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        async def async_wrapper(*args, **kwargs):
            timeout = timeout_seconds or APITimeoutConfig.DEFAULT_TIMEOUT
            
            for attempt in range(retry_attempts):
                try:
                    start_time = time.time()
                    
                    # Execute with timeout
                    result = await asyncio.wait_for(
                        func(*args, **kwargs),
                        timeout=timeout
                    )
                    
                    elapsed = time.time() - start_time
                    logger.info(f"✅ {service_name} call completed in {elapsed:.2f}s (attempt {attempt + 1})")
                    return result
                    
                except asyncio.TimeoutError:
                    elapsed = time.time() - start_time
                    logger.warning(f"⏰ {service_name} timeout after {elapsed:.2f}s (attempt {attempt + 1}/{retry_attempts})")
                    
                    if attempt == retry_attempts - 1:
                        logger.error(f"❌ {service_name} failed after {retry_attempts} attempts")
                        if fallback_value is not None:
                            return fallback_value
                        raise TimeoutError(f"{service_name} timeout after {timeout}s")
                    
                    # Exponential backoff
                    await asyncio.sleep(APITimeoutConfig.BACKOFF_FACTOR * (2 ** attempt))
                    
                except Exception as e:
                    logger.error(f"❌ {service_name} error (attempt {attempt + 1}): {e}")
                    if attempt == retry_attempts - 1:
                        if fallback_value is not None:
                            return fallback_value
                        raise
                    await asyncio.sleep(APITimeoutConfig.BACKOFF_FACTOR * (2 ** attempt))
        
        @functools.wraps(func)
        def sync_wrapper(*args, **kwargs):
            timeout = timeout_seconds or APITimeoutConfig.DEFAULT_TIMEOUT
            
            for attempt in range(retry_attempts):
                try:
                    start_time = time.time()
                    
                    # For sync functions, we can't use asyncio.wait_for
                    # Instead, we'll rely on the underlying library's timeout
                    result = func(*args, **kwargs)
                    
                    elapsed = time.time() - start_time
                    logger.info(f"✅ {service_name} call completed in {elapsed:.2f}s (attempt {attempt + 1})")
                    return result
                    
                except Exception as e:
                    # Handle timeout exceptions (requests may not be available in Temporal sandbox)
                    if REQUESTS_AVAILABLE and hasattr(requests, 'exceptions'):
                        if isinstance(e, (requests.exceptions.Timeout, requests.exceptions.ConnectTimeout, 
                                        requests.exceptions.ReadTimeout)):
                            pass  # This is a timeout exception
                    # Handle any timeout-like exception
                    elapsed = time.time() - start_time
                    logger.warning(f"⏰ {service_name} timeout after {elapsed:.2f}s (attempt {attempt + 1}/{retry_attempts})")
                    
                    if attempt == retry_attempts - 1:
                        logger.error(f"❌ {service_name} failed after {retry_attempts} attempts")
                        if fallback_value is not None:
                            return fallback_value
                        raise TimeoutError(f"{service_name} timeout after {timeout}s")
                    
                    time.sleep(APITimeoutConfig.BACKOFF_FACTOR * (2 ** attempt))
                    
                except Exception as e:
                    logger.error(f"❌ {service_name} error (attempt {attempt + 1}): {e}")
                    if attempt == retry_attempts - 1:
                        if fallback_value is not None:
                            return fallback_value
                        raise
                    time.sleep(APITimeoutConfig.BACKOFF_FACTOR * (2 ** attempt))
        
        # Return appropriate wrapper based on function type
        if asyncio.iscoroutinefunction(func):
            return async_wrapper
        else:
            return sync_wrapper
    
    return decorator

def create_requests_session(timeout: int = APITimeoutConfig.DEFAULT_TIMEOUT):
    """
    Create a requests session with timeout and retry configuration
    
    Args:
        timeout: Request timeout in seconds
        
    Returns:
        Configured requests session or None if requests not available
    """
    if not REQUESTS_AVAILABLE:
        logger.warning("⚠️ Requests library not available (Temporal sandbox restriction)")
        return None
        
    session = requests.Session()
    
    # Configure retry strategy
    retry_strategy = None
    if Retry:
        retry_strategy = Retry(
            total=APITimeoutConfig.MAX_RETRIES,
            backoff_factor=APITimeoutConfig.BACKOFF_FACTOR,
            status_forcelist=APITimeoutConfig.RETRY_STATUS_CODES,
            allowed_methods=["HEAD", "GET", "PUT", "DELETE", "OPTIONS", "TRACE", "POST"]
        )
    
    # Mount adapter with retry strategy
    if HTTPAdapter:
        adapter = HTTPAdapter(max_retries=retry_strategy)
        session.mount("http://", adapter)
        session.mount("https://", adapter)
    
    # Set default timeout
    session.timeout = timeout
    
    return session

@asynccontextmanager
async def timeout_context(timeout_seconds: int, service_name: str = "Operation"):
    """
    Async context manager for timeout protection
    
    Usage:
        async with timeout_context(30, "Database Query"):
            result = await some_long_operation()
    """
    start_time = time.time()
    try:
        async with asyncio.timeout(timeout_seconds):
            yield
        elapsed = time.time() - start_time
        logger.info(f"✅ {service_name} completed in {elapsed:.2f}s")
    except asyncio.TimeoutError:
        elapsed = time.time() - start_time
        logger.error(f"⏰ {service_name} timeout after {elapsed:.2f}s")
        raise TimeoutError(f"{service_name} timeout after {timeout_seconds}s")

# Specialized timeout decorators for different services
def harvest_timeout(func: Callable) -> Callable:
    """Timeout wrapper specifically for Harvest MCP calls"""
    return timeout_wrapper(
        timeout_seconds=APITimeoutConfig.HARVEST_MCP_TIMEOUT,
        service_name="Harvest MCP",
        retry_attempts=2,
        fallback_value={"error": "Harvest service timeout", "total_hours": 0, "entries": []}
    )(func)

def supabase_timeout(func: Callable) -> Callable:
    """Timeout wrapper specifically for Supabase calls"""
    return timeout_wrapper(
        timeout_seconds=APITimeoutConfig.SUPABASE_TIMEOUT,
        service_name="Supabase",
        retry_attempts=2,
        fallback_value=[]
    )(func)

def twilio_timeout(func: Callable) -> Callable:
    """Timeout wrapper specifically for Twilio calls"""
    return timeout_wrapper(
        timeout_seconds=APITimeoutConfig.TWILIO_TIMEOUT,
        service_name="Twilio",
        retry_attempts=2,
        fallback_value={"status": "error", "error": "SMS service timeout"}
    )(func)

def openai_timeout(func: Callable) -> Callable:
    """Timeout wrapper specifically for OpenAI calls"""
    return timeout_wrapper(
        timeout_seconds=APITimeoutConfig.OPENAI_TIMEOUT,
        service_name="OpenAI",
        retry_attempts=2,
        fallback_value="I apologize, but I'm experiencing technical difficulties. Please try again."
    )(func)

def email_timeout(func: Callable) -> Callable:
    """Timeout wrapper specifically for email operations"""
    return timeout_wrapper(
        timeout_seconds=APITimeoutConfig.EMAIL_TIMEOUT,
        service_name="Email Service",
        retry_attempts=2,
        fallback_value={"status": "error", "error": "Email service timeout"}
    )(func)

# Circuit breaker pattern for repeated failures
class CircuitBreaker:
    """Simple circuit breaker to prevent cascading failures"""
    
    def __init__(self, failure_threshold: int = 5, recovery_timeout: int = 60):
        self.failure_threshold = failure_threshold
        self.recovery_timeout = recovery_timeout
        self.failure_count = 0
        self.last_failure_time = None
        self.state = "CLOSED"  # CLOSED, OPEN, HALF_OPEN
    
    def call(self, func: Callable, *args, **kwargs):
        """Execute function with circuit breaker protection"""
        if self.state == "OPEN":
            if time.time() - self.last_failure_time > self.recovery_timeout:
                self.state = "HALF_OPEN"
                logger.info("🔄 Circuit breaker transitioning to HALF_OPEN")
            else:
                raise Exception("Circuit breaker is OPEN - service unavailable")
        
        try:
            result = func(*args, **kwargs)
            if self.state == "HALF_OPEN":
                self.state = "CLOSED"
                self.failure_count = 0
                logger.info("✅ Circuit breaker reset to CLOSED")
            return result
        except Exception as e:
            self.failure_count += 1
            self.last_failure_time = time.time()
            
            if self.failure_count >= self.failure_threshold:
                self.state = "OPEN"
                logger.error(f"🚨 Circuit breaker OPEN after {self.failure_count} failures")
            
            raise

# Global circuit breakers for different services
harvest_circuit_breaker = CircuitBreaker(failure_threshold=3, recovery_timeout=300)  # 5 minutes
supabase_circuit_breaker = CircuitBreaker(failure_threshold=5, recovery_timeout=60)   # 1 minute
twilio_circuit_breaker = CircuitBreaker(failure_threshold=3, recovery_timeout=120)    # 2 minutes
