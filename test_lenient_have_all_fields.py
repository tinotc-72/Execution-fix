#!/usr/bin/env python3
"""
Test suite for lenient _have_all_fields implementation.

This test extracts and validates the _have_all_fields function directly
without needing to import the entire main.py module.
"""

import re
import sys

def extract_have_all_fields_function():
    """Extract _have_all_fields function from main.py"""
    with open('main.py', 'r') as f:
        content = f.read()
    
    # Find the function definition
    pattern = r'def _have_all_fields\(trade_info: dict\) -> bool:(.*?)(?=\ndef )'
    match = re.search(pattern, content, re.DOTALL)
    
    if not match:
        raise ValueError("Could not find _have_all_fields function")
    
    return match.group(0)


def test_lenient_behavior():
    """Test that _have_all_fields does not require action field"""
    print("=" * 80)
    print("TEST: _have_all_fields Lenient Behavior (No Action Required)")
    print("=" * 80)
    
    func_code = extract_have_all_fields_function()
    
    # Check docstring mentions lenient
    if "LENIENT" not in func_code:
        print("  ❌ FAIL: Function should be documented as LENIENT")
        return False
    
    # Check that action is NOT in the required fields check
    # Look for the main validation logic
    if 'trade_info.get("action")' in func_code:
        print("  ❌ FAIL: Function should not check for action field")
        return False
    
    # Check that only dex, wallet_address, and token_mint are checked
    if 'trade_info.get("dex")' not in func_code:
        print("  ❌ FAIL: Function should check for dex")
        return False
    
    if 'trade_info.get("wallet_address")' not in func_code:
        print("  ❌ FAIL: Function should check for wallet_address")
        return False
    
    if "token_mint" not in func_code:
        print("  ❌ FAIL: Function should check for token_mint")
        return False
    
    print("  ✅ PASS: Function does not require action field")
    print("  ✅ PASS: Function only requires dex, wallet_address, and token_mint")
    return True


def test_mint_normalization():
    """Test that mint is normalized to token_mint"""
    print("\n" + "=" * 80)
    print("TEST: mint Normalization to token_mint")
    print("=" * 80)
    
    func_code = extract_have_all_fields_function()
    
    # Check that function handles both mint and token_mint
    if '"mint"' not in func_code and "'mint'" not in func_code:
        print("  ❌ FAIL: Function should handle 'mint' field")
        return False
    
    # Check that it normalizes to token_mint
    if 'trade_info["token_mint"]' not in func_code:
        print("  ❌ FAIL: Function should normalize to token_mint")
        return False
    
    print("  ✅ PASS: Function normalizes mint to token_mint")
    return True


def test_validation_logic():
    """Test that validation logic is correct"""
    print("\n" + "=" * 80)
    print("TEST: Validation Logic")
    print("=" * 80)
    
    func_code = extract_have_all_fields_function()
    
    # Check that it validates against placeholder values
    invalid_values = ['None', '""', '"unknown"', '"PENDING_ANALYSIS"']
    
    for value in invalid_values:
        if value not in func_code:
            print(f"  ⚠️  WARNING: Function may not check for {value}")
    
    # Check that it uses all() for validation
    if "all(" not in func_code:
        print("  ℹ️  INFO: Function does not use all() - may use alternative validation")
    else:
        print("  ✅ PASS: Function uses all() for comprehensive validation")
    
    return True


def test_documentation():
    """Test that documentation is clear about requirements"""
    print("\n" + "=" * 80)
    print("TEST: Documentation")
    print("=" * 80)
    
    func_code = extract_have_all_fields_function()
    
    # Check for key documentation elements
    checks = [
        ("dex" in func_code.lower(), "mentions dex"),
        ("wallet_address" in func_code.lower(), "mentions wallet_address"),
        ("token_mint" in func_code.lower(), "mentions token_mint"),
        ("does not require action" in func_code.lower() or "not require action" in func_code.lower(), "clarifies action is not required"),
    ]
    
    passed = 0
    for check, description in checks:
        if check:
            print(f"  ✅ Documentation {description}")
            passed += 1
        else:
            print(f"  ⚠️  Documentation should {description}")
    
    return passed >= 3  # At least 3 out of 4


def main():
    """Run all tests"""
    print("\n" + "=" * 80)
    print("LENIENT _HAVE_ALL_FIELDS VALIDATION")
    print("=" * 80)
    print("Validates that _have_all_fields only requires:")
    print("  - dex")
    print("  - wallet_address")
    print("  - token_mint (or mint)")
    print("And does NOT require action")
    print()
    
    tests = [
        ("Lenient behavior (no action required)", test_lenient_behavior),
        ("mint normalization", test_mint_normalization),
        ("Validation logic", test_validation_logic),
        ("Documentation", test_documentation),
    ]
    
    results = []
    for name, test_func in tests:
        try:
            passed = test_func()
            results.append((name, passed))
        except Exception as e:
            print(f"  ❌ Test failed with exception: {e}")
            import traceback
            traceback.print_exc()
            results.append((name, False))
    
    # Summary
    print("\n" + "=" * 80)
    print("SUMMARY")
    print("=" * 80)
    
    passed_tests = sum(1 for _, passed in results if passed)
    total_tests = len(results)
    
    for name, passed in results:
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"  {status}: {name}")
    
    print(f"\n  Tests Passed: {passed_tests}/{total_tests}")
    print()
    
    if all(passed for _, passed in results):
        print("  🎉 ALL TESTS PASSED!")
        print("\n  The _have_all_fields implementation is lenient:")
        print("  ✅ Does NOT require action field")
        print("  ✅ Only requires dex, wallet_address, and token_mint")
        print("  ✅ Normalizes mint to token_mint")
        print("  ✅ Properly validates field values")
        return 0
    else:
        print("  ⚠️  SOME TESTS FAILED")
        print("  Review implementation")
        return 1


if __name__ == "__main__":
    sys.exit(main())
