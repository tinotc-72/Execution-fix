import asyncio
import logging
import aiohttp
import time
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
from config import kz

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class RPCEndpoint:
    url: str
    name: str
    last_success: float = 0.0
    consecutive_failures: int = 0
    current_slot: Optional[int] = None
    latency_ms: float = 0.0
    rate_limit_remaining: Optional[int] = None

class RPCHealthChecker:
    def __init__(self):
        # Initialize with multiple endpoints for redundancy
        self.endpoints: List[RPCEndpoint] = [
            RPCEndpoint(url=kz.HELIUS_RPC_URL, name="Helius"),
            RPCEndpoint(url=kz.PUBLIC_RPC_URL, name="Solana Public")
        ]
        
        # Add QuickNode if configured
        if kz.QUICKNODE_RPC_URL:
            self.endpoints.append(RPCEndpoint(url=kz.QUICKNODE_RPC_URL, name="QuickNode"))
            
        self.session: Optional[aiohttp.ClientSession] = None
        self.last_check_time = 0.0
        self.CHECK_INTERVAL = 5  # seconds between health checks
        self.MAX_CONSECUTIVE_FAILURES = 3  # number of failures before marking endpoint as unhealthy
        
    async def initialize(self):
        """Initialize the aiohttp session with appropriate timeouts"""
        if not self.session:
            timeout = aiohttp.ClientTimeout(total=10, connect=5)
            self.session = aiohttp.ClientSession(timeout=timeout)

    async def close(self):
        """Close the aiohttp session"""
        if self.session:
            await self.session.close()
            self.session = None

    async def check_endpoint_health(self, endpoint: RPCEndpoint) -> bool:
        """Check the health of a single RPC endpoint with improved error handling"""
        if not self.session:
            await self.initialize()

        start_time = time.time()
        try:
            # First try a simple getVersion request as it's lighter than getHealth
            async with self.session.post(
                endpoint.url,
                json={
                    "jsonrpc": "2.0",
                    "id": 1,
                    "method": "getVersion",
                },
                timeout=5.0
            ) as response:
                if response.status != 200:
                    logger.warning(f"{endpoint.name} returned status {response.status}")
                    endpoint.consecutive_failures += 1
                    return False
                    
                result = await response.json()
                if "result" not in result:
                    endpoint.consecutive_failures += 1
                    return False

            # If version check passed, update endpoint stats
            endpoint.latency_ms = (time.time() - start_time) * 1000
            endpoint.last_success = time.time()
            
            # Only reset failures counter if we're below the max
            if endpoint.consecutive_failures < self.MAX_CONSECUTIVE_FAILURES:
                endpoint.consecutive_failures = 0
                
            return True

        except Exception as e:
            logger.warning(f"{endpoint.name} health check error: {str(e)}")
            endpoint.consecutive_failures += 1
            return False

    async def check_all_endpoints(self) -> List[RPCEndpoint]:
        """Check health of all RPC endpoints and return healthy ones"""
        current_time = time.time()
        
        # Only check if enough time has passed since last check
        if current_time - self.last_check_time < self.CHECK_INTERVAL:
            return [e for e in self.endpoints if e.consecutive_failures < self.MAX_CONSECUTIVE_FAILURES]
            
        self.last_check_time = current_time
        
        # Check all endpoints in parallel
        health_checks = [self.check_endpoint_health(endpoint) for endpoint in self.endpoints]
        await asyncio.gather(*health_checks)
        
        # Return endpoints that haven't failed too many times
        healthy_endpoints = [e for e in self.endpoints if e.consecutive_failures < self.MAX_CONSECUTIVE_FAILURES]
        
        if not healthy_endpoints:
            logger.warning("No healthy RPC endpoints found!")
        else:
            logger.info(f"Found {len(healthy_endpoints)} healthy RPC endpoints")
            
        return healthy_endpoints

    def get_best_endpoint(self) -> Optional[RPCEndpoint]:
        """Get the current best endpoint based on last health check"""
        healthy_endpoints = [ep for ep in self.endpoints if ep.consecutive_failures < 3]
        if not healthy_endpoints:
            return None
        return min(healthy_endpoints, key=lambda x: (x.consecutive_failures, x.latency_ms))

    async def get_fallback_endpoints(self) -> List[str]:
        """Get a list of healthy RPC endpoints URLs in priority order"""
        healthy_endpoints = await self.check_all_endpoints()
        return [ep.url for ep in healthy_endpoints]

    def get_health_status(self) -> str:
        """Get a simple health status string"""
        try:
            endpoint = self.get_best_endpoint()
            if endpoint:
                return f"OK ({endpoint.latency_ms:.2f}ms)"
            return "No healthy endpoints"
        except Exception as e:
            return f"Error: {str(e)}"

# Helper function to create a singleton instance
_rpc_health_checker: Optional[RPCHealthChecker] = None

def get_rpc_health_checker() -> RPCHealthChecker:
    global _rpc_health_checker
    if _rpc_health_checker is None:
        _rpc_health_checker = RPCHealthChecker()
    return _rpc_health_checker

async def get_healthy_rpc_endpoint() -> Optional[str]:
    """Utility function to get the best currently healthy RPC endpoint"""
    checker = get_rpc_health_checker()
    healthy_endpoints = await checker.check_all_endpoints()
    return healthy_endpoints[0].url if healthy_endpoints else None
