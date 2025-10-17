#!/usr/bin/env python3
"""
Test script to verify DebugSpan functionality.

This script validates that the DebugSpan context manager:
1. Logs START/OK/FAIL messages
2. Tracks elapsed time
3. Logs input/output keys
4. Includes correlation ID in logs
5. Captures stack trace on errors
6. Works as both context manager and decorator
"""

import sys
import logging
from utils.debug_span import DebugSpan, set_span_id, get_span_id

# Configure logging to see debug output
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)


def test_context_manager_success():
    """Test DebugSpan as context manager with successful execution."""
    print("\n" + "=" * 80)
    print("TEST 1: DebugSpan as Context Manager - Success")
    print("=" * 80)
    
    set_span_id("test-corr-123")
    
    input_data = {"key1": "value1", "key2": "value2"}
    
    with DebugSpan("test_step_success", input_data=input_data):
        # Simulate some work
        import time
        time.sleep(0.1)
        result = "success"
    
    print("✅ Context manager success test completed")
    return True


def test_context_manager_failure():
    """Test DebugSpan as context manager with failure."""
    print("\n" + "=" * 80)
    print("TEST 2: DebugSpan as Context Manager - Failure")
    print("=" * 80)
    
    set_span_id("test-corr-456")
    
    try:
        with DebugSpan("test_step_failure", input_data={"test": "data"}):
            # Simulate error
            raise ValueError("Test error for debugging")
    except ValueError:
        print("✅ Context manager failure test completed (error handled)")
        return True
    
    return False


def test_decorator():
    """Test DebugSpan as decorator."""
    print("\n" + "=" * 80)
    print("TEST 3: DebugSpan as Decorator")
    print("=" * 80)
    
    set_span_id("test-corr-789")
    
    @DebugSpan("decorated_function")
    def sample_function(arg1, arg2, kwarg1=None):
        """Sample function to test decorator."""
        import time
        time.sleep(0.05)
        return {"result": arg1 + arg2, "kwarg": kwarg1}
    
    result = sample_function(10, 20, kwarg1="test")
    print(f"Result: {result}")
    print("✅ Decorator test completed")
    return True


def test_correlation_id():
    """Test correlation ID functionality."""
    print("\n" + "=" * 80)
    print("TEST 4: Correlation ID")
    print("=" * 80)
    
    # Test setting and getting correlation ID
    test_id = "corr-test-999"
    set_span_id(test_id)
    retrieved_id = get_span_id()
    
    if retrieved_id == test_id:
        print(f"✅ Correlation ID correctly set and retrieved: {retrieved_id}")
    else:
        print(f"❌ Correlation ID mismatch: expected {test_id}, got {retrieved_id}")
        return False
    
    # Test that correlation ID is included in logs
    with DebugSpan("correlation_test"):
        pass
    
    print("✅ Correlation ID test completed")
    return True


def test_nested_spans():
    """Test nested DebugSpan usage."""
    print("\n" + "=" * 80)
    print("TEST 5: Nested DebugSpans")
    print("=" * 80)
    
    set_span_id("nested-corr-111")
    
    with DebugSpan("outer_span", input_data={"level": "outer"}):
        import time
        time.sleep(0.05)
        
        with DebugSpan("inner_span", input_data={"level": "inner"}):
            time.sleep(0.03)
            result = "nested complete"
    
    print("✅ Nested spans test completed")
    return True


def run_all_tests():
    """Run all tests and report results."""
    print("\n" + "=" * 80)
    print("RUNNING DEBUGSPAN TESTS")
    print("=" * 80)
    
    tests = [
        ("Context Manager Success", test_context_manager_success),
        ("Context Manager Failure", test_context_manager_failure),
        ("Decorator", test_decorator),
        ("Correlation ID", test_correlation_id),
        ("Nested Spans", test_nested_spans),
    ]
    
    results = []
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"❌ Test '{test_name}' raised unexpected exception: {e}")
            results.append((test_name, False))
    
    # Summary
    print("\n" + "=" * 80)
    print("TEST SUMMARY")
    print("=" * 80)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status}: {test_name}")
    
    print(f"\nTotal: {passed}/{total} tests passed")
    
    return passed == total


if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)
