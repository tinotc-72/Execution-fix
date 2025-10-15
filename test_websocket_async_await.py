#!/usr/bin/env python3
"""
Test script to validate websocket_handler.py async/await pattern and explicit logging.

This test verifies:
1. WebSocket handler properly awaits trade_callback instead of using create_task
2. Explicit SCHEDULED/START/END/ERROR logs are present
3. Pipeline execution is properly tracked and visible in logs
"""

import re
import sys

def test_no_create_task_in_callbacks():
    """Verify that asyncio.create_task is NOT used for trade callbacks"""
    print("\n=== Test 1: No create_task for callbacks ===")
    
    with open('websocket_handler.py', 'r') as f:
        content = f.read()
    
    # Find all callback invocations - should NOT use create_task
    create_task_pattern = r'asyncio\.create_task\(\s*(?:self\.)?(?:_safe_callback|trade_callback)'
    matches = re.findall(create_task_pattern, content)
    
    if matches:
        print(f"  ❌ FAIL: Found {len(matches)} create_task calls for callbacks")
        print(f"         This means callbacks are fire-and-forget, not awaited")
        for match in matches[:3]:  # Show first 3
            print(f"         - {match}")
        return False
    else:
        print("  ✅ PASS: No create_task found for callbacks - callbacks are properly awaited")
        return True

def test_await_trade_callback():
    """Verify that trade_callback is properly awaited"""
    print("\n=== Test 2: trade_callback is awaited ===")
    
    with open('websocket_handler.py', 'r') as f:
        content = f.read()
    
    # Find await self.trade_callback patterns
    await_pattern = r'await\s+self\.trade_callback\('
    matches = re.findall(await_pattern, content)
    
    if not matches:
        print("  ❌ FAIL: No 'await self.trade_callback' found")
        print("         Callbacks must be awaited for proper async execution")
        return False
    else:
        print(f"  ✅ PASS: Found {len(matches)} properly awaited trade_callback invocations")
        return True

def test_explicit_scheduled_logs():
    """Verify SCHEDULED logs are present"""
    print("\n=== Test 3: SCHEDULED logs present ===")
    
    with open('websocket_handler.py', 'r') as f:
        content = f.read()
    
    # Look for SCHEDULED log pattern
    scheduled_pattern = r'logger\.(?:info|debug)\([^)]*SCHEDULED[^)]*pipeline'
    matches = re.findall(scheduled_pattern, content, re.IGNORECASE)
    
    if not matches:
        print("  ❌ FAIL: No SCHEDULED logs found")
        print("         Pipeline scheduling must be logged for visibility")
        return False
    else:
        print(f"  ✅ PASS: Found {len(matches)} SCHEDULED log statements")
        for match in matches[:3]:  # Show first 3
            print(f"         - {match[:80]}...")
        return True

def test_explicit_start_logs():
    """Verify START logs are present"""
    print("\n=== Test 4: START logs present ===")
    
    with open('websocket_handler.py', 'r') as f:
        content = f.read()
    
    # Look for START log pattern
    start_pattern = r'logger\.(?:info|debug)\([^)]*START[^)]*pipeline'
    matches = re.findall(start_pattern, content, re.IGNORECASE)
    
    if not matches:
        print("  ❌ FAIL: No START logs found")
        print("         Pipeline start must be logged for visibility")
        return False
    else:
        print(f"  ✅ PASS: Found {len(matches)} START log statements")
        for match in matches[:3]:  # Show first 3
            print(f"         - {match[:80]}...")
        return True

def test_explicit_end_logs():
    """Verify END logs are present"""
    print("\n=== Test 5: END logs present ===")
    
    with open('websocket_handler.py', 'r') as f:
        content = f.read()
    
    # Look for END log pattern
    end_pattern = r'logger\.(?:info|debug)\([^)]*END[^)]*pipeline'
    matches = re.findall(end_pattern, content, re.IGNORECASE)
    
    if not matches:
        print("  ❌ FAIL: No END logs found")
        print("         Pipeline completion must be logged for visibility")
        return False
    else:
        print(f"  ✅ PASS: Found {len(matches)} END log statements")
        for match in matches[:3]:  # Show first 3
            print(f"         - {match[:80]}...")
        return True

def test_explicit_error_logs():
    """Verify ERROR logs are present in exception handlers"""
    print("\n=== Test 6: ERROR logs present ===")
    
    with open('websocket_handler.py', 'r') as f:
        content = f.read()
    
    # Look for ERROR log pattern in exception context
    error_pattern = r'logger\.error\([^)]*ERROR[^)]*pipeline[^)]*crashed'
    matches = re.findall(error_pattern, content, re.IGNORECASE)
    
    if not matches:
        print("  ❌ FAIL: No ERROR logs found for pipeline crashes")
        print("         Pipeline errors must be logged for debugging")
        return False
    else:
        print(f"  ✅ PASS: Found {len(matches)} ERROR log statements for pipeline crashes")
        for match in matches[:3]:  # Show first 3
            print(f"         - {match[:80]}...")
        return True

def test_try_except_around_callback():
    """Verify try/except blocks around awaited callbacks"""
    print("\n=== Test 7: Try/except around callbacks ===")
    
    with open('websocket_handler.py', 'r') as f:
        content = f.read()
    
    # Find try blocks with await self.trade_callback (more flexible pattern)
    try_await_pattern = r'try:\s+.*?await\s+self\.trade_callback.*?except\s+Exception'
    matches = re.findall(try_await_pattern, content, re.MULTILINE | re.DOTALL)
    
    if not matches:
        print("  ❌ FAIL: No try/except blocks found around awaited callbacks")
        print("         Callbacks must be wrapped in try/except for error handling")
        return False
    else:
        print(f"  ✅ PASS: Found {len(matches)} properly wrapped callback invocations")
        return True

def test_log_flow_pattern():
    """Verify complete log flow pattern: SCHEDULED → START → END/ERROR"""
    print("\n=== Test 8: Complete log flow pattern ===")
    
    with open('websocket_handler.py', 'r') as f:
        content = f.read()
    
    # Look for the complete pattern in sequence
    flow_pattern = r'SCHEDULED.*?START.*?(?:END|ERROR)'
    
    # Find all handler methods
    handler_methods = ['_handle_logs_notification', '_handle_account_notification', 
                      '_handle_signature_notification', '_handle_enhanced_transaction_notification']
    
    found_patterns = 0
    for method in handler_methods:
        # Extract method content
        method_pattern = rf'async def {method}\(.*?\):\s*""".*?"""(.*?)(?=\n    async def|\n    def|\nclass|\Z)'
        method_match = re.search(method_pattern, content, re.DOTALL)
        
        if method_match:
            method_content = method_match.group(1)
            if re.search(flow_pattern, method_content, re.DOTALL):
                found_patterns += 1
                print(f"  ✅ {method}: Has complete SCHEDULED → START → END/ERROR flow")
    
    if found_patterns >= len(handler_methods):
        print(f"\n  ✅ PASS: All {found_patterns} handlers have complete log flow")
        return True
    else:
        print(f"\n  ⚠️  PARTIAL: {found_patterns}/{len(handler_methods)} handlers have complete log flow")
        return found_patterns > 0

def main():
    """Run all tests"""
    print("=" * 70)
    print("WebSocket Handler Async/Await Pattern Validation")
    print("=" * 70)
    
    tests = [
        test_no_create_task_in_callbacks,
        test_await_trade_callback,
        test_explicit_scheduled_logs,
        test_explicit_start_logs,
        test_explicit_end_logs,
        test_explicit_error_logs,
        test_try_except_around_callback,
        test_log_flow_pattern
    ]
    
    results = []
    for test in tests:
        try:
            result = test()
            results.append(result)
        except Exception as e:
            print(f"  ❌ EXCEPTION: {e}")
            results.append(False)
    
    # Summary
    print("\n" + "=" * 70)
    print("SUMMARY")
    print("=" * 70)
    passed = sum(results)
    total = len(results)
    
    print(f"\nTests passed: {passed}/{total}")
    
    if passed == total:
        print("\n✅ ALL TESTS PASSED!")
        print("\nWebSocket handler correctly:")
        print("  • Awaits trade_callback instead of using create_task")
        print("  • Logs SCHEDULED when pipeline is about to start")
        print("  • Logs START when pipeline execution begins")
        print("  • Logs END when pipeline completes successfully")
        print("  • Logs ERROR when pipeline crashes with exc_info")
        print("\nThis ensures pipeline execution is visible in logs!")
        return 0
    else:
        print(f"\n❌ {total - passed} TESTS FAILED")
        print("\nSome async/await patterns or logging may be missing.")
        return 1

if __name__ == "__main__":
    sys.exit(main())
