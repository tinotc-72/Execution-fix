#!/usr/bin/env python3
"""
Rate Limiter - Handle RPC rate limiting and retries
"""

import asyncio
import logging
import time
from typing import Callable, Any, Dict

logger = logging.getLogger(__name__)

class RateLimiter:
    """Handle rate limiting for RPC calls"""
    
    def __init__(self, calls_per_second: float = 10):
        self.calls_per_second = calls_per_second
        self.min_interval = 1.0 / calls_per_second
        self.last_call_time = 0
    
    async def wait_if_needed(self):
        """Wait if we need to respect rate limit"""
        current_time = time.time()
        time_since_last_call = current_time - self.last_call_time
        
        if time_since_last_call < self.min_interval:
            wait_time = self.min_interval - time_since_last_call
            await asyncio.sleep(wait_time)
        
        self.last_call_time = time.time()

class RetryHandler:
    """Handle retries with exponential backoff"""
    
    @staticmethod
    async def retry_with_backoff(
        func: Callable,
        max_retries: int = 3,
        base_delay: float = 1.0,
        max_delay: float = 30.0,
        backoff_factor: float = 2.0
    ) -> Any:
        """Retry function with exponential backoff"""
        
        for attempt in range(max_retries + 1):
            try:
                return await func()
            except Exception as e:
                if attempt == max_retries:
                    logger.error(f"❌ All {max_retries + 1} attempts failed: {e}")
                    raise
                
                # Check if it's a rate limit error
                if "429" in str(e) or "Too Many Requests" in str(e):
                    delay = min(base_delay * (backoff_factor ** attempt), max_delay)
                    logger.warning(f"⚠️  Rate limited, retrying in {delay:.1f}s (attempt {attempt + 1}/{max_retries + 1})")
                    await asyncio.sleep(delay)
                    continue
                
                # For other errors, shorter delay
                if attempt < max_retries:
                    delay = min(base_delay * (backoff_factor ** attempt) * 0.5, max_delay * 0.5)
                    logger.warning(f"⚠️  Error occurred, retrying in {delay:.1f}s: {e}")
                    await asyncio.sleep(delay)
                else:
                    raise

# Global rate limiter instances
RPC_RATE_LIMITER = RateLimiter(calls_per_second=8)  # Conservative rate limit
JUPITER_RATE_LIMITER = RateLimiter(calls_per_second=5)  # Even more conservative for Jupiter
