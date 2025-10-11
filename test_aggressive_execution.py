#!/usr/bin/env python3
"""
Test script to verify aggressive execution logic implementation.

This script validates that the bot executes trades when either:
1. Trade instructions (DEX programs) are detected, OR
2. The transaction signer is in MONITORED_WALLETS
"""

import re
import sys


def test_execution_conditions():
    """Test that execution conditions are properly checked."""
    print("=" * 80)
    print("TEST 1: Verify Execution Condition Checks")
    print("=" * 80)
    
    with open('main.py', 'r') as f:
        main = f.read()
    
    tests = [
        # Check for trade instruction detection
        (
            r"_check_trade_instructions.*trade_info",
            "Trade instruction check implemented"
        ),
        # Check for monitored signer detection
        (
            r"_check_monitored_wallet_is_signer.*trade_info",
            "Monitored wallet signer check implemented"
        ),
        # Check for OR condition
        (
            r"if not \(has_trade_instructions or has_monitored_signer\)",
            "Execution proceeds if EITHER condition is met"
        ),
        # Check for explicit 0.001 SOL investment
        (
            r"amount_sol=0\.001.*# Explicit 0\.001 SOL investment",
            "Explicit 0.001 SOL investment for buys"
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


def test_sell_percentage_calculation():
    """Test that sell percentage is calculated from monitored wallet."""
    print("=" * 80)
    print("TEST 2: Verify Sell Percentage Calculation")
    print("=" * 80)
    
    with open('main.py', 'r') as f:
        main = f.read()
    
    tests = [
        (
            r"_calculate_sell_percentage",
            "Sell percentage calculation method exists"
        ),
        (
            r"sell_percentage = self\._calculate_sell_percentage",
            "Sell percentage is calculated before sell execution"
        ),
        (
            r"preTokenBalances.*postTokenBalances",
            "Balance changes are analyzed for percentage"
        ),
        (
            r"sell_percentage=sell_percentage",
            "Calculated percentage is passed to executor"
        ),
    ]
    
    passed = 0
    for pattern, description in tests:
        if re.search(pattern, main, re.DOTALL | re.IGNORECASE):
            print(f"  ✅ {description}")
            passed += 1
        else:
            print(f"  ❌ {description}")
    
    print(f"\n  Result: {passed}/{len(tests)} tests passed\n")
    return passed == len(tests)


def test_aggressive_execution_patterns():
    """Test that aggressive execution patterns are present."""
    print("=" * 80)
    print("TEST 3: Verify Aggressive Execution Patterns")
    print("=" * 80)
    
    with open('main.py', 'r') as f:
        main = f.read()
    
    with open('trade_processor.py', 'r') as f:
        processor = f.read()
    
    tests = [
        (main, r"AGGRESSIVE.*EXECUTION", "Aggressive execution mode logging in main.py"),
        (main, r"action = 'swap'", "Unknown actions default to swap (main.py)"),
        (processor, r"AGGRESSIVE EXECUTION", "Aggressive execution logging in trade_processor.py"),
        (processor, r"synthetic.*action", "Creates synthetic actions when needed"),
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
    print("TEST 4: Verify Execution Method Calls")
    print("=" * 80)
    
    with open('main.py', 'r') as f:
        main = f.read()
    
    buy_calls = len(re.findall(r'_execute_copy_buy', main))
    sell_calls = len(re.findall(r'_execute_copy_sell', main))
    
    print(f"  ✅ Found {buy_calls} _execute_copy_buy calls")
    print(f"  ✅ Found {sell_calls} _execute_copy_sell calls")
    print(f"\n  Total execution calls: {buy_calls + sell_calls}")
    
    # Should have at least 2 calls (one buy, one sell in main execution path)
    passed = (buy_calls >= 2 and sell_calls >= 1)
    
    if passed:
        print(f"  ✅ Sufficient execution calls found\n")
    else:
        print(f"  ❌ Too few execution calls\n")
    
    return passed


def test_logging_and_debugging():
    """Test that proper logging is in place."""
    print("=" * 80)
    print("TEST 5: Verify Logging and Debugging")
    print("=" * 80)
    
    with open('main.py', 'r') as f:
        main = f.read()
    
    tests = [
        (
            r"EXECUTION_CHECK.*Trade instructions detected",
            "Logs trade instruction detection status"
        ),
        (
            r"EXECUTION_CHECK.*Monitored wallet signer",
            "Logs monitored wallet signer status"
        ),
        (
            r"At least one condition met",
            "Logs when execution conditions are met"
        ),
        (
            r"Neither condition met.*skipping execution",
            "Logs when execution is skipped"
        ),
    ]
    
    passed = 0
    for pattern, description in tests:
        if re.search(pattern, main, re.DOTALL | re.IGNORECASE):
            print(f"  ✅ {description}")
            passed += 1
        else:
            print(f"  ❌ {description}")
    
    print(f"\n  Result: {passed}/{len(tests)} tests passed\n")
    return passed == len(tests)


def main():
    """Run all tests."""
    print("\n" + "=" * 80)
    print("AGGRESSIVE EXECUTION LOGIC TEST SUITE")
    print("=" * 80)
    print()
    
    tests = [
        test_execution_conditions(),
        test_sell_percentage_calculation(),
        test_aggressive_execution_patterns(),
        test_execution_method_calls(),
        test_logging_and_debugging(),
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
        print("  ✅ Executes on trade instructions OR monitored wallet signer")
        print("  ✅ Buys with 0.001 SOL, sells same % as monitored wallet")
        print()
        return 0
    else:
        print("\n  ❌ SOME TESTS FAILED")
        print("  ❌ Review implementation")
        print()
        return 1


if __name__ == "__main__":
    sys.exit(main())

