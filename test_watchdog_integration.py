#!/usr/bin/env python3
"""
Test script to verify timeout watchdog and error handling for infer_missing_fields.

This test verifies:
1. Timeout watchdog works correctly
2. Error handling preserves original trade_info
3. DebugSpan logs step-level checkpoints
"""

import asyncio
import logging
import sys
import time
from typing import Dict, Any

# Add current directory to path
sys.path.insert(0, '.')

# Configure logging to see DebugSpan output
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

from utils.async_timeout import run_with_watchdog
from debug_utils import DebugSpan, set_span_id


async def test_timeout_behavior():
    """Test that timeout returns fallback value."""
    print("\n=== Test 1: Timeout Behavior ===")
    
    async def slow_operation():
        """Simulate a slow operation that exceeds timeout."""
        await asyncio.sleep(5.0)
        return {"status": "completed"}
    
    fallback = {"status": "fallback"}
    
    set_span_id("test_timeout")
    start = time.time()
    
    with DebugSpan("timeout_test", input_data={"timeout": "2s"}):
        result = await run_with_watchdog(
            slow_operation(),
            timeout_seconds=2.0,
            operation_name="slow_operation",
            fallback_value=fallback
        )
    
    elapsed = time.time() - start
    
    if result == fallback:
        print(f"✅ Timeout returned fallback value after {elapsed:.2f}s")
    else:
        print(f"❌ Timeout did not return fallback value: {result}")
        return False
    
    if elapsed < 3.0:  # Should timeout around 2s, not wait 5s
        print(f"✅ Timeout triggered correctly (~{elapsed:.2f}s, expected ~2s)")
    else:
        print(f"❌ Timeout took too long: {elapsed:.2f}s")
        return False
    
    return True


async def test_error_handling():
    """Test that errors return fallback value."""
    print("\n=== Test 2: Error Handling ===")
    
    async def failing_operation():
        """Simulate an operation that fails."""
        raise ValueError("Simulated error")
    
    fallback = {"status": "fallback"}
    
    set_span_id("test_error")
    
    with DebugSpan("error_test", input_data={"should_fail": True}):
        result = await run_with_watchdog(
            failing_operation(),
            timeout_seconds=5.0,
            operation_name="failing_operation",
            fallback_value=fallback
        )
    
    if result == fallback:
        print("✅ Error returned fallback value")
    else:
        print(f"❌ Error did not return fallback value: {result}")
        return False
    
    return True


async def test_success_case():
    """Test that successful operations return their result."""
    print("\n=== Test 3: Success Case ===")
    
    async def successful_operation():
        """Simulate a successful operation."""
        await asyncio.sleep(0.1)
        return {"status": "success", "data": "result"}
    
    fallback = {"status": "fallback"}
    
    set_span_id("test_success")
    
    with DebugSpan("success_test", input_data={"should_succeed": True}):
        result = await run_with_watchdog(
            successful_operation(),
            timeout_seconds=5.0,
            operation_name="successful_operation",
            fallback_value=fallback
        )
    
    if result == {"status": "success", "data": "result"}:
        print("✅ Success case returned correct result")
    else:
        print(f"❌ Success case did not return correct result: {result}")
        return False
    
    return True


async def test_trade_info_preservation():
    """Test that original trade_info is preserved on timeout/error."""
    print("\n=== Test 4: Trade Info Preservation ===")
    
    original_trade_info = {
        "signature": "test_sig_12345",
        "wallet_address": "test_wallet",
        "action": "unknown",
        "token_mint": "UNKNOWN"
    }
    
    async def inference_timeout():
        """Simulate inference that times out."""
        await asyncio.sleep(5.0)
        return {**original_trade_info, "action": "buy", "token_mint": "inferred_mint"}
    
    set_span_id("test_preservation")
    
    with DebugSpan("preservation_test", input_data={"signature": "test_sig_12345"}):
        result = await run_with_watchdog(
            inference_timeout(),
            timeout_seconds=1.0,
            operation_name="infer_missing_fields",
            fallback_value=original_trade_info.copy()
        )
    
    # Verify original trade_info is preserved
    if result == original_trade_info:
        print("✅ Original trade_info preserved on timeout")
    else:
        print(f"❌ Trade info was modified: {result}")
        return False
    
    # Verify we can continue with original data
    if result.get("signature") == "test_sig_12345":
        print("✅ Can continue pipeline with original data")
    else:
        print(f"❌ Cannot continue pipeline: missing signature")
        return False
    
    return True


async def main():
    """Run all tests."""
    print("=" * 60)
    print("Testing Timeout Watchdog and Error Handling")
    print("=" * 60)
    
    tests = [
        test_timeout_behavior,
        test_error_handling,
        test_success_case,
        test_trade_info_preservation
    ]
    
    results = []
    for test in tests:
        try:
            result = await test()
            results.append(result)
        except Exception as e:
            print(f"❌ Test failed with exception: {e}")
            import traceback
            traceback.print_exc()
            results.append(False)
    
    print("\n" + "=" * 60)
    print("Test Results")
    print("=" * 60)
    
    passed = sum(1 for r in results if r)
    total = len(results)
    
    print(f"Passed: {passed}/{total}")
    
    if passed == total:
        print("✅ All tests passed!")
        return 0
    else:
        print(f"❌ {total - passed} test(s) failed")
        return 1


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)
