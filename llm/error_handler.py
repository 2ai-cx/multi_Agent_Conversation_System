"""
Error Handler

Retry logic with exponential backoff and circuit breaker
"""

import logging
from typing import Callable, Any, Optional
from datetime import datetime, timedelta

from llm.config import LLMConfig

logger = logging.getLogger(__name__)


class CircuitBreakerOpen(Exception):
    """Raised when circuit breaker is open"""
    pass


class CircuitBreaker:
    """
    Circuit breaker pattern implementation
    
    States:
    - CLOSED: Normal operation
    - OPEN: Too many failures, reject requests
    - HALF_OPEN: Testing if service recovered
    """
    
    def __init__(
        self,
        failure_threshold: int = 5,
        recovery_timeout: int = 60
    ):
        """
        Initialize circuit breaker
        
        Args:
            failure_threshold: Number of failures before opening
            recovery_timeout: Seconds before attempting recovery
        """
        self.failure_threshold = failure_threshold
        self.recovery_timeout = recovery_timeout
        
        self.failure_count = 0
        self.last_failure_time: Optional[datetime] = None
        self.state = "CLOSED"  # CLOSED, OPEN, HALF_OPEN
        
        logger.info(
            f"Circuit breaker initialized: "
            f"threshold={failure_threshold}, timeout={recovery_timeout}s"
        )
    
    def record_success(self):
        """Record successful call"""
        self.failure_count = 0
        if self.state == "HALF_OPEN":
            self.state = "CLOSED"
            logger.info("Circuit breaker closed (recovered)")
    
    def record_failure(self):
        """Record failed call"""
        self.failure_count += 1
        self.last_failure_time = datetime.now()
        
        if self.failure_count >= self.failure_threshold:
            self.state = "OPEN"
            logger.warning(
                f"Circuit breaker opened after {self.failure_count} failures"
            )
    
    def can_execute(self) -> bool:
        """Check if request can be executed"""
        if self.state == "CLOSED":
            return True
        
        if self.state == "OPEN":
            # Check if recovery timeout elapsed
            if self.last_failure_time:
                elapsed = (datetime.now() - self.last_failure_time).total_seconds()
                if elapsed >= self.recovery_timeout:
                    self.state = "HALF_OPEN"
                    logger.info("Circuit breaker half-open (testing recovery)")
                    return True
            return False
        
        # HALF_OPEN state
        return True


class ErrorHandler:
    """
    Error handler with retry logic and circuit breaker
    
    Features:
    - Exponential backoff with jitter
    - Circuit breaker pattern
    - Configurable retry attempts
    - Specific exception handling
    """
    
    def __init__(self, config: LLMConfig):
        """
        Initialize error handler
        
        Args:
            config: LLM configuration
        """
        self.config = config
        
        # Initialize circuit breaker if enabled
        self.circuit_breaker = None
        if config.circuit_breaker_enabled:
            self.circuit_breaker = CircuitBreaker(
                failure_threshold=config.circuit_breaker_failure_threshold,
                recovery_timeout=config.circuit_breaker_recovery_timeout
            )
        
        logger.info(
            f"Error handler initialized: "
            f"retry={config.retry_enabled}, "
            f"max_attempts={config.retry_max_attempts}, "
            f"circuit_breaker={config.circuit_breaker_enabled}"
        )
    
    async def execute_with_retry(
        self,
        func: Callable,
        **kwargs
    ) -> Any:
        """
        Execute function with retry logic
        
        Args:
            func: Async function to execute
            **kwargs: Function arguments
        
        Returns:
            Function result
        
        Raises:
            CircuitBreakerOpen: If circuit breaker is open
            Exception: If all retries fail
        """
        # Check circuit breaker
        if self.circuit_breaker and not self.circuit_breaker.can_execute():
            raise CircuitBreakerOpen(
                "Circuit breaker is open. Service temporarily unavailable."
            )
        
        # If retry disabled, just execute once
        if not self.config.retry_enabled:
            return await self._execute_once(func, **kwargs)
        
        # Execute with retry using tenacity
        try:
            from tenacity import (
                retry,
                stop_after_attempt,
                wait_exponential,
                retry_if_exception_type,
                before_sleep_log
            )
            
            # Import httpx for HTTP errors
            import httpx
            
            # Define retry decorator
            retry_decorator = retry(
                stop=stop_after_attempt(self.config.retry_max_attempts),
                wait=wait_exponential(
                    min=self.config.retry_min_wait_seconds,
                    max=self.config.retry_max_wait_seconds
                ),
                retry=retry_if_exception_type((
                    # Retry on these exceptions
                    ConnectionError,
                    TimeoutError,
                    httpx.HTTPStatusError,  # Retry on 429, 503, etc.
                    httpx.ConnectError,
                    httpx.TimeoutException,
                )),
                before_sleep=before_sleep_log(logger, logging.WARNING),
                reraise=True
            )
            
            # Wrap function with retry decorator
            @retry_decorator
            async def _execute():
                return await self._execute_once(func, **kwargs)
            
            # Execute with retry
            result = await _execute()
            
            # Record success in circuit breaker
            if self.circuit_breaker:
                self.circuit_breaker.record_success()
            
            return result
        
        except ImportError:
            logger.warning(
                "Tenacity not installed. Falling back to simple retry logic."
            )
            return await self._simple_retry(func, **kwargs)
        
        except Exception as e:
            # Record failure in circuit breaker
            if self.circuit_breaker:
                self.circuit_breaker.record_failure()
            
            logger.error(f"All retry attempts failed: {e}")
            raise
    
    async def _execute_once(
        self,
        func: Callable,
        **kwargs
    ) -> Any:
        """
        Execute function once
        
        Args:
            func: Function to execute
            **kwargs: Function arguments
        
        Returns:
            Function result
        """
        try:
            result = await func(**kwargs)
            return result
        except Exception as e:
            logger.error(f"Function {func.__name__} failed: {e}")
            raise
    
    async def _simple_retry(
        self,
        func: Callable,
        **kwargs
    ) -> Any:
        """
        Simple retry logic without tenacity
        
        Args:
            func: Function to execute
            **kwargs: Function arguments
        
        Returns:
            Function result
        """
        import asyncio
        
        last_exception = None
        
        for attempt in range(1, self.config.retry_max_attempts + 1):
            try:
                logger.debug(f"Attempt {attempt}/{self.config.retry_max_attempts}")
                result = await self._execute_once(func, **kwargs)
                
                # Success - record in circuit breaker
                if self.circuit_breaker:
                    self.circuit_breaker.record_success()
                
                return result
            
            except Exception as e:
                last_exception = e
                
                if attempt < self.config.retry_max_attempts:
                    # Calculate exponential backoff
                    wait_time = min(
                        self.config.retry_min_wait_seconds * (2 ** (attempt - 1)),
                        self.config.retry_max_wait_seconds
                    )
                    
                    logger.warning(
                        f"Attempt {attempt} failed: {e}. "
                        f"Retrying in {wait_time}s..."
                    )
                    
                    await asyncio.sleep(wait_time)
                else:
                    logger.error(f"All {attempt} attempts failed")
        
        # Record failure in circuit breaker
        if self.circuit_breaker:
            self.circuit_breaker.record_failure()
        
        # All retries failed
        raise last_exception
