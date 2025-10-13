"""
Advanced Rate Limit Manager for Copy Trading Bot
Handles Jupiter API rate limiting and request distribution
"""

import asyncio
import time
from typing import Dict, List, Optional
from collections import defaultdict, deque
import logging

logger = logging.getLogger(__name__)

class RateLimitManager:
    """Smart rate limit manager with multiple strategies"""
    
    def __init__(self):
        # Jupiter API limits: 60 requests per minute
        self.jupiter_requests = deque()  # Track request timestamps
        self.jupiter_limit = 60  # requests per minute
        self.jupiter_window = 60  # seconds
        
        # Request distribution across multiple RPC endpoints
        self.rpc_rotation_index = 0
        self.last_request_times = defaultdict(float)
        
        # Backoff strategy
        self.backoff_multiplier = 1.0
        self.max_backoff = 30.0
        
    def can_make_jupiter_request(self) -> bool:
        """Check if we can make a Jupiter API request"""
        now = time.time()
        
        # Remove requests older than the window
        while self.jupiter_requests and self.jupiter_requests[0] < (now - self.jupiter_window):
            self.jupiter_requests.popleft()
        
        # Check if we're under the limit
        return len(self.jupiter_requests) < (self.jupiter_limit - 5)  # Leave 5 requests buffer
    
    async def wait_for_jupiter_slot(self):
        """Wait until we can make a Jupiter request"""
        while not self.can_make_jupiter_request():
            wait_time = min(2.0 * self.backoff_multiplier, 5.0)
            logger.warning(f"🚦 Jupiter rate limit - waiting {wait_time:.1f}s...")
            await asyncio.sleep(wait_time)
            self.backoff_multiplier = min(self.backoff_multiplier * 1.2, 3.0)
        
        # Reset backoff on successful slot
        self.backoff_multiplier = 1.0
    
    def record_jupiter_request(self):
        """Record a Jupiter API request"""
        self.jupiter_requests.append(time.time())
    
    def get_request_delay(self, service: str = "default") -> float:
        """Get recommended delay before next request"""
        now = time.time()
        last_request = self.last_request_times.get(service, 0)
        time_since_last = now - last_request
        
        # Minimum 100ms between requests to same service
        min_delay = 0.1
        if time_since_last < min_delay:
            return min_delay - time_since_last
        return 0.0
    
    async def throttle_request(self, service: str = "default"):
        """Apply throttling for a service"""
        delay = self.get_request_delay(service)
        if delay > 0:
            await asyncio.sleep(delay)
        
        self.last_request_times[service] = time.time()

# Global instance
rate_limit_manager = RateLimitManager()
