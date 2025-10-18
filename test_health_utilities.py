#!/usr/bin/env python3
"""
Test health checking and retry utilities.

Tests the basic functionality of utils/health.py helper functions.
"""

import time
import asyncio
from utils.health import rpc_healthy, with_retries, async_with_retries, get_healthy_rpc


def test_rpc_healthy():
    """Test RPC health checking"""
    print("=" * 80)
    print("TEST: rpc_healthy()")
    print("=" * 80)
    
    # Test with a known public RPC (may be slow)
    public_rpc = "https://api.mainnet-beta.solana.com"
    print(f"\nTesting public RPC: {public_rpc}")
    
    is_healthy = rpc_healthy(public_rpc, timeout=5.0)
    print(f"Health check result: {is_healthy}")
    
    # Test with an invalid RPC
    invalid_rpc = "https://invalid-rpc-endpoint-12345.com"
    print(f"\nTesting invalid RPC: {invalid_rpc}")
    
    is_healthy_invalid = rpc_healthy(invalid_rpc, timeout=2.0)
    print(f"Health check result: {is_healthy_invalid}")
    assert is_healthy_invalid is False, "Invalid RPC should return False"
    
    print("\n✅ PASS: rpc_healthy() works correctly")
    return True


def test_with_retries():
    """Test retry wrapper for sync functions"""
    print("\n" + "=" * 80)
    print("TEST: with_retries()")
    print("=" * 80)
    
    # Test successful call
    call_count = [0]
    
    def successful_fn():
        call_count[0] += 1
        return "success"
    
    result = with_retries(successful_fn, attempts=3)
    print(f"\nSuccessful call result: {result}")
    print(f"Call count: {call_count[0]}")
    assert result == "success", "Should return success"
    assert call_count[0] == 1, "Should only call once on success"
    
    # Test retries on failure
    fail_count = [0]
    
    def failing_fn():
        fail_count[0] += 1
        if fail_count[0] < 3:
            raise ValueError(f"Attempt {fail_count[0]} failed")
        return "success after retries"
    
    result = with_retries(failing_fn, attempts=3, base_sleep=0.1)
    print(f"\nRetry result: {result}")
    print(f"Call count: {fail_count[0]}")
    assert result == "success after retries", "Should succeed on third attempt"
    assert fail_count[0] == 3, "Should retry until success"
    
    # Test all attempts fail
    always_fail_count = [0]
    
    def always_fail():
        always_fail_count[0] += 1
        raise RuntimeError(f"Attempt {always_fail_count[0]}")
    
    try:
        with_retries(always_fail, attempts=3, base_sleep=0.1)
        assert False, "Should have raised exception"
    except RuntimeError as e:
        print(f"\nExpected failure after all retries: {e}")
        print(f"Call count: {always_fail_count[0]}")
        assert always_fail_count[0] == 3, "Should try all attempts"
    
    print("\n✅ PASS: with_retries() works correctly")
    return True


async def test_async_with_retries():
    """Test retry wrapper for async functions"""
    print("\n" + "=" * 80)
    print("TEST: async_with_retries()")
    print("=" * 80)
    
    # Test successful async call
    call_count = [0]
    
    async def successful_async_fn():
        call_count[0] += 1
        await asyncio.sleep(0.01)
        return "async success"
    
    result = await async_with_retries(successful_async_fn, attempts=3)
    print(f"\nSuccessful async call result: {result}")
    print(f"Call count: {call_count[0]}")
    assert result == "async success", "Should return success"
    assert call_count[0] == 1, "Should only call once on success"
    
    # Test retries on failure
    fail_count = [0]
    
    async def failing_async_fn():
        fail_count[0] += 1
        await asyncio.sleep(0.01)
        if fail_count[0] < 3:
            raise ValueError(f"Async attempt {fail_count[0]} failed")
        return "async success after retries"
    
    result = await async_with_retries(failing_async_fn, attempts=3, base_sleep=0.1)
    print(f"\nAsync retry result: {result}")
    print(f"Call count: {fail_count[0]}")
    assert result == "async success after retries", "Should succeed on third attempt"
    assert fail_count[0] == 3, "Should retry until success"
    
    # Test all attempts fail
    always_fail_count = [0]
    
    async def always_fail_async():
        always_fail_count[0] += 1
        await asyncio.sleep(0.01)
        raise RuntimeError(f"Async attempt {always_fail_count[0]}")
    
    try:
        await async_with_retries(always_fail_async, attempts=3, base_sleep=0.1)
        assert False, "Should have raised exception"
    except RuntimeError as e:
        print(f"\nExpected async failure after all retries: {e}")
        print(f"Call count: {always_fail_count[0]}")
        assert always_fail_count[0] == 3, "Should try all attempts"
    
    print("\n✅ PASS: async_with_retries() works correctly")
    return True


def test_get_healthy_rpc():
    """Test RPC failover logic"""
    print("\n" + "=" * 80)
    print("TEST: get_healthy_rpc()")
    print("=" * 80)
    
    # Test with both RPCs invalid (should return primary as fallback)
    primary = "https://invalid-primary-12345.com"
    secondary = "https://invalid-secondary-12345.com"
    
    result = get_healthy_rpc(primary, secondary, timeout=1.0)
    print(f"\nBoth invalid - result: {result}")
    assert result == primary, "Should return primary when both invalid"
    
    # Test with no secondary (should return primary)
    result = get_healthy_rpc(primary, None, timeout=1.0)
    print(f"\nNo secondary - result: {result}")
    assert result == primary, "Should return primary when no secondary"
    
    print("\n✅ PASS: get_healthy_rpc() works correctly")
    return True


async def run_async_tests():
    """Run all async tests"""
    await test_async_with_retries()


def main():
    """Run all tests"""
    print("\n" + "=" * 80)
    print("HEALTH CHECK AND RETRY UTILITIES TEST SUITE")
    print("=" * 80)
    
    # Run sync tests
    test_rpc_healthy()
    test_with_retries()
    test_get_healthy_rpc()
    
    # Run async tests
    asyncio.run(run_async_tests())
    
    print("\n" + "=" * 80)
    print("ALL TESTS PASSED ✅")
    print("=" * 80)


if __name__ == "__main__":
    main()
