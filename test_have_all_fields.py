#!/usr/bin/env python3
"""
Test suite for _have_all_fields helper function.

Validates that:
1. Function checks all required fields (dex, action, wallet_address, token_mint/mint)
2. Function normalizes mint to token_mint
3. Function returns False for incomplete/invalid fields
4. Function returns True for complete valid fields
"""

import sys
import os

# Add parent directory to path to import from main
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_have_all_fields_complete():
    """Test that _have_all_fields returns True for complete fields"""
    print("=" * 80)
    print("TEST 1: _have_all_fields with Complete Fields")
    print("=" * 80)
    
    # Import the function
    from main import _have_all_fields
    
    trade_info = {
        "dex": "jupiter",
        "action": "buy",
        "wallet_address": "ABC123",
        "token_mint": "XYZ789"
    }
    
    result = _have_all_fields(trade_info)
    
    print(f"  Input: {trade_info}")
    print(f"  Result: {result}")
    
    if result:
        print("  ✅ PASS: Returns True for complete fields")
        return True
    else:
        print("  ❌ FAIL: Should return True for complete fields")
        return False


def test_have_all_fields_mint_normalization():
    """Test that _have_all_fields normalizes mint to token_mint"""
    print("=" * 80)
    print("TEST 2: _have_all_fields Normalizes mint to token_mint")
    print("=" * 80)
    
    from main import _have_all_fields
    
    trade_info = {
        "dex": "jupiter",
        "action": "buy",
        "wallet_address": "ABC123",
        "mint": "XYZ789"  # Using "mint" instead of "token_mint"
    }
    
    result = _have_all_fields(trade_info)
    
    print(f"  Input: {trade_info}")
    print(f"  Result: {result}")
    print(f"  Normalized trade_info: {trade_info}")
    
    if result and trade_info.get("token_mint") == "XYZ789":
        print("  ✅ PASS: Normalizes mint to token_mint")
        return True
    else:
        print(f"  ❌ FAIL: Should normalize mint to token_mint (got token_mint={trade_info.get('token_mint')})")
        return False


def test_have_all_fields_incomplete():
    """Test that _have_all_fields returns False for incomplete fields"""
    print("=" * 80)
    print("TEST 3: _have_all_fields with Incomplete Fields")
    print("=" * 80)
    
    from main import _have_all_fields
    
    test_cases = [
        ({"dex": "unknown", "action": "buy", "wallet_address": "ABC", "token_mint": "XYZ"}, "dex=unknown"),
        ({"dex": "jupiter", "action": "unknown", "wallet_address": "ABC", "token_mint": "XYZ"}, "action=unknown"),
        ({"dex": "jupiter", "action": "buy", "wallet_address": "", "token_mint": "XYZ"}, "wallet_address empty"),
        ({"dex": "jupiter", "action": "buy", "wallet_address": "ABC", "token_mint": None}, "token_mint=None"),
        ({"dex": "jupiter", "action": "buy", "wallet_address": "ABC", "token_mint": "PENDING_ANALYSIS"}, "token_mint=PENDING_ANALYSIS"),
    ]
    
    passed = 0
    for trade_info, description in test_cases:
        result = _have_all_fields(trade_info.copy())
        if not result:
            print(f"  ✅ Correctly returns False for: {description}")
            passed += 1
        else:
            print(f"  ❌ Should return False for: {description}")
    
    print(f"\n  Result: {passed}/{len(test_cases)} checks passed\n")
    return passed == len(test_cases)


def test_have_all_fields_both_mint_and_token_mint():
    """Test that _have_all_fields prefers token_mint over mint"""
    print("=" * 80)
    print("TEST 4: _have_all_fields with Both mint and token_mint")
    print("=" * 80)
    
    from main import _have_all_fields
    
    trade_info = {
        "dex": "jupiter",
        "action": "buy",
        "wallet_address": "ABC123",
        "token_mint": "PRIMARY",
        "mint": "SECONDARY"
    }
    
    result = _have_all_fields(trade_info)
    
    print(f"  Input: {trade_info}")
    print(f"  Result: {result}")
    
    # Should use token_mint when both present
    if result and trade_info.get("token_mint") == "PRIMARY":
        print("  ✅ PASS: Prefers token_mint over mint when both present")
        return True
    else:
        print(f"  ❌ FAIL: Should prefer token_mint (got {trade_info.get('token_mint')})")
        return False


def test_have_all_fields_missing_field():
    """Test that _have_all_fields returns False for missing required fields"""
    print("=" * 80)
    print("TEST 5: _have_all_fields with Missing Fields")
    print("=" * 80)
    
    from main import _have_all_fields
    
    test_cases = [
        ({"action": "buy", "wallet_address": "ABC", "token_mint": "XYZ"}, "missing dex"),
        ({"dex": "jupiter", "wallet_address": "ABC", "token_mint": "XYZ"}, "missing action"),
        ({"dex": "jupiter", "action": "buy", "token_mint": "XYZ"}, "missing wallet_address"),
        ({"dex": "jupiter", "action": "buy", "wallet_address": "ABC"}, "missing token_mint/mint"),
    ]
    
    passed = 0
    for trade_info, description in test_cases:
        result = _have_all_fields(trade_info.copy())
        if not result:
            print(f"  ✅ Correctly returns False for: {description}")
            passed += 1
        else:
            print(f"  ❌ Should return False for: {description}")
    
    print(f"\n  Result: {passed}/{len(test_cases)} checks passed\n")
    return passed == len(test_cases)


def main():
    """Run all tests"""
    print("\n" + "=" * 80)
    print("_HAVE_ALL_FIELDS IMPLEMENTATION VALIDATION")
    print("=" * 80 + "\n")
    
    tests = [
        ("Complete fields", test_have_all_fields_complete),
        ("mint normalization", test_have_all_fields_mint_normalization),
        ("Incomplete fields", test_have_all_fields_incomplete),
        ("Both mint and token_mint", test_have_all_fields_both_mint_and_token_mint),
        ("Missing fields", test_have_all_fields_missing_field),
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
        print()
    
    # Summary
    print("=" * 80)
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
        print()
        print("  The _have_all_fields implementation is complete:")
        print("  ✅ Checks all required fields")
        print("  ✅ Normalizes mint to token_mint")
        print("  ✅ Validates field values correctly")
        print("  ✅ Handles missing/invalid fields properly")
        return 0
    else:
        print("  ❌ SOME TESTS FAILED")
        print("  ❌ Review implementation")
        return 1


if __name__ == "__main__":
    # Suppress import warnings for test
    import warnings
    warnings.filterwarnings("ignore")
    sys.exit(main())
