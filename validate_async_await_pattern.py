#!/usr/bin/env python3
"""
Validation script to ensure async/await pattern is correctly implemented
for coordinator handoff.

This script validates that:
1. route_and_execute is an async function
2. route_and_execute properly awaits maybe_execute
3. _handle_websocket_trade properly awaits route_and_execute
4. No synchronous calls to async coordinator functions exist
"""

import re
import sys


def validate_async_await_pattern():
    """Validate the async/await pattern in the codebase"""
    print("=" * 80)
    print("ASYNC/AWAIT PATTERN VALIDATION")
    print("=" * 80)
    print()
    
    # Read main.py
    with open('main.py', 'r') as f:
        main_content = f.read()
    
    # Read execution_coordinator.py
    with open('execution_coordinator.py', 'r') as f:
        coordinator_content = f.read()
    
    all_passed = True
    
    # Test 1: route_and_execute is async
    print("Test 1: route_and_execute is async function")
    if 'async def route_and_execute' in main_content:
        print("  ✅ PASS: route_and_execute is declared as async")
    else:
        print("  ❌ FAIL: route_and_execute is NOT async")
        all_passed = False
    print()
    
    # Test 2: route_and_execute awaits maybe_execute
    print("Test 2: route_and_execute awaits maybe_execute")
    route_func = re.search(
        r'async def route_and_execute.*?(?=\n(?:async def|def|class|\Z))',
        main_content,
        re.DOTALL
    )
    if route_func and 'await maybe_execute' in route_func.group(0):
        print("  ✅ PASS: route_and_execute properly awaits maybe_execute")
    else:
        print("  ❌ FAIL: route_and_execute does NOT await maybe_execute")
        all_passed = False
    print()
    
    # Test 3: maybe_execute is async
    print("Test 3: maybe_execute is async function")
    if 'async def maybe_execute' in coordinator_content:
        print("  ✅ PASS: maybe_execute is declared as async")
    else:
        print("  ❌ FAIL: maybe_execute is NOT async")
        all_passed = False
    print()
    
    # Test 4: _handle_websocket_trade is async
    print("Test 4: _handle_websocket_trade is async function")
    if 'async def _handle_websocket_trade' in main_content:
        print("  ✅ PASS: _handle_websocket_trade is declared as async")
    else:
        print("  ❌ FAIL: _handle_websocket_trade is NOT async")
        all_passed = False
    print()
    
    # Test 5: _handle_websocket_trade awaits route_and_execute
    print("Test 5: _handle_websocket_trade awaits route_and_execute")
    handle_func = re.search(
        r'async def _handle_websocket_trade.*?(?=\n    async def|\n    def|\nclass|\Z)',
        main_content,
        re.DOTALL
    )
    if handle_func and 'await route_and_execute' in handle_func.group(0):
        print("  ✅ PASS: _handle_websocket_trade properly awaits route_and_execute")
    else:
        print("  ❌ FAIL: _handle_websocket_trade does NOT await route_and_execute")
        all_passed = False
    print()
    
    # Test 6: Check for critical warning comment
    print("Test 6: Critical await warning comment exists")
    if '⚠️ CRITICAL: ALWAYS AWAIT coordinator handoff' in main_content:
        print("  ✅ PASS: Critical await warning comment found")
    else:
        print("  ❌ FAIL: Critical await warning comment NOT found")
        all_passed = False
    print()
    
    # Test 7: No synchronous calls to route_and_execute without await
    print("Test 7: No synchronous calls to route_and_execute")
    # Look for route_and_execute( without await before it
    sync_calls = []
    
    # Remove docstrings to avoid false positives
    content_without_docstrings = re.sub(r'""".*?"""', '', main_content, flags=re.DOTALL)
    content_without_docstrings = re.sub(r"'''.*?'''", '', content_without_docstrings, flags=re.DOTALL)
    
    # Find all calls to route_and_execute (not the definition)
    for match in re.finditer(r'\broute_and_execute\(', content_without_docstrings):
        # Skip if this is the function definition
        start = max(0, match.start() - 50)
        before_context = content_without_docstrings[start:match.start()]
        if 'async def ' in before_context or 'def ' in before_context:
            continue  # This is the function definition, skip it
        
        # Check if 'await' is within 20 chars before the call
        await_context = content_without_docstrings[max(0, match.start() - 20):match.start()]
        if 'await' not in await_context:
            sync_calls.append(match.group(0))
    
    if not sync_calls:
        print("  ✅ PASS: No synchronous calls to route_and_execute found")
    else:
        print("  ❌ FAIL: Found potential synchronous calls:")
        for call in sync_calls[:5]:  # Show first 5
            print(f"     - {call.strip()}")
        all_passed = False
    print()
    
    # Test 8: route_and_execute has proper documentation
    print("Test 8: route_and_execute has critical await documentation")
    if route_func:
        func_text = route_func.group(0)
        if 'MUST be called with \'await\'' in func_text or 'ALWAYS AWAIT' in func_text:
            print("  ✅ PASS: route_and_execute has await documentation")
        else:
            print("  ❌ FAIL: route_and_execute missing await documentation")
            all_passed = False
    print()
    
    # Final summary
    print("=" * 80)
    print("VALIDATION SUMMARY")
    print("=" * 80)
    print()
    
    if all_passed:
        print("✅ ALL TESTS PASSED!")
        print()
        print("The async/await pattern is correctly implemented:")
        print("  ✅ route_and_execute is async and awaits maybe_execute")
        print("  ✅ _handle_websocket_trade is async and awaits route_and_execute")
        print("  ✅ Critical await warnings are in place")
        print("  ✅ No synchronous calls to async coordinator functions")
        print()
        print("This ensures:")
        print("  • Coordinator logs appear correctly (🧭 [COORDINATOR] Route=...)")
        print("  • Trade execution happens properly (✅ [EXECUTION] submitted: ...)")
        print("  • Errors are caught and logged")
        print()
        return 0
    else:
        print("❌ VALIDATION FAILED!")
        print()
        print("Some tests failed. Please review the issues above.")
        print()
        return 1


if __name__ == "__main__":
    sys.exit(validate_async_await_pattern())
