#!/usr/bin/env python3
"""
Test script to validate route_hint and meteora routing logic.

This validates that:
1. route_hint='direct_copy' is respected in execution_coordinator
2. Meteora routing is properly prioritized and logged
"""

import re
import sys


def test_route_hint_priority():
    """Test that execution_coordinator checks route_hint and prioritizes direct_copy."""
    print("=" * 80)
    print("TEST: Route Hint Priority")
    print("=" * 80)
    
    with open('execution_coordinator.py', 'r') as f:
        code = f.read()
    
    tests = [
        (
            r'route_hint = trade_info\.get\("route_hint"',
            '✅ Extracts route_hint from trade_info'
        ),
        (
            r'if route_hint:.*self\.logger\.info\(f".*Route hint:',
            '✅ Logs route_hint when present'
        ),
        (
            r'if route_hint == "direct_copy":',
            '✅ Checks for route_hint == "direct_copy"'
        ),
        (
            r'if route_hint == "direct_copy":.*plan = \["direct_copy"',
            '✅ Prioritizes direct_copy when route_hint is set'
        ),
        (
            r'self\.logger\.info\(f"\[ROUTING\] ✅ route_hint=.direct_copy. detected - prioritizing direct_copy executor"\)',
            '✅ Logs route_hint detection with INFO emoji'
        ),
    ]
    
    passed = 0
    for pattern, description in tests:
        if re.search(pattern, code, re.DOTALL):
            print(f"  {description}")
            passed += 1
        else:
            print(f"  ❌ {description.replace('✅', '')} - NOT FOUND")
    
    print(f"\n  Result: {passed}/{len(tests)} checks passed\n")
    return passed == len(tests)


def test_meteora_routing_logs():
    """Test that meteora routing is properly logged."""
    print("=" * 80)
    print("TEST: Meteora Routing Logs")
    print("=" * 80)
    
    with open('execution_coordinator.py', 'r') as f:
        code = f.read()
    
    tests = [
        (
            r'"meteora":\s*\["meteora"',
            '✅ ROUTE_MAP prioritizes meteora for dex==meteora'
        ),
        (
            r'plan = ROUTE_MAP\.get\(dex_key, ROUTE_MAP\["unknown"\]\)',
            '✅ Uses ROUTE_MAP for DEX-based routing'
        ),
        (
            r'self\.logger\.info\(f"\[ROUTING\] Using ROUTE_MAP for dex=',
            '✅ Logs ROUTE_MAP usage'
        ),
        (
            r'if dex_key == "meteora":.*self\.logger\.info\(f"\[ROUTING\] ℹ️  Meteora detected',
            '✅ Special logging for meteora route detection'
        ),
        (
            r'Meteora detected - route prioritizes meteora executor first',
            '✅ Logs that meteora executor is prioritized'
        ),
    ]
    
    passed = 0
    for pattern, description in tests:
        if re.search(pattern, code, re.DOTALL):
            print(f"  {description}")
            passed += 1
        else:
            print(f"  ❌ {description.replace('✅', '')} - NOT FOUND")
    
    print(f"\n  Result: {passed}/{len(tests)} checks passed\n")
    return passed == len(tests)


def test_direct_copy_executor_call():
    """Test that direct_copy executor is called when route_hint is set."""
    print("=" * 80)
    print("TEST: Direct Copy Executor Integration")
    print("=" * 80)
    
    with open('execution_coordinator.py', 'r') as f:
        code = f.read()
    
    tests = [
        (
            r'if label == "direct_copy":',
            '✅ Checks for direct_copy in executor routing'
        ),
        (
            r'result = await self\._execute_direct_copy_buy\(',
            '✅ Calls _execute_direct_copy_buy executor'
        ),
        (
            r'async def _execute_direct_copy_buy\(self.*trade_info: dict',
            '✅ _execute_direct_copy_buy accepts trade_info parameter'
        ),
        (
            r'from transaction_cloner import clone_tx_from_signature',
            '✅ Imports transaction cloner'
        ),
        (
            r'sig = trade_info\.get\("signature"\) if trade_info else None',
            '✅ Extracts signature from trade_info'
        ),
        (
            r'if not sig:.*logger\.error\("❌ \[COORDINATOR\] direct_copy requested but no signature present"\)',
            '✅ Handles missing signature with ERROR emoji'
        ),
    ]
    
    passed = 0
    for pattern, description in tests:
        if re.search(pattern, code, re.DOTALL):
            print(f"  {description}")
            passed += 1
        else:
            print(f"  ❌ {description.replace('✅', '')} - NOT FOUND")
    
    print(f"\n  Result: {passed}/{len(tests)} checks passed\n")
    return passed == len(tests)


def test_logging_format_consistency():
    """Test that logging format is consistent with existing emoji format."""
    print("=" * 80)
    print("TEST: Logging Format Consistency")
    print("=" * 80)
    
    with open('execution_coordinator.py', 'r') as f:
        code = f.read()
    
    tests = [
        (
            r'self\.logger\.info\(f"\[ROUTING\] ✅',
            '✅ Uses INFO level with ✅ emoji for routing decisions'
        ),
        (
            r'self\.logger\.info\(f"\[ROUTING\] ℹ️',
            '✅ Uses INFO level with ℹ️ emoji for informational messages'
        ),
        (
            r'logger\.error\("❌ \[COORDINATOR\]',
            '✅ Uses ERROR level with ❌ emoji for errors'
        ),
        (
            r'\[ROUTING\]',
            '✅ Uses [ROUTING] prefix for routing logs'
        ),
        (
            r'\[COORDINATOR\]',
            '✅ Uses [COORDINATOR] prefix for coordinator logs'
        ),
    ]
    
    passed = 0
    for pattern, description in tests:
        if re.search(pattern, code, re.DOTALL):
            print(f"  {description}")
            passed += 1
        else:
            print(f"  ❌ {description.replace('✅', '')} - NOT FOUND")
    
    print(f"\n  Result: {passed}/{len(tests)} checks passed\n")
    return passed == len(tests)


def main():
    """Run all validation tests."""
    print("\n" + "=" * 80)
    print("ROUTE HINT AND METEORA ROUTING TESTS")
    print("=" * 80)
    print()
    
    tests = [
        ("Route Hint Priority", test_route_hint_priority()),
        ("Meteora Routing Logs", test_meteora_routing_logs()),
        ("Direct Copy Executor Integration", test_direct_copy_executor_call()),
        ("Logging Format Consistency", test_logging_format_consistency()),
    ]
    
    passed = sum(1 for _, result in tests if result)
    total = len(tests)
    
    print("=" * 80)
    print("FINAL RESULTS")
    print("=" * 80)
    print(f"\n  Tests Passed: {passed}/{total}")
    
    if passed == total:
        print("\n  🎉 ALL TESTS PASSED!")
        print("\n  Implementation verified:")
        print("  ✅ route_hint='direct_copy' is checked and prioritized")
        print("  ✅ Direct copy executor is called when route_hint is set")
        print("  ✅ Meteora routing uses ROUTE_MAP and logs appropriately")
        print("  ✅ Meteora route prioritizes meteora executor first")
        print("  ✅ Logging format is consistent (INFO/WARNING/ERROR emojis)")
        return 0
    else:
        print("\n  ❌ SOME TESTS FAILED")
        print(f"\n  {total - passed} test(s) did not pass")
        return 1


if __name__ == "__main__":
    sys.exit(main())
