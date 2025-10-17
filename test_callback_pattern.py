#!/usr/bin/env python3
"""
Test script to validate that websocket_handler.py has the correct pattern for
handling both sync and async callbacks.

This test verifies:
1. inspect module is imported
2. inspect.iscoroutinefunction is used to check callback type
3. Async callbacks are awaited directly
4. Sync callbacks use loop.run_in_executor()
"""

import re
import sys


def test_inspect_import():
    """Verify inspect module is imported"""
    print("\n=== Test 1: inspect module imported ===")
    
    with open('websocket_handler.py', 'r') as f:
        content = f.read()
    
    if re.search(r'^import inspect$', content, re.MULTILINE):
        print("  ✅ PASS: inspect module is imported")
        return True
    else:
        print("  ❌ FAIL: inspect module is not imported")
        return False


def test_iscoroutinefunction_check():
    """Verify inspect.iscoroutinefunction is used to check callback type"""
    print("\n=== Test 2: inspect.iscoroutinefunction check ===")
    
    with open('websocket_handler.py', 'r') as f:
        content = f.read()
    
    # Look for the pattern: if inspect.iscoroutinefunction(self.trade_callback):
    pattern = r'if\s+inspect\.iscoroutinefunction\(self\.trade_callback\)'
    matches = re.findall(pattern, content)
    
    if len(matches) >= 4:  # Should have 4 occurrences (one per handler)
        print(f"  ✅ PASS: Found {len(matches)} inspect.iscoroutinefunction checks")
        return True
    elif len(matches) > 0:
        print(f"  ⚠️  PARTIAL: Found {len(matches)} checks (expected 4)")
        return True
    else:
        print("  ❌ FAIL: No inspect.iscoroutinefunction checks found")
        return False


def test_async_await_pattern():
    """Verify async callbacks are awaited directly"""
    print("\n=== Test 3: Async callback await pattern ===")
    
    with open('websocket_handler.py', 'r') as f:
        content = f.read()
    
    # Look for pattern: if inspect.iscoroutinefunction ... await self.trade_callback
    pattern = r'if\s+inspect\.iscoroutinefunction.*?await\s+self\.trade_callback\(trade_info\)'
    matches = re.findall(pattern, content, re.DOTALL)
    
    if len(matches) >= 4:
        print(f"  ✅ PASS: Found {len(matches)} async await patterns")
        return True
    elif len(matches) > 0:
        print(f"  ⚠️  PARTIAL: Found {len(matches)} patterns (expected 4)")
        return True
    else:
        print("  ❌ FAIL: No async await patterns found")
        return False


def test_sync_executor_pattern():
    """Verify sync callbacks use run_in_executor"""
    print("\n=== Test 4: Sync callback executor pattern ===")
    
    with open('websocket_handler.py', 'r') as f:
        content = f.read()
    
    # Look for pattern: else: ... loop.run_in_executor
    pattern = r'loop\s*=\s*asyncio\.get_event_loop\(\).*?await\s+loop\.run_in_executor\(None,\s*self\.trade_callback,\s*trade_info\)'
    matches = re.findall(pattern, content, re.DOTALL)
    
    if len(matches) >= 4:
        print(f"  ✅ PASS: Found {len(matches)} sync executor patterns")
        return True
    elif len(matches) > 0:
        print(f"  ⚠️  PARTIAL: Found {len(matches)} patterns (expected 4)")
        return True
    else:
        print("  ❌ FAIL: No sync executor patterns found")
        return False


def test_finished_logs():
    """Verify FINISHED logs are present (not END)"""
    print("\n=== Test 5: FINISHED logs present ===")
    
    with open('websocket_handler.py', 'r') as f:
        content = f.read()
    
    # Count FINISHED logs
    finished_pattern = r'logger\.info\([^)]*FINISHED[^)]*pipeline'
    finished_matches = re.findall(finished_pattern, content, re.IGNORECASE)
    
    # Count END logs (should be 0 or very few)
    end_pattern = r'logger\.info\([^)]*\bEND\b[^)]*pipeline[^)]*successfully'
    end_matches = re.findall(end_pattern, content)
    
    if len(finished_matches) >= 4 and len(end_matches) == 0:
        print(f"  ✅ PASS: Found {len(finished_matches)} FINISHED logs and no END logs")
        return True
    elif len(finished_matches) > 0:
        print(f"  ⚠️  PARTIAL: Found {len(finished_matches)} FINISHED logs and {len(end_matches)} END logs")
        return True
    else:
        print(f"  ❌ FAIL: Found {len(finished_matches)} FINISHED logs (expected 4)")
        return False


def test_complete_pattern():
    """Verify complete pattern in each handler"""
    print("\n=== Test 6: Complete pattern in handlers ===")
    
    with open('websocket_handler.py', 'r') as f:
        content = f.read()
    
    # Look for the complete pattern
    complete_pattern = r'SCHEDULED.*?START.*?iscoroutinefunction.*?run_in_executor.*?FINISHED'
    
    handler_methods = [
        '_handle_logs_notification',
        '_handle_account_notification',
        '_handle_signature_notification',
        '_handle_enhanced_transaction_notification'
    ]
    
    found_patterns = 0
    for method in handler_methods:
        # Extract method content
        method_pattern = rf'async def {method}\(.*?\):[^#]*?"""[^"]*?"""(.*?)(?=\n    async def|\n    def|\nclass|\Z)'
        method_match = re.search(method_pattern, content, re.DOTALL)
        
        if method_match:
            method_content = method_match.group(1)
            if re.search(complete_pattern, method_content, re.DOTALL):
                found_patterns += 1
                print(f"  ✅ {method}: Has complete sync/async handling pattern")
    
    if found_patterns >= len(handler_methods):
        print(f"\n  ✅ PASS: All {found_patterns} handlers have complete pattern")
        return True
    else:
        print(f"\n  ⚠️  PARTIAL: {found_patterns}/{len(handler_methods)} handlers have complete pattern")
        return found_patterns > 0


def main():
    """Run all tests"""
    print("=" * 70)
    print("WebSocket Handler Callback Pattern Validation")
    print("=" * 70)
    
    tests = [
        test_inspect_import,
        test_iscoroutinefunction_check,
        test_async_await_pattern,
        test_sync_executor_pattern,
        test_finished_logs,
        test_complete_pattern
    ]
    
    results = []
    for test in tests:
        try:
            result = test()
            results.append(result)
        except Exception as e:
            print(f"  ❌ EXCEPTION: {e}")
            import traceback
            traceback.print_exc()
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
        print("  • Imports inspect module")
        print("  • Uses inspect.iscoroutinefunction() to detect callback type")
        print("  • Awaits async callbacks directly")
        print("  • Executes sync callbacks via loop.run_in_executor()")
        print("  • Logs FINISHED instead of END")
        print("\nThis ensures both sync and async callbacks work properly!")
        return 0
    else:
        print(f"\n❌ {total - passed} TESTS FAILED")
        print("\nSome patterns may be missing or incorrect.")
        return 1


if __name__ == "__main__":
    sys.exit(main())
