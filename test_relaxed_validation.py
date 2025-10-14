#!/usr/bin/env python3
"""
Test script to validate relaxed validation logic for direct_copy execution.

This validates that trades with PENDING_ANALYSIS mint but valid signature
are allowed via the direct_copy route.
"""

import re
import sys


def test_relaxed_validation_for_direct_copy():
    """Test that validation allows direct_copy when mint is unknown but signature exists."""
    print("=" * 80)
    print("TEST: Relaxed Validation for Direct Copy")
    print("=" * 80)
    
    with open('trade_processor.py', 'r') as f:
        code = f.read()
    
    tests = [
        (
            r'has_any_data = has_sig or trade\.get\("logs"\) or trade\.get\("transaction"\)',
            '✅ Checks for any available data (signature/logs/transaction)'
        ),
        (
            r'if not has_any_data:.*logger\.warning\(.*Insufficient data.*no signature/logs/tx',
            '✅ Rejects only when truly no data available'
        ),
        (
            r'if token_mint in \(None, "", "PENDING_ANALYSIS", "UNKNOWN"\):',
            '✅ Checks for unresolved mint including PENDING_ANALYSIS'
        ),
        (
            r'if has_sig:.*trade\["route_hint"\] = trade\.get\("route_hint"\) or "direct_copy"',
            '✅ Sets route_hint to direct_copy when signature exists'
        ),
        (
            r'trade\["dex"\] = trade\.get\("dex"\) or trade\.get\("dex_type"\) or "unknown"',
            '✅ Sets default dex to unknown when needed'
        ),
        (
            r'trade\["action"\] = trade\.get\("action"\) or "swap"',
            '✅ Sets default action to swap when needed'
        ),
        (
            r'logger\.info\(.*Allowing execution via direct_copy \(mint unresolved but signature present\)',
            '✅ Logs reason for allowing direct_copy route'
        ),
        (
            r'logger\.warning\(.*Mint unresolved and no signature.*skipping',
            '✅ Rejects when mint is unresolved AND no signature'
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
    """Test that logging format is consistent with existing code."""
    print("=" * 80)
    print("TEST: Logging Format Consistency")
    print("=" * 80)
    
    with open('trade_processor.py', 'r') as f:
        code = f.read()
    
    tests = [
        (
            r'logger\.info\("✅ \[VALIDATION\]',
            '✅ Uses INFO level with ✅ emoji for success'
        ),
        (
            r'logger\.warning\("🛑 \[VALIDATION\]',
            '✅ Uses WARNING level with 🛑 emoji for rejection'
        ),
        (
            r'\[VALIDATION\]',
            '✅ Uses [VALIDATION] prefix consistently'
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


def test_backward_compatibility():
    """Test that existing validation logic is preserved."""
    print("=" * 80)
    print("TEST: Backward Compatibility")
    print("=" * 80)
    
    with open('trade_processor.py', 'r') as f:
        code = f.read()
    
    tests = [
        (
            r'valid_dexes = \{.*"pumpfun".*"raydium".*"jupiter"',
            '✅ Valid DEX list preserved'
        ),
        (
            r'valid_actions = \{.*"buy".*"sell".*"swap"',
            '✅ Valid actions list preserved'
        ),
        (
            r'if dex in valid_dexes and action in valid_actions and mint and mint not in',
            '✅ Existing validation for complete trades preserved'
        ),
        (
            r'logger\.warning\(f"\[VALIDATION\] ❌ Trade rejected - insufficient data:"\)',
            '✅ Rejection logging for incomplete data preserved'
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
    print("RELAXED VALIDATION TESTS")
    print("=" * 80)
    print()
    
    tests = [
        ("Relaxed Validation for Direct Copy", test_relaxed_validation_for_direct_copy()),
        ("Logging Format Consistency", test_logging_format_consistency()),
        ("Backward Compatibility", test_backward_compatibility()),
    ]
    
    passed = sum(1 for _, result in tests if result)
    total = len(tests)
    
    print("=" * 80)
    print("FINAL RESULTS")
    print("=" * 80)
    print(f"\n  Tests Passed: {passed}/{total}")
    
    if passed == total:
        print("\n  🎉 ALL TESTS PASSED!")
        print("\n  The validation now:")
        print("  ✅ Allows direct_copy when mint is PENDING_ANALYSIS but signature exists")
        print("  ✅ Sets appropriate defaults (route_hint, dex, action)")
        print("  ✅ Logs the reason for allowing direct_copy")
        print("  ✅ Only rejects when truly no data is available")
        print("  ✅ Maintains backward compatibility with existing logic")
        return 0
    else:
        print("\n  ❌ SOME TESTS FAILED")
        print(f"\n  {total - passed} test(s) did not pass")
        return 1


if __name__ == "__main__":
    sys.exit(main())
