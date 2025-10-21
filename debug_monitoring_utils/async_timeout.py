"""
Async timeout watchdog utility for wrapping long-running async operations.

This module provides a run_with_watchdog() utility that wraps async functions
with timeout protection and comprehensive logging.
"""

import asyncio
import logging
from typing import Any, Callable, Optional, TypeVar, Coroutine

logger = logging.getLogger(__name__)

T = TypeVar('T')


async def run_with_watchdog(
    coro: Coroutine[Any, Any, T],
    timeout_seconds: float,
    operation_name: str,
    fallback_value: Optional[T] = None,
    log_timeout: bool = True,
    log_error: bool = True
) -> T:
    """
    Run an async coroutine with a timeout watchdog.
    
    This utility wraps an async operation with timeout protection and logging.
    If the operation times out or fails, it returns the fallback value and logs
    the incident.
    
    Args:
        coro: The coroutine to execute
        timeout_seconds: Maximum time in seconds to wait for completion
        operation_name: Human-readable name for logging
        fallback_value: Value to return on timeout or error (default: None)
        log_timeout: Whether to log timeout events (default: True)
        log_error: Whether to log error events (default: True)
    
    Returns:
        The result of the coroutine if successful, fallback_value on timeout/error
    
    Example:
        ```python
        async def slow_operation(data):
            # ... long-running work ...
            return result
        
        result = await run_with_watchdog(
            slow_operation(data),
            timeout_seconds=5.0,
            operation_name="slow_operation",
            fallback_value=default_data
        )
        ```
    """
    try:
        # Run the coroutine with timeout protection
        result = await asyncio.wait_for(coro, timeout=timeout_seconds)
        return result
    
    except asyncio.TimeoutError:
        # Operation timed out
        if log_timeout:
            logger.warning(
                f"⏱️ [WATCHDOG_TIMEOUT] Operation '{operation_name}' exceeded timeout "
                f"of {timeout_seconds}s - returning fallback value"
            )
        return fallback_value
    
    except Exception as e:
        # Operation failed with an error
        if log_error:
            logger.error(
                f"❌ [WATCHDOG_ERROR] Operation '{operation_name}' failed with error: {e}",
                exc_info=True
            )
        return fallback_value
