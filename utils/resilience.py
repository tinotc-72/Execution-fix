from __future__ import annotations
import time, requests
from typing import Callable, TypeVar, List

T = TypeVar("T")

def retry(attempts: int = 3, base: float = 0.5):
    def deco(fn: Callable[..., T]) -> Callable[..., T]:
        def inner(*args, **kwargs):
            wait = base
            last = None
            for _ in range(attempts):
                try:
                    return fn(*args, **kwargs)
                except Exception as e:
                    last = e
                    time.sleep(min(wait, 2.0)); wait *= 2
            raise last
        return inner
    return deco

def healthy_rpc(rpcs: List[str], timeout: float = 3.0) -> str:
    """
    Select a healthy RPC endpoint from a list.
    
    Tries each endpoint with getHealth check and returns the first healthy one.
    Falls back to the first endpoint if none are healthy.
    
    Args:
        rpcs: List of RPC endpoint URLs
        timeout: Request timeout in seconds (default: 3.0)
        
    Returns:
        URL of first healthy endpoint, or first endpoint as fallback, or empty string if list is empty
    """
    for url in rpcs:
        try:
            r = requests.post(url, json={"jsonrpc":"2.0","id":1,"method":"getHealth","params":[]}, timeout=timeout)
            if r.status_code == 200 and (r.json().get("result") in ("ok", "healthy", None)):
                return url
        except Exception:
            continue
    return rpcs[0] if rpcs else ""  # fallback
