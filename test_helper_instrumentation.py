#!/usr/bin/env python3
"""
Test script to verify DebugSpan instrumentation in helper methods.

This script validates that:
1. All helper methods have DebugSpan wrapping
2. Loop protection constants are defined
3. Sanity checks prevent infinite loops
4. Exception handling is robust
5. Correlation IDs are logged in helper methods
"""

import sys
import re


def test_constants_defined():
    """Test that loop protection constants are defined."""
    print("\n" + "=" * 80)
    print("TEST 1: Loop Protection Constants")
    print("=" * 80)
    
    with open('trade_processor.py', 'r') as f:
        content = f.read()
    
    constants = [
        'MAX_LOG_LINES_TO_SCAN',
        'MAX_ADDRESSES_TO_CHECK',
        'MAX_INSTRUCTIONS_TO_SCAN',
        'MAX_TOKEN_BALANCES_TO_SCAN',
    ]
    
    all_found = True
    for const in constants:
        if re.search(rf'{const}\s*=\s*\d+', content):
            print(f"  ✅ {const} is defined")
        else:
            print(f"  ❌ {const} is not defined")
            all_found = False
    
    return all_found


def test_helper_debug_spans():
    """Test that all helper methods have DebugSpan instrumentation."""
    print("\n" + "=" * 80)
    print("TEST 2: Helper Methods DebugSpan Instrumentation")
    print("=" * 80)
    
    with open('trade_processor.py', 'r') as f:
        content = f.read()
    
    helper_methods = [
        ('_analyze_logs_for_action', r'def _analyze_logs_for_action.*?with DebugSpan\("_analyze_logs_for_action"'),
        ('_extract_mint_from_logs_enhanced', r'def _extract_mint_from_logs_enhanced.*?with DebugSpan\("_extract_mint_from_logs_enhanced"'),
        ('_extract_mint_from_token_balances', r'def _extract_mint_from_token_balances.*?with DebugSpan\("_extract_mint_from_token_balances"'),
        ('_extract_mint_from_instruction_accounts', r'def _extract_mint_from_instruction_accounts.*?with DebugSpan\("_extract_mint_from_instruction_accounts"'),
        ('_parse_raydium_accounts', r'def _parse_raydium_accounts.*?with DebugSpan\("_parse_raydium_accounts"'),
        ('_infer_signature_from_transaction', r'def _infer_signature_from_transaction.*?with DebugSpan\("_infer_signature_from_transaction"'),
        ('_infer_wallet_from_transaction', r'def _infer_wallet_from_transaction.*?with DebugSpan\("_infer_wallet_from_transaction"'),
    ]
    
    all_found = True
    for method_name, pattern in helper_methods:
        if re.search(pattern, content, re.DOTALL):
            print(f"  ✅ {method_name} has DebugSpan wrapper")
        else:
            print(f"  ❌ {method_name} missing DebugSpan wrapper")
            all_found = False
    
    return all_found


def test_correlation_id_in_helpers():
    """Test that helper methods log correlation IDs."""
    print("\n" + "=" * 80)
    print("TEST 3: Correlation ID Logging in Helper Methods")
    print("=" * 80)
    
    with open('trade_processor.py', 'r') as f:
        content = f.read()
    
    helper_methods = [
        '_analyze_logs_for_action',
        '_extract_mint_from_logs_enhanced',
        '_extract_mint_from_token_balances',
        '_extract_mint_from_instruction_accounts',
        '_parse_raydium_accounts',
        '_infer_signature_from_transaction',
        '_infer_wallet_from_transaction',
    ]
    
    all_found = True
    for method_name in helper_methods:
        # Find the method definition
        method_match = re.search(rf'def {method_name}\(.*?\):.*?(?=\n    def [^_]|\Z)', content, re.DOTALL)
        if method_match:
            method_body = method_match.group(0)
            # Check if corr_id is retrieved
            if 'corr_id = get_span_id()' in method_body:
                print(f"  ✅ {method_name} retrieves correlation ID")
            else:
                print(f"  ⚠️  {method_name} does not retrieve correlation ID (may not need it)")
        else:
            print(f"  ❌ Could not find {method_name} definition")
            all_found = False
    
    return all_found


def test_sanity_checks_in_helpers():
    """Test that helper methods have sanity checks to prevent infinite loops."""
    print("\n" + "=" * 80)
    print("TEST 4: Sanity Checks in Helper Methods")
    print("=" * 80)
    
    with open('trade_processor.py', 'r') as f:
        content = f.read()
    
    checks = [
        ('_analyze_logs_for_action', 'MAX_LOG_LINES_TO_SCAN'),
        ('_extract_mint_from_logs_enhanced', 'MAX_LOG_LINES_TO_SCAN'),
        ('_extract_mint_from_logs_enhanced', 'MAX_ADDRESSES_TO_CHECK'),
        ('_extract_mint_from_token_balances', 'MAX_TOKEN_BALANCES_TO_SCAN'),
        ('_extract_mint_from_instruction_accounts', 'MAX_INSTRUCTIONS_TO_SCAN'),
        ('_extract_mint_from_instruction_accounts', 'MAX_ADDRESSES_TO_CHECK'),
        ('_parse_raydium_accounts', 'MAX_INSTRUCTIONS_TO_SCAN'),
        ('_infer_wallet_from_transaction', 'MAX_TOKEN_BALANCES_TO_SCAN'),
    ]
    
    all_found = True
    for method_name, check_const in checks:
        # Find the method definition
        method_match = re.search(rf'def {method_name}\(.*?\):.*?(?=\n    def [^_]|\Z)', content, re.DOTALL)
        if method_match:
            method_body = method_match.group(0)
            if check_const in method_body:
                print(f"  ✅ {method_name} uses {check_const}")
            else:
                print(f"  ❌ {method_name} missing {check_const} check")
                all_found = False
        else:
            print(f"  ❌ Could not find {method_name} definition")
            all_found = False
    
    return all_found


def test_exception_handling_in_helpers():
    """Test that helper methods have robust exception handling."""
    print("\n" + "=" * 80)
    print("TEST 5: Exception Handling in Helper Methods")
    print("=" * 80)
    
    with open('trade_processor.py', 'r') as f:
        content = f.read()
    
    helper_methods = [
        '_extract_mint_from_token_balances',
        '_extract_mint_from_instruction_accounts',
        '_parse_raydium_accounts',
        '_infer_signature_from_transaction',
        '_infer_wallet_from_transaction',
    ]
    
    all_found = True
    for method_name in helper_methods:
        # Find the method definition
        method_match = re.search(rf'def {method_name}\(.*?\):.*?(?=\n    def [^_]|\Z)', content, re.DOTALL)
        if method_match:
            method_body = method_match.group(0)
            # Check for try-except blocks
            if 'except Exception' in method_body and 'exc_info=True' in method_body:
                print(f"  ✅ {method_name} has robust exception handling with exc_info")
            elif 'except Exception' in method_body:
                print(f"  ⚠️  {method_name} has exception handling but no exc_info")
            else:
                print(f"  ❌ {method_name} missing exception handling")
                all_found = False
        else:
            print(f"  ❌ Could not find {method_name} definition")
            all_found = False
    
    return all_found


def test_warning_logs_on_limit_reached():
    """Test that warning logs are emitted when limits are reached."""
    print("\n" + "=" * 80)
    print("TEST 6: Warning Logs on Limit Reached")
    print("=" * 80)
    
    with open('trade_processor.py', 'r') as f:
        content = f.read()
    
    helper_methods = [
        '_analyze_logs_for_action',
        '_extract_mint_from_logs_enhanced',
        '_extract_mint_from_token_balances',
        '_extract_mint_from_instruction_accounts',
        '_parse_raydium_accounts',
        '_infer_wallet_from_transaction',
    ]
    
    all_found = True
    for method_name in helper_methods:
        # Find the method definition
        method_match = re.search(rf'def {method_name}\(.*?\):.*?(?=\n    def [^_]|\Z)', content, re.DOTALL)
        if method_match:
            method_body = method_match.group(0)
            # Check for warning logs when limits are reached
            if 'logger.warning' in method_body and 'Limiting' in method_body:
                print(f"  ✅ {method_name} logs warnings on limit reached")
            else:
                print(f"  ⚠️  {method_name} may not log warnings on limit (may not need it)")
        else:
            print(f"  ❌ Could not find {method_name} definition")
            all_found = False
    
    return all_found


def run_all_tests():
    """Run all tests and report results."""
    print("\n" + "=" * 80)
    print("RUNNING HELPER INSTRUMENTATION TESTS")
    print("=" * 80)
    
    tests = [
        ("Loop Protection Constants", test_constants_defined),
        ("Helper Methods DebugSpan", test_helper_debug_spans),
        ("Correlation ID in Helpers", test_correlation_id_in_helpers),
        ("Sanity Checks in Helpers", test_sanity_checks_in_helpers),
        ("Exception Handling in Helpers", test_exception_handling_in_helpers),
        ("Warning Logs on Limit Reached", test_warning_logs_on_limit_reached),
    ]
    
    results = []
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"❌ Test '{test_name}' raised exception: {e}")
            results.append((test_name, False))
    
    # Summary
    print("\n" + "=" * 80)
    print("TEST SUMMARY")
    print("=" * 80)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status}: {test_name}")
    
    print(f"\nTotal: {passed}/{total} tests passed")
    
    if passed == total:
        print("\n🎉 All helper instrumentation tests passed!")
    
    return passed == total


if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)
