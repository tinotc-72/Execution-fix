"""
Health checking and retry utilities for RPC/Jito endpoints.

This module provides:
- rpc_healthy(): Check if an RPC endpoint is responding
- with_retries(): Wrap function calls with exponential backoff retries
- async_with_retries(): Wrap async function calls with exponential backoff retries
- get_healthy_rpc(): Get a healthy RPC URL with automatic failover

Copilot TODO:
1. Wrap outbound RPC calls in `with_retries()` with bounded attempts.
2. Add a simple failover: if `rpc_healthy(primary)` is False, switch to `secondary` from config.
"""

from __future__ import annotations
import time
import asyncio
import logging
from typing import Callable, TypeVar, Awaitable, Optional

import requests

T = TypeVar("T")

logger = logging.getLogger(__name__)

def rpc_healthy(rpc_url: str, timeout: float = 3.0) -> bool:
    """
    Check if an RPC endpoint is healthy by calling getHealth.
    
    Args:
        rpc_url: The RPC endpoint URL to check
        timeout: Request timeout in seconds (default: 3.0)
        
    Returns:
        True if the endpoint is healthy, False otherwise
        
    Example:
        >>> if rpc_healthy("https://api.mainnet-beta.solana.com"):
        ...     print("RPC is healthy")
    """
    try:
        payload = {"jsonrpc": "2.0", "id": 1, "method": "getHealth", "params": []}
        r = requests.post(rpc_url, json=payload, timeout=timeout)
        return r.status_code == 200 and r.json().get("result") in ("ok", "healthy", None)
    except Exception:
        return False

def get_healthy_rpc(primary_rpc: str, secondary_rpc: Optional[str] = None, timeout: float = 3.0) -> str:
    """
    Get a healthy RPC URL with automatic failover.
    
    Copilot TODO: This implements simple failover - if primary RPC is unhealthy, 
    switch to secondary from config.
    
    Args:
        primary_rpc: The primary RPC endpoint URL
        secondary_rpc: The secondary RPC endpoint URL for failover (optional)
        timeout: Health check timeout in seconds (default: 3.0)
        
    Returns:
        The primary RPC if healthy, otherwise the secondary RPC if available and healthy,
        otherwise the primary RPC as a fallback
        
    Example:
        >>> from config import HELIUS_RPC_URL, SECONDARY_RPC_URL
        >>> rpc_url = get_healthy_rpc(HELIUS_RPC_URL, SECONDARY_RPC_URL)
    """
    # Check if primary is healthy
    if rpc_healthy(primary_rpc, timeout=timeout):
        logger.debug(f"[HEALTH] Primary RPC is healthy: {primary_rpc}")
        return primary_rpc
    
    logger.warning(f"[HEALTH] Primary RPC is unhealthy: {primary_rpc}")
    
    # Try secondary if provided
    if secondary_rpc:
        if rpc_healthy(secondary_rpc, timeout=timeout):
            logger.info(f"[HEALTH] ✅ Failing over to secondary RPC: {secondary_rpc}")
            return secondary_rpc
        else:
            logger.error(f"[HEALTH] ❌ Secondary RPC is also unhealthy: {secondary_rpc}")
    
    # Return primary as last resort (let caller handle the error)
    logger.warning(f"[HEALTH] ⚠️  Using primary RPC despite health check failure")
    return primary_rpc

def with_retries(fn: Callable[[], T], attempts: int = 3, base_sleep: float = 0.5) -> T:
    """
    Execute a function with exponential backoff retries.
    
    Args:
        fn: A callable that takes no arguments and returns a value
        attempts: Maximum number of attempts (default: 3)
        base_sleep: Base sleep time in seconds, doubled each retry (default: 0.5)
        
    Returns:
        The return value of fn() if successful
        
    Raises:
        The last exception encountered if all attempts fail
        
    Example:
        >>> result = with_retries(lambda: risky_rpc_call(), attempts=3, base_sleep=0.5)
    """
    last = None
    for i in range(attempts):
        try:
            return fn()
        except Exception as e:
            last = e
            time.sleep(min(base_sleep * (2 ** i), 2.0))
    raise last

async def async_with_retries(fn: Callable[[], Awaitable[T]], attempts: int = 3, base_sleep: float = 0.5) -> T:
    """
    Execute an async function with exponential backoff retries.
    
    Args:
        fn: An async callable that takes no arguments and returns a value
        attempts: Maximum number of attempts (default: 3)
        base_sleep: Base sleep time in seconds, doubled each retry (default: 0.5)
        
    Returns:
        The return value of await fn() if successful
        
    Raises:
        The last exception encountered if all attempts fail
        
    Example:
        >>> result = await async_with_retries(lambda: async_risky_call(), attempts=3, base_sleep=0.5)
    """
    last = None
    for i in range(attempts):
        try:
            return await fn()
        except Exception as e:
            last = e
            await asyncio.sleep(min(base_sleep * (2 ** i), 2.0))
    raise last

