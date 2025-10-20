#!/usr/bin/env python3
"""
Test to validate that _have_all_fields matches the exact specification from problem statement.

The problem statement specifies:
def _have_all_fields(ti):
    tok = ti.get("token_mint") or ti.get("mint")
    return all(ti.get(k) not in (None, "", "unknown", "PENDING_ANALYSIS") for k in ("dex","action","wallet_address")) and bool(tok)
"""

import sys
import re


def test_exact_helper_function():
    """Test that _have_all_fields exactly matches problem statement spec"""
    print("=" * 80)
    print("TEST: Exact Helper Function Matches Problem Statement")
    print("=" * 80)
    
    with open('main.py', 'r') as f:
        content = f.read()
    
    # Find the _have_all_fields function
    pattern = r'def _have_all_fields\(.*?\):(.*?)(?=\ndef |\nclass |\nif __name__|$)'
    match = re.search(pattern, content, re.DOTALL)
    
    if not match:
        print("  ❌ Could not find _have_all_fields function")
        return False
    
    func_body = match.group(0)
    
    # Check for exact implementation from problem statement
    checks = [
        (r'tok = ti\.get\("token_mint"\) or ti\.get\("mint"\)', 
         "✅ Gets token from token_mint or mint"),
        (r'return all\(ti\.get\(k\) not in \(None, "", "unknown", "PENDING_ANALYSIS"\) for k in \("dex","action","wallet_address"\)\) and bool\(tok\)',
         "✅ Returns all fields check AND bool(tok)"),
    ]
    
    passed = 0
    for pattern, description in checks:
        if re.search(pattern, func_body):
            print(f"  {description}")
            passed += 1
        else:
            print(f"  ❌ {description.replace('✅', '')}")
    
    if passed == len(checks):
        print("\n  ✅ Helper function matches problem statement exactly!")
        return True
    else:
        print(f"\n  ❌ Helper function does not match problem statement")
        return False


def test_helper_behavior():
    """Test that helper function behaves correctly"""
    print("\n" + "=" * 80)
    print("TEST: Helper Function Behavior")
    print("=" * 80)
    
    # Import the function (we'll just check the logic is correct via code inspection)
    with open('main.py', 'r') as f:
        content = f.read()
    
    # Find the function
    pattern = r'def _have_all_fields\(.*?\):(.*?)(?=\ndef |\nclass |\nif __name__|$)'
    match = re.search(pattern, content, re.DOTALL)
    
    if not match:
        print("  ❌ Could not find _have_all_fields function")
        return False
    
    func_body = match.group(0)
    
    # Check that it checks all required fields
    if 'dex' in func_body and 'action' in func_body and 'wallet_address' in func_body:
        print("  ✅ Checks dex, action, and wallet_address fields")
    else:
        print("  ❌ Missing field checks")
        return False
    
    # Check that it checks for invalid values
    if 'None' in func_body and '""' in func_body and '"unknown"' in func_body and '"PENDING_ANALYSIS"' in func_body:
        print("  ✅ Checks for None, empty string, 'unknown', and 'PENDING_ANALYSIS'")
    else:
        print("  ❌ Missing invalid value checks")
        return False
    
    # Check that it handles both token_mint and mint
    if 'token_mint' in func_body and 'mint' in func_body:
        print("  ✅ Accepts both token_mint and mint fields")
    else:
        print("  ❌ Does not handle both token_mint and mint")
        return False
    
    return True


def main():
    """Run all tests"""
    print("\n" + "=" * 80)
    print("PROBLEM STATEMENT HELPER FUNCTION VALIDATION")
    print("=" * 80 + "\n")
    
    tests = [
        test_exact_helper_function(),
        test_helper_behavior(),
    ]
    
    passed = sum(tests)
    total = len(tests)
    
    print("\n" + "=" * 80)
    print("SUMMARY")
    print("=" * 80)
    print(f"\n  Tests Passed: {passed}/{total}")
    
    if all(tests):
        print("\n  🎉 HELPER FUNCTION VALIDATED!")
        print("\n  The _have_all_fields helper function:")
        print("  ✅ Exactly matches the problem statement specification")
        print("  ✅ Checks all required fields (dex, action, wallet_address)")
        print("  ✅ Checks for invalid values (None, '', 'unknown', 'PENDING_ANALYSIS')")
        print("  ✅ Accepts both token_mint and mint fields")
        print()
        return 0
    else:
        print("\n  ❌ SOME TESTS FAILED")
        print("  ❌ Review helper function implementation")
        print()
        return 1


if __name__ == "__main__":
    sys.exit(main())
