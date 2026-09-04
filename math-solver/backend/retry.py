"""
Retry logic with exponential backoff for handling transient failures
"""

import asyncio
import logging
from typing import Callable, TypeVar, Optional, Any
import time

logger = logging.getLogger(__name__)

T = TypeVar('T')


class RetryConfig:
    """Configuration for retry behavior"""
    
    def __init__(
        self,
        max_retries: int = 3,
        initial_delay: float = 1.0,
        max_delay: float = 60.0,
        backoff_factor: float = 2.0,
        jitter: bool = True
    ):
        self.max_retries = max_retries
        self.initial_delay = initial_delay
        self.max_delay = max_delay
        self.backoff_factor = backoff_factor
        self.jitter = jitter
    
    def get_delay(self, attempt: int) -> float:
        """Calculate delay for retry attempt"""
        delay = self.initial_delay * (self.backoff_factor ** attempt)
        delay = min(delay, self.max_delay)
        
        if self.jitter:
            # Add random jitter (±10%)
            import random
            jitter_amount = delay * 0.1
            delay += random.uniform(-jitter_amount, jitter_amount)
        
        return max(0, delay)  # Ensure non-negative


class RetryableException(Exception):
    """Exception that indicates the operation should be retried"""
    
    def __init__(self, message: str, original_exception: Optional[Exception] = None):
        self.message = message
        self.original_exception = original_exception
        super().__init__(message)


async def retry_with_backoff(
    func: Callable,
    args: tuple = (),
    kwargs: dict = None,
    config: RetryConfig = None,
    on_retry: Callable = None
) -> Any:
    """
    Execute an async function with retry logic and exponential backoff.
    
    Args:
        func: Async function to execute
        args: Positional arguments for func
        kwargs: Keyword arguments for func
        config: RetryConfig instance (uses default if None)
        on_retry: Callback function called before each retry with (attempt, delay, exception)
    
    Returns:
        Result of func execution
        
    Raises:
        The last exception if all retries are exhausted
    """
    if config is None:
        config = RetryConfig()
    
    if kwargs is None:
        kwargs = {}
    
    last_exception = None
    
    for attempt in range(config.max_retries + 1):
        try:
            logger.debug(f"Executing {func.__name__} (attempt {attempt + 1}/{config.max_retries + 1})")
            result = await func(*args, **kwargs)
            
            if attempt > 0:
                logger.info(f"{func.__name__} succeeded on attempt {attempt + 1}")
            
            return result
            
        except RetryableException as e:
            last_exception = e.original_exception or e
            
            if attempt < config.max_retries:
                delay = config.get_delay(attempt)
                logger.warning(
                    f"{func.__name__} failed (attempt {attempt + 1}/{config.max_retries + 1}): {e.message}. "
                    f"Retrying in {delay:.2f}s..."
                )
                
                if on_retry:
                    on_retry(attempt + 1, delay, last_exception)
                
                await asyncio.sleep(delay)
            else:
                logger.error(f"{func.__name__} failed after {config.max_retries + 1} attempts")
                raise
        
        except Exception as e:
            # Non-retryable exception
            logger.error(f"{func.__name__} failed with non-retryable error: {str(e)}")
            raise
    
    # This shouldn't be reached, but just in case
    if last_exception:
        raise last_exception


def retry_on_exception(
    exception_types: tuple = (Exception,),
    config: RetryConfig = None,
    on_retry: Callable = None
):
    """
    Decorator for retrying async functions on specific exceptions.
    
    Args:
        exception_types: Tuple of exception types to retry on
        config: RetryConfig instance
        on_retry: Callback function
    """
    if config is None:
        config = RetryConfig()
    
    def decorator(func: Callable):
        async def wrapper(*args, **kwargs):
            last_exception = None
            
            for attempt in range(config.max_retries + 1):
                try:
                    return await func(*args, **kwargs)
                
                except exception_types as e:
                    last_exception = e
                    
                    if attempt < config.max_retries:
                        delay = config.get_delay(attempt)
                        logger.warning(
                            f"{func.__name__} failed (attempt {attempt + 1}/{config.max_retries + 1}): {str(e)}. "
                            f"Retrying in {delay:.2f}s..."
                        )
                        
                        if on_retry:
                            on_retry(attempt + 1, delay, e)
                        
                        await asyncio.sleep(delay)
                    else:
                        logger.error(f"{func.__name__} failed after {config.max_retries + 1} attempts")
                        raise
            
            # Fallback (shouldn't reach here)
            if last_exception:
                raise last_exception
        
        return wrapper
    
    return decorator


# Default retry config for API calls
DEFAULT_API_RETRY_CONFIG = RetryConfig(
    max_retries=3,
    initial_delay=1.0,
    max_delay=60.0,
    backoff_factor=2.0,
    jitter=True
)

# More aggressive retry config for critical operations
CRITICAL_RETRY_CONFIG = RetryConfig(
    max_retries=5,
    initial_delay=0.5,
    max_delay=120.0,
    backoff_factor=1.5,
    jitter=True
)

# More conservative retry config for rate-limited operations
RATE_LIMIT_RETRY_CONFIG = RetryConfig(
    max_retries=3,
    initial_delay=2.0,
    max_delay=300.0,
    backoff_factor=2.0,
    jitter=True
)
