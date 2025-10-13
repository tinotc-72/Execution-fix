import asyncio
import logging
from rpc_health import get_rpc_health_checker, get_healthy_rpc_endpoint

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def test_rpc_health():
    try:
        # Get RPC health checker instance
        health_checker = get_rpc_health_checker()
        
        # Initialize session
        await health_checker.initialize()
        
        try:
            # Test initial health check
            logger.info("\n🔍 Checking RPC endpoints health...")
            healthy_endpoints = await health_checker.check_all_endpoints()
            
            if not healthy_endpoints:
                logger.error("❌ No healthy RPC endpoints found!")
                return
            
            logger.info(f"\n✅ Found {len(healthy_endpoints)} healthy endpoints:")
            for endpoint in healthy_endpoints:
                logger.info(f"""
    Endpoint: {endpoint.name}
    - Latency: {endpoint.latency_ms:.2f}ms
    - Current Slot: {endpoint.current_slot}
    - Rate Limit Remaining: {endpoint.rate_limit_remaining or 'N/A'}
    - Last Success: {endpoint.last_success}
    """)
            
            # Test getting best endpoint
            best_endpoint = health_checker.get_best_endpoint()
            if best_endpoint:
                logger.info(f"\n🏆 Best endpoint: {best_endpoint.name} ({best_endpoint.latency_ms:.2f}ms)")
            
            # Test utility function
            healthy_url = await get_healthy_rpc_endpoint()
            if healthy_url:
                logger.info(f"\n🔗 Healthy RPC URL: {healthy_url}")
            
            # Test fallback functionality
            logger.info("\n📡 Testing fallback endpoints...")
            fallbacks = await health_checker.get_fallback_endpoints()
            logger.info(f"Found {len(fallbacks)} fallback endpoints")
            
        finally:
            # Clean up
            await health_checker.close()
            
    except Exception as e:
        logger.error(f"Error in test_rpc_health: {str(e)}")
        raise

if __name__ == "__main__":
    asyncio.run(test_rpc_health())
