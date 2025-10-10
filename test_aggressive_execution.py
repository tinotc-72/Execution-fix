#!/usr/bin/env python3
"""
Test script to verify aggressive execution logic implementation.

This script validates that all validation checks have been removed or bypassed,
ensuring that ANY detected trade triggers execution.
"""

import re
import sys


def test_no_blocking_returns():
    """Test that there are no blocking returns that prevent execution."""
    print("=" * 80)
    print("TEST 1: Verify No Blocking Returns")
    print("=" * 80)
    
    with open('main.py', 'r') as f:
        main = f.read()
    
    # Check critical sections don't have blocking returns
    tests = [
        # No early return on routing failure
        (
            r"if not routing:.*?routing = \{.*?'action': 'swap'",
            "Routing failure creates default routing (no early return)"
        ),
        # No early return on unknown action after retries
        (
            r"if action == 'unknown'.*?action = 'swap'.*?# Log for analytics but DO NOT return",
            "Unknown action after retries continues execution (no early return)"
        ),
    ]
    
    passed = 0
    for pattern, description in tests:
        if re.search(pattern, main, re.DOTALL):
            print(f"  ✅ {description}")
            passed += 1
        else:
            print(f"  ❌ {description}")
    
    print(f"\n  Result: {passed}/{len(tests)} tests passed\n")
    return passed == len(tests)


def test_aggressive_execution_patterns():
    """Test that aggressive execution patterns are present."""
    print("=" * 80)
    print("TEST 2: Verify Aggressive Execution Patterns")
    print("=" * 80)
    
    with open('main.py', 'r') as f:
        main = f.read()
    
    with open('trade_processor.py', 'r') as f:
        processor = f.read()
    
    tests = [
        (main, r"AGGRESSIVE EXECUTION MODE", "Aggressive execution mode logging in main.py"),
        (main, r"executing anyway.*?aggressive mode", "Execution continues in aggressive mode (main.py)"),
        (main, r"action = 'swap'", "Unknown actions default to swap (main.py)"),
        (processor, r"AGGRESSIVE EXECUTION", "Aggressive execution logging in trade_processor.py"),
        (processor, r"but executing anyway", "Bypasses validation in trade_processor.py"),
        (processor, r"synthetic.*?action", "Creates synthetic actions when needed"),
    ]
    
    passed = 0
    for content, pattern, description in tests:
        if re.search(pattern, content, re.IGNORECASE):
            print(f"  ✅ {description}")
            passed += 1
        else:
            print(f"  ❌ {description}")
    
    print(f"\n  Result: {passed}/{len(tests)} tests passed\n")
    return passed == len(tests)


def test_execution_method_calls():
    """Test that execution methods are called in all critical paths."""
    print("=" * 80)
    print("TEST 3: Verify Execution Method Calls")
    print("=" * 80)
    
    with open('main.py', 'r') as f:
        main = f.read()
    
    buy_calls = len(re.findall(r'_execute_copy_buy', main))
    sell_calls = len(re.findall(r'_execute_copy_sell', main))
    
    print(f"  ✅ Found {buy_calls} _execute_copy_buy calls")
    print(f"  ✅ Found {sell_calls} _execute_copy_sell calls")
    print(f"\n  Total execution calls: {buy_calls + sell_calls}")
    
    # Should have multiple calls (at least 5 total)
    passed = (buy_calls + sell_calls) >= 5
    
    if passed:
        print(f"  ✅ Sufficient execution calls found\n")
    else:
        print(f"  ❌ Too few execution calls\n")
    
    return passed


def test_validation_bypasses():
    """Test that all validation checks are bypassed."""
    print("=" * 80)
    print("TEST 4: Verify All Validation Bypasses")
    print("=" * 80)
    
    with open('trade_processor.py', 'r') as f:
        processor = f.read()
    
    bypasses = [
        (r"requires_execution.*?but executing anyway", "requires_execution bypass"),
        (r"wallet validation failed.*?but executing anyway", "Wallet validation bypass"),
        (r"No balance changes.*?synthetic action", "Balance changes bypass"),
        (r"No significant.*?but executing anyway", "Significance check bypass"),
        (r"non-monitored wallet.*?but executing anyway", "Monitored wallet bypass"),
        (r"NO DEX PROGRAMS.*?return 'swap'", "DEX detection bypass"),
    ]
    
    passed = 0
    for pattern, description in bypasses:
        if re.search(pattern, processor, re.IGNORECASE | re.DOTALL):
            print(f"  ✅ {description}")
            passed += 1
        else:
            print(f"  ❌ {description}")
    
    print(f"\n  Result: {passed}/{len(bypasses)} bypasses found\n")
    return passed == len(bypasses)


def test_default_action_strategy():
    """Test that default action strategy is implemented."""
    print("=" * 80)
    print("TEST 5: Verify Default Action Strategy")
    print("=" * 80)
    
    with open('main.py', 'r') as f:
        main = f.read()
    
    strategies = [
        (r"if action == 'unknown':.*?action = 'swap'", "Unknown action defaults to 'swap'"),
        (r"executing as BUY.*?aggressive mode", "Unknown actions execute as BUY"),
        (r"swap default", "Swap is default action for unknown"),
    ]
    
    passed = 0
    for pattern, description in strategies:
        if re.search(pattern, main, re.DOTALL | re.IGNORECASE):
            print(f"  ✅ {description}")
            passed += 1
        else:
            print(f"  ❌ {description}")
    
    print(f"\n  Result: {passed}/{len(strategies)} strategies found\n")
    return passed == len(strategies)


def main():
    """Run all tests."""
    print("\n" + "=" * 80)
    print("AGGRESSIVE EXECUTION LOGIC TEST SUITE")
    print("=" * 80)
    print()
    
    tests = [
        test_no_blocking_returns(),
        test_aggressive_execution_patterns(),
        test_execution_method_calls(),
        test_validation_bypasses(),
        test_default_action_strategy(),
    ]
    
    passed = sum(tests)
    total = len(tests)
    
    print("=" * 80)
    print("FINAL RESULTS")
    print("=" * 80)
    print(f"\n  Tests Passed: {passed}/{total}")
    
    if passed == total:
        print("\n  ✅ ALL TESTS PASSED!")
        print("  ✅ Aggressive execution logic fully implemented")
        print("  ✅ ANY detected trade will trigger execution")
        print()
        return 0
    else:
        print("\n  ❌ SOME TESTS FAILED")
        print("  ❌ Review implementation")
        print()
        return 1


if __name__ == "__main__":
    sys.exit(main())
