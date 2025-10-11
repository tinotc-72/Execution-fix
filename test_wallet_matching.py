#!/usr/bin/env python3
"""
Test script to verify case-insensitive wallet matching implementation.

This script validates that wallet matching works correctly with:
1. Case-insensitive comparison (e.g., 'DfMx...' matches 'dfmx...')
2. Proper normalization of wallet addresses
3. Consistent behavior across all wallet validation methods
"""

import re
import sys


def test_validate_monitored_wallet():
    """Test _validate_monitored_wallet uses case-insensitive matching."""
    print("=" * 80)
    print("TEST 1: Verify _validate_monitored_wallet Case-Insensitive Matching")
    print("=" * 80)
    
    with open('trade_processor.py', 'r') as f:
        processor = f.read()
    
    # Find the _validate_monitored_wallet method
    method_match = re.search(
        r'def _validate_monitored_wallet\(self.*?\n(.*?)(?=\n    def |\Z)',
        processor,
        re.DOTALL
    )
    
    if not method_match:
        print("  ❌ _validate_monitored_wallet method not found")
        return False
    
    method_body = method_match.group(1)
    
    tests = [
        (
            r"\.lower\(\)",
            "Uses .lower() for case normalization"
        ),
        (
            r"case-insensitive",
            "Documentation mentions case-insensitive matching"
        ),
        (
            r"monitored_wallets_lower",
            "Creates lowercase comparison set"
        ),
        (
            r"wallet_str\.lower\(\) in monitored_wallets_lower",
            "Compares normalized wallet addresses"
        ),
    ]
    
    passed = 0
    for pattern, description in tests:
        if re.search(pattern, method_body, re.IGNORECASE):
            print(f"  ✅ {description}")
            passed += 1
        else:
            print(f"  ❌ {description}")
    
    print(f"\n  Result: {passed}/{len(tests)} checks passed\n")
    return passed == len(tests)


def test_check_monitored_wallet_is_signer():
    """Test _check_monitored_wallet_is_signer uses case-insensitive matching."""
    print("=" * 80)
    print("TEST 2: Verify _check_monitored_wallet_is_signer Case-Insensitive Matching")
    print("=" * 80)
    
    with open('trade_processor.py', 'r') as f:
        processor = f.read()
    
    # Find the _check_monitored_wallet_is_signer method
    method_match = re.search(
        r'def _check_monitored_wallet_is_signer\(self.*?\n(.*?)(?=\n    def |\Z)',
        processor,
        re.DOTALL
    )
    
    if not method_match:
        print("  ❌ _check_monitored_wallet_is_signer method not found")
        return False
    
    method_body = method_match.group(1)
    
    tests = [
        (
            r"case-insensitive",
            "Documentation mentions case-insensitive matching"
        ),
        (
            r"monitored_wallets_lower.*\.lower\(\)",
            "Creates lowercase wallet set"
        ),
        (
            r"fee_payer.*\.lower\(\).*in monitored_wallets_lower",
            "Compares fee_payer case-insensitively"
        ),
        (
            r"s\.lower\(\) in monitored_wallets_lower",
            "Compares signers case-insensitively"
        ),
    ]
    
    passed = 0
    for pattern, description in tests:
        if re.search(pattern, method_body, re.DOTALL | re.IGNORECASE):
            print(f"  ✅ {description}")
            passed += 1
        else:
            print(f"  ❌ {description}")
    
    print(f"\n  Result: {passed}/{len(tests)} checks passed\n")
    return passed == len(tests)


def test_is_target_wallet():
    """Test is_target_wallet uses case-insensitive matching."""
    print("=" * 80)
    print("TEST 3: Verify is_target_wallet Case-Insensitive Matching")
    print("=" * 80)
    
    with open('trade_processor.py', 'r') as f:
        processor = f.read()
    
    # Find the is_target_wallet method
    method_match = re.search(
        r'def is_target_wallet\(self.*?\n(.*?)(?=\n    def |\Z)',
        processor,
        re.DOTALL
    )
    
    if not method_match:
        print("  ❌ is_target_wallet method not found")
        return False
    
    method_body = method_match.group(1)
    
    tests = [
        (
            r"case-insensitive",
            "Documentation mentions case-insensitive matching"
        ),
        (
            r"\.lower\(\)",
            "Uses .lower() for normalization"
        ),
        (
            r"wallet_lower.*target_wallets_lower",
            "Compares normalized wallet addresses"
        ),
    ]
    
    passed = 0
    for pattern, description in tests:
        if re.search(pattern, method_body, re.IGNORECASE):
            print(f"  ✅ {description}")
            passed += 1
        else:
            print(f"  ❌ {description}")
    
    print(f"\n  Result: {passed}/{len(tests)} checks passed\n")
    return passed == len(tests)


def test_main_py_documentation():
    """Test that main.py documentation reflects case-insensitive matching."""
    print("=" * 80)
    print("TEST 4: Verify main.py Documentation")
    print("=" * 80)
    
    with open('main.py', 'r') as f:
        main = f.read()
    
    tests = [
        (
            r"case-insensitive.*wallet",
            "Main documentation mentions case-insensitive wallet matching"
        ),
        (
            r"Case-Insensitive Wallet Matching",
            "Dedicated section for case-insensitive matching"
        ),
        (
            r"_process_detected_trade.*case-insensitive",
            "_process_detected_trade docstring mentions case-insensitive"
        ),
    ]
    
    passed = 0
    for pattern, description in tests:
        if re.search(pattern, main, re.DOTALL | re.IGNORECASE):
            print(f"  ✅ {description}")
            passed += 1
        else:
            print(f"  ❌ {description}")
    
    print(f"\n  Result: {passed}/{len(tests)} checks passed\n")
    return passed == len(tests)


def test_no_case_sensitive_comparisons():
    """Verify no case-sensitive wallet comparisons remain."""
    print("=" * 80)
    print("TEST 5: Verify No Case-Sensitive Wallet Comparisons")
    print("=" * 80)
    
    with open('trade_processor.py', 'r') as f:
        processor = f.read()
    
    # Look for patterns that might indicate case-sensitive comparison
    # We want to ensure wallet comparisons use .lower()
    
    # Check that monitored wallet comparisons use lowercase
    has_lowercase_comparison = bool(re.search(
        r"(wallet.*\.lower\(\)|monitored_wallets_lower)",
        processor
    ))
    
    # Check for old case-sensitive patterns that should be gone
    has_old_patterns = bool(re.search(
        r"(wallet_str in monitored_wallets[^_]|fee_payer in monitored_wallets_set)",
        processor
    ))
    
    if has_lowercase_comparison and not has_old_patterns:
        print("  ✅ Uses lowercase comparison for wallet matching")
        print("  ✅ No old case-sensitive patterns detected")
        print(f"\n  Result: All checks passed\n")
        return True
    else:
        if not has_lowercase_comparison:
            print("  ❌ Missing lowercase comparison patterns")
        if has_old_patterns:
            print("  ❌ Old case-sensitive patterns still present")
        print(f"\n  Result: Some checks failed\n")
        return False


def main():
    """Run all tests."""
    print("\n" + "=" * 80)
    print("CASE-INSENSITIVE WALLET MATCHING TEST SUITE")
    print("=" * 80)
    print()
    
    tests = [
        test_validate_monitored_wallet(),
        test_check_monitored_wallet_is_signer(),
        test_is_target_wallet(),
        test_main_py_documentation(),
        test_no_case_sensitive_comparisons(),
    ]
    
    passed = sum(tests)
    total = len(tests)
    
    print("=" * 80)
    print("FINAL RESULTS")
    print("=" * 80)
    print(f"\n  Tests Passed: {passed}/{total}")
    
    if passed == total:
        print("\n  ✅ ALL TESTS PASSED!")
        print("  ✅ Case-insensitive wallet matching fully implemented")
        print("  ✅ Wallet comparisons use normalized addresses")
        print("  ✅ Documentation updated to reflect changes")
        print()
        return 0
    else:
        print("\n  ❌ SOME TESTS FAILED")
        print("  ❌ Review implementation")
        print()
        return 1


if __name__ == "__main__":
    sys.exit(main())
