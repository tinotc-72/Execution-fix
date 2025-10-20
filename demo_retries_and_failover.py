#!/usr/bin/env python3
"""
Demo: Retries, Health Checks, and Endpoint Failover

This demo shows how the new retry and failover mechanisms work:
1. RPC health checking
2. Automatic failover to secondary RPC
3. Retry wrapper for transient failures
"""

import asyncio
from utils.health import rpc_healthy, with_retries, async_with_retries, get_healthy_rpc


def demo_health_checks():
    """Demonstrate RPC health checking"""
    print("=" * 80)
    print("DEMO 1: RPC Health Checks")
    print("=" * 80)
    
    # Test various RPC endpoints
    endpoints = [
        "https://api.mainnet-beta.solana.com",
        "https://invalid-rpc-12345.com",
    ]
    
    for rpc_url in endpoints:
        print(f"\nChecking: {rpc_url}")
        is_healthy = rpc_healthy(rpc_url, timeout=3.0)
        status = "✅ HEALTHY" if is_healthy else "❌ UNHEALTHY"
        print(f"Status: {status}")


def demo_failover():
    """Demonstrate automatic RPC failover"""
    print("\n" + "=" * 80)
    print("DEMO 2: Automatic RPC Failover")
    print("=" * 80)
    
    # Scenario 1: Primary healthy, use primary
    print("\n📍 Scenario 1: Primary healthy")
    primary = "https://api.mainnet-beta.solana.com"
    secondary = "https://api.devnet.solana.com"
    
    selected_rpc = get_healthy_rpc(primary, secondary, timeout=2.0)
    print(f"Selected RPC: {selected_rpc}")
    
    # Scenario 2: Primary unhealthy, failover to secondary
    print("\n📍 Scenario 2: Primary unhealthy, failover to secondary")
    primary = "https://invalid-primary-12345.com"
    secondary = "https://api.mainnet-beta.solana.com"
    
    selected_rpc = get_healthy_rpc(primary, secondary, timeout=2.0)
    print(f"Selected RPC: {selected_rpc}")
    
    # Scenario 3: Both unhealthy, use primary as last resort
    print("\n📍 Scenario 3: Both unhealthy, use primary as fallback")
    primary = "https://invalid-primary-12345.com"
    secondary = "https://invalid-secondary-12345.com"
    
    selected_rpc = get_healthy_rpc(primary, secondary, timeout=1.0)
    print(f"Selected RPC: {selected_rpc}")


def demo_retries():
    """Demonstrate retry mechanism"""
    print("\n" + "=" * 80)
    print("DEMO 3: Retry Mechanism")
    print("=" * 80)
    
    # Scenario 1: Function succeeds immediately
    print("\n📍 Scenario 1: Function succeeds immediately")
    call_count = [0]
    
    def successful_fn():
        call_count[0] += 1
        print(f"  Attempt {call_count[0]}: Success!")
        return "result"
    
    result = with_retries(successful_fn, attempts=3, base_sleep=0.1)
    print(f"Final result: {result}")
    print(f"Total attempts: {call_count[0]}")
    
    # Scenario 2: Function fails twice, succeeds on third attempt
    print("\n📍 Scenario 2: Function fails twice, succeeds on third attempt")
    fail_count = [0]
    
    def retry_then_succeed():
        fail_count[0] += 1
        if fail_count[0] < 3:
            print(f"  Attempt {fail_count[0]}: Failed (transient error)")
            raise RuntimeError("Transient RPC error")
        print(f"  Attempt {fail_count[0]}: Success!")
        return "success after retries"
    
    result = with_retries(retry_then_succeed, attempts=3, base_sleep=0.1)
    print(f"Final result: {result}")
    print(f"Total attempts: {fail_count[0]}")
    
    # Scenario 3: Function fails all attempts
    print("\n📍 Scenario 3: Function fails all attempts")
    always_fail_count = [0]
    
    def always_fail():
        always_fail_count[0] += 1
        print(f"  Attempt {always_fail_count[0]}: Failed")
        raise RuntimeError("Permanent RPC error")
    
    try:
        with_retries(always_fail, attempts=3, base_sleep=0.1)
    except RuntimeError as e:
        print(f"Final exception raised: {e}")
        print(f"Total attempts: {always_fail_count[0]}")


async def demo_async_retries():
    """Demonstrate async retry mechanism"""
    print("\n" + "=" * 80)
    print("DEMO 4: Async Retry Mechanism")
    print("=" * 80)
    
    # Scenario 1: Async function succeeds immediately
    print("\n📍 Scenario 1: Async function succeeds immediately")
    call_count = [0]
    
    async def successful_async_fn():
        call_count[0] += 1
        print(f"  Async attempt {call_count[0]}: Success!")
        await asyncio.sleep(0.01)
        return "async result"
    
    result = await async_with_retries(successful_async_fn, attempts=3, base_sleep=0.1)
    print(f"Final result: {result}")
    print(f"Total attempts: {call_count[0]}")
    
    # Scenario 2: Async function fails twice, succeeds on third attempt
    print("\n📍 Scenario 2: Async function fails twice, succeeds on third attempt")
    fail_count = [0]
    
    async def retry_then_succeed_async():
        fail_count[0] += 1
        await asyncio.sleep(0.01)
        if fail_count[0] < 3:
            print(f"  Async attempt {fail_count[0]}: Failed (transient error)")
            raise RuntimeError("Transient Jito error")
        print(f"  Async attempt {fail_count[0]}: Success!")
        return "async success after retries"
    
    result = await async_with_retries(retry_then_succeed_async, attempts=3, base_sleep=0.1)
    print(f"Final result: {result}")
    print(f"Total attempts: {fail_count[0]}")


def demo_integration():
    """Demonstrate how these utilities are used in the codebase"""
    print("\n" + "=" * 80)
    print("DEMO 5: Integration Examples")
    print("=" * 80)
    
    print("\n📍 Example 1: Jupiter Quote with Retries")
    print("""
    # In mev_jupiter_executor.py, get_best_route() now uses:
    
    def _quote_request():
        response = requests.get(endpoint_url, params=params, headers=headers, timeout=15)
        response.raise_for_status()
        return response.json()
    
    data = with_retries(_quote_request, attempts=3, base_sleep=0.5)
    
    # This wraps the Jupiter quote API call with automatic retries
    """)
    
    print("\n📍 Example 2: Jito Transaction Submission with Retries")
    print("""
    # In jito_service.py, send_transaction() now uses:
    
    async def _send_tx():
        # ... prepare transaction ...
        async with httpx.AsyncClient(timeout=10.0) as client:
            r = await client.post(self.tx_url, headers=self.headers, json=payload)
            r.raise_for_status()
            return r.json()
    
    return await async_with_retries(_send_tx, attempts=3, base_sleep=0.5)
    
    # This wraps Jito submissions with automatic retries
    """)
    
    print("\n📍 Example 3: RPC Failover in Configuration")
    print("""
    # In config.py, you can now use:
    
    from utils.health import get_healthy_rpc
    
    # Select healthy RPC with automatic failover
    rpc_url = get_healthy_rpc(HELIUS_RPC_URL, SECONDARY_RPC_URL)
    
    # This checks primary health and fails over to secondary if needed
    """)


def main():
    """Run all demos"""
    print("\n" + "=" * 80)
    print("RETRIES, HEALTH CHECKS, AND ENDPOINT FAILOVER DEMO")
    print("=" * 80)
    print("\nThis demo shows how transient RPC/Jito issues are handled automatically.\n")
    
    # Run sync demos
    demo_health_checks()
    demo_failover()
    demo_retries()
    demo_integration()
    
    # Run async demos
    asyncio.run(demo_async_retries())
    
    print("\n" + "=" * 80)
    print("DEMO COMPLETE")
    print("=" * 80)
    print("\nKey Takeaways:")
    print("✅ RPC health checks prevent using unhealthy endpoints")
    print("✅ Automatic failover ensures execution continues")
    print("✅ Retries handle transient network/API issues")
    print("✅ Bounded attempts prevent infinite loops")
    print("✅ Exponential backoff reduces server load")
    print("\n")


if __name__ == "__main__":
    main()
