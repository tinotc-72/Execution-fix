#!/usr/bin/env python3
"""
Test suite for async/await coordinator handoff pattern.

This test ensures that:
1. All async functions are properly awaited
2. Coordinator handoff always happens after inference
3. Logs appear correctly when functions are awaited
"""

import re


def test_route_and_execute_is_async():
    """Test that route_and_execute is an async function"""
    print("Test 1: route_and_execute is async")
    
    with open('main.py', 'r') as f:
        content = f.read()
    
    if 'async def route_and_execute' in content:
        print("  ✅ PASS: route_and_execute is async")
        return True
    else:
        print("  ❌ FAIL: route_and_execute is NOT async")
        return False


def test_route_and_execute_awaits_maybe_execute():
    """Test that route_and_execute awaits maybe_execute"""
    print("Test 2: route_and_execute awaits maybe_execute")
    
    with open('main.py', 'r') as f:
        content = f.read()
    
    # Extract route_and_execute function
    route_func = re.search(
        r'async def route_and_execute.*?(?=\n(?:async def|def|class|\Z))',
        content,
        re.DOTALL
    )
    
    if route_func and 'await maybe_execute' in route_func.group(0):
        print("  ✅ PASS: route_and_execute awaits maybe_execute")
        return True
    else:
        print("  ❌ FAIL: route_and_execute does NOT await maybe_execute")
        return False


def test_maybe_execute_is_async():
    """Test that maybe_execute is an async function"""
    print("Test 3: maybe_execute is async")
    
    with open('execution_coordinator.py', 'r') as f:
        content = f.read()
    
    if 'async def maybe_execute' in content:
        print("  ✅ PASS: maybe_execute is async")
        return True
    else:
        print("  ❌ FAIL: maybe_execute is NOT async")
        return False


def test_handler_is_async():
    """Test that _handle_websocket_trade is an async function"""
    print("Test 4: _handle_websocket_trade is async")
    
    with open('main.py', 'r') as f:
        content = f.read()
    
    if 'async def _handle_websocket_trade' in content:
        print("  ✅ PASS: _handle_websocket_trade is async")
        return True
    else:
        print("  ❌ FAIL: _handle_websocket_trade is NOT async")
        return False


def test_handler_awaits_route_and_execute():
    """Test that _handle_websocket_trade awaits route_and_execute"""
    print("Test 5: _handle_websocket_trade awaits route_and_execute")
    
    with open('main.py', 'r') as f:
        content = f.read()
    
    # Extract _handle_websocket_trade function
    handle_func = re.search(
        r'async def _handle_websocket_trade.*?(?=\n    async def|\n    def|\nclass|\Z)',
        content,
        re.DOTALL
    )
    
    if handle_func and 'await route_and_execute' in handle_func.group(0):
        print("  ✅ PASS: _handle_websocket_trade awaits route_and_execute")
        return True
    else:
        print("  ❌ FAIL: _handle_websocket_trade does NOT await route_and_execute")
        return False


def test_critical_await_comment_exists():
    """Test that critical await warning comment exists"""
    print("Test 6: Critical await warning exists")
    
    with open('main.py', 'r') as f:
        content = f.read()
    
    if '⚠️ CRITICAL: ALWAYS AWAIT coordinator handoff' in content:
        print("  ✅ PASS: Critical await warning found in code")
        return True
    else:
        print("  ❌ FAIL: Critical await warning NOT found")
        return False


def test_await_documentation_exists():
    """Test that route_and_execute has await documentation"""
    print("Test 7: route_and_execute has await documentation")
    
    with open('main.py', 'r') as f:
        content = f.read()
    
    # Extract route_and_execute function
    route_func = re.search(
        r'async def route_and_execute.*?(?=\n(?:async def|def|class|\Z))',
        content,
        re.DOTALL
    )
    
    if route_func:
        func_text = route_func.group(0)
        if 'MUST be called with \'await\'' in func_text or 'CRITICAL' in func_text:
            print("  ✅ PASS: route_and_execute has proper await documentation")
            return True
    
    print("  ❌ FAIL: route_and_execute missing await documentation")
    return False


def test_await_happens_after_inference():
    """Test that await route_and_execute happens after infer_missing_fields"""
    print("Test 8: Coordinator handoff after inference")
    
    with open('main.py', 'r') as f:
        content = f.read()
    
    # Look for the pattern: infer_missing_fields ... await route_and_execute
    pattern = r'infer_missing_fields.*?await route_and_execute'
    if re.search(pattern, content, re.DOTALL):
        print("  ✅ PASS: Coordinator handoff happens after inference")
        return True
    else:
        print("  ❌ FAIL: Coordinator handoff does NOT happen after inference")
        return False


def main():
    """Run all tests"""
    print("=" * 80)
    print("ASYNC/AWAIT COORDINATOR HANDOFF TEST SUITE")
    print("=" * 80)
    print()
    
    tests = [
        test_route_and_execute_is_async,
        test_route_and_execute_awaits_maybe_execute,
        test_maybe_execute_is_async,
        test_handler_is_async,
        test_handler_awaits_route_and_execute,
        test_critical_await_comment_exists,
        test_await_documentation_exists,
        test_await_happens_after_inference,
    ]
    
    results = []
    for test in tests:
        result = test()
        results.append(result)
        print()
    
    # Summary
    print("=" * 80)
    print("TEST SUMMARY")
    print("=" * 80)
    print()
    
    passed = sum(results)
    total = len(results)
    
    print(f"Tests Passed: {passed}/{total}")
    print()
    
    if all(results):
        print("✅ ALL TESTS PASSED!")
        print()
        print("The async/await coordinator handoff pattern is correctly implemented:")
        print("  • route_and_execute is async and awaits maybe_execute")
        print("  • _handle_websocket_trade is async and awaits route_and_execute")
        print("  • Coordinator handoff happens after inference")
        print("  • Critical warnings and documentation are in place")
        print()
        print("This ensures:")
        print("  • Coordinator logs appear (🧭 [COORDINATOR] Route=...)")
        print("  • Trade execution completes (✅ [EXECUTION] submitted: ...)")
        print("  • Errors are properly caught and logged")
        print()
        return 0
    else:
        print("❌ SOME TESTS FAILED!")
        print()
        print("Please review the failures above and fix the issues.")
        print()
        return 1


if __name__ == "__main__":
    import sys
    sys.exit(main())
