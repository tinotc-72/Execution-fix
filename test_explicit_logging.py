#!/usr/bin/env python3
"""
Test script to validate explicit logging for direct_copy fallback and Meteora routing.

This validates that:
1. validate_trade_info() explicitly logs when route_hint is set to 'direct_copy'
2. execution_coordinator explicitly logs when Meteora route is prioritized
"""

import re
import sys


def test_validate_trade_info_explicit_logging():
    """Test that validate_trade_info explicitly logs route_hint setting."""
    print("=" * 80)
    print("TEST: validate_trade_info() Explicit route_hint Logging")
    print("=" * 80)
    
    with open('trade_processor.py', 'r') as f:
        code = f.read()
    
    tests = [
        (
            r'trade\["route_hint"\] = trade\.get\("route_hint"\) or "direct_copy"',
            '✅ Sets route_hint to "direct_copy" when mint is unresolved'
        ),
        (
            r'logger\.info\(.*route_hint.*direct_copy.*fallback',
            '✅ Explicitly logs that route_hint is set to direct_copy'
        ),
        (
            r'logger\.info\(.*route_hint=.direct_copy.*mint unresolved but signature present',
            '✅ Log message explicitly mentions route_hint setting and reason'
        ),
        (
            r'✅ \[VALIDATION\] route_hint=.direct_copy',
            '✅ Uses ✅ emoji for approval message about route_hint'
        ),
    ]
    
    passed = 0
    for pattern, description in tests:
        if re.search(pattern, code, re.DOTALL | re.IGNORECASE):
            print(f"  {description}")
            passed += 1
        else:
            print(f"  ❌ {description.replace('✅', '')} - NOT FOUND")
            print(f"     Pattern: {pattern}")
    
    print(f"\n  Result: {passed}/{len(tests)} checks passed\n")
    return passed == len(tests)


def test_meteora_explicit_logging():
    """Test that execution_coordinator explicitly logs Meteora route prioritization."""
    print("=" * 80)
    print("TEST: execution_coordinator Meteora Route Prioritization Logging")
    print("=" * 80)
    
    with open('execution_coordinator.py', 'r') as f:
        code = f.read()
    
    tests = [
        (
            r'if dex_key == "meteora":',
            '✅ Checks for dex_key == "meteora"'
        ),
        (
            r'if dex_key == "meteora":.*self\.logger\.info\(f"\[ROUTING\] ℹ️',
            '✅ Logs with INFO level and ℹ️ emoji when Meteora is detected'
        ),
        (
            r'Meteora detected.*route prioritizes meteora executor first',
            '✅ Explicitly states that route prioritizes meteora executor first'
        ),
        (
            r'"meteora":\s*\["meteora"',
            '✅ ROUTE_MAP has meteora executor first for dex==meteora'
        ),
    ]
    
    passed = 0
    for pattern, description in tests:
        if re.search(pattern, code, re.DOTALL):
            print(f"  {description}")
            passed += 1
        else:
            print(f"  ❌ {description.replace('✅', '')} - NOT FOUND")
            print(f"     Pattern: {pattern}")
    
    print(f"\n  Result: {passed}/{len(tests)} checks passed\n")
    return passed == len(tests)


def test_logging_consistency():
    """Test that logging format is consistent with existing format."""
    print("=" * 80)
    print("TEST: Logging Format Consistency")
    print("=" * 80)
    
    # Check trade_processor.py
    with open('trade_processor.py', 'r') as f:
        tp_code = f.read()
    
    # Check execution_coordinator.py
    with open('execution_coordinator.py', 'r') as f:
        ec_code = f.read()
    
    tests = [
        (
            tp_code,
            r'logger\.info\("✅ \[VALIDATION\]',
            '✅ trade_processor uses ✅ emoji for INFO level logs'
        ),
        (
            ec_code,
            r'self\.logger\.info\(f"\[ROUTING\] ℹ️',
            '✅ execution_coordinator uses ℹ️ emoji for INFO level logs'
        ),
        (
            tp_code,
            r'\[VALIDATION\]',
            '✅ trade_processor uses [VALIDATION] prefix'
        ),
        (
            ec_code,
            r'\[ROUTING\]',
            '✅ execution_coordinator uses [ROUTING] prefix'
        ),
    ]
    
    passed = 0
    for code, pattern, description in tests:
        if re.search(pattern, code):
            print(f"  {description}")
            passed += 1
        else:
            print(f"  ❌ {description.replace('✅', '')} - NOT FOUND")
    
    print(f"\n  Result: {passed}/{len(tests)} checks passed\n")
    return passed == len(tests)


def main():
    """Run all validation tests."""
    print("\n" + "=" * 80)
    print("EXPLICIT LOGGING VALIDATION TESTS")
    print("=" * 80)
    print()
    
    tests = [
        ("validate_trade_info() Explicit Logging", test_validate_trade_info_explicit_logging()),
        ("Meteora Explicit Logging", test_meteora_explicit_logging()),
        ("Logging Format Consistency", test_logging_consistency()),
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
        print("  ✅ validate_trade_info() explicitly logs route_hint='direct_copy' setting")
        print("  ✅ execution_coordinator explicitly logs Meteora route prioritization")
        print("  ✅ Logging format is consistent (ℹ️ emoji for INFO messages)")
        print("  ✅ Proper prefixes used ([VALIDATION], [ROUTING])")
        return 0
    else:
        print("\n  ❌ SOME TESTS FAILED")
        print(f"\n  {total - passed} test(s) did not pass")
        return 1


if __name__ == "__main__":
    sys.exit(main())
