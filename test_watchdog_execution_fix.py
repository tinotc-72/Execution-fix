#!/usr/bin/env python3
"""
Test for watchdog-protected infer_missing_fields with guaranteed execution.

This test validates that:
1. _have_all_fields is lenient (only requires dex, wallet_address, token_mint)
2. infer_missing_fields is wrapped with run_with_watchdog (5s timeout)
3. route_and_execute is always called in finally block
4. Before/After infer_missing_fields logs are present
"""

import re
import sys
import os

def test_have_all_fields_lenient():
    """Test that _have_all_fields only requires dex, wallet_address, and token_mint"""
    print("\n" + "="*80)
    print("TEST 1: _have_all_fields is lenient (does not require action)")
    print("="*80)
    
    with open('main.py', 'r') as f:
        content = f.read()
    
    # Find _have_all_fields function
    pattern = r'def _have_all_fields\(trade_info: dict\) -> bool:(.*?)(?=\ndef )'
    match = re.search(pattern, content, re.DOTALL)
    
    if not match:
        print("❌ FAIL: Could not find _have_all_fields function")
        return False
    
    func_body = match.group(1)
    
    # Check that function comment mentions lenient behavior
    if "LENIENT" not in func_body:
        print("❌ FAIL: Function should be marked as LENIENT in comments")
        return False
    
    # Check that function does NOT require action field
    if "action" in func_body.lower() and "not require action" not in func_body.lower():
        # Make sure it's not checking for action as a required field
        if 'trade_info.get("action")' in func_body or "trade_info.get('action')" in func_body:
            print("❌ FAIL: Function should not check for action field")
            return False
    
    # Check that it normalizes mint to token_mint
    if "token_mint" not in func_body or "mint" not in func_body:
        print("❌ FAIL: Function should normalize mint to token_mint")
        return False
    
    # Check that it only checks dex, wallet_address, and token_mint
    if "dex" not in func_body or "wallet_address" not in func_body:
        print("❌ FAIL: Function should check dex and wallet_address")
        return False
    
    print("✅ PASS: _have_all_fields is lenient and only requires dex, wallet_address, and token_mint")
    return True


def test_watchdog_wrapper():
    """Test that infer_missing_fields is wrapped with run_with_watchdog"""
    print("\n" + "="*80)
    print("TEST 2: infer_missing_fields wrapped with run_with_watchdog")
    print("="*80)
    
    with open('main.py', 'r') as f:
        content = f.read()
    
    # Look for the watchdog wrapper pattern
    if "run_with_watchdog" not in content:
        print("❌ FAIL: run_with_watchdog not found in main.py")
        return False
    
    # Check for 5 second timeout
    if "timeout_seconds=5.0" not in content:
        print("❌ FAIL: timeout_seconds should be 5.0 as per problem statement")
        return False
    
    # Check for operation_name="infer_missing_fields"
    if 'operation_name="infer_missing_fields"' not in content:
        print("❌ FAIL: operation_name should be 'infer_missing_fields'")
        return False
    
    # Check for fallback_value=trade_info
    if "fallback_value=trade_info" not in content:
        print("❌ FAIL: fallback_value should be trade_info")
        return False
    
    # Check for log_timeout=True and log_error=True
    if "log_timeout=True" not in content or "log_error=True" not in content:
        print("❌ FAIL: log_timeout and log_error should both be True")
        return False
    
    print("✅ PASS: infer_missing_fields is wrapped with run_with_watchdog with correct parameters")
    return True


def test_guaranteed_execution():
    """Test that route_and_execute is always called in finally block"""
    print("\n" + "="*80)
    print("TEST 3: route_and_execute always called in finally block")
    print("="*80)
    
    with open('main.py', 'r') as f:
        content = f.read()
    
    # Find the try/except/finally block for infer_missing_fields
    # Look for pattern: try: ... run_with_watchdog ... except ... finally: ... route_and_execute
    
    # Check that finally block exists and contains route_and_execute
    pattern = r'finally:.*?route_and_execute\(trade_info'
    if not re.search(pattern, content, re.DOTALL):
        print("❌ FAIL: route_and_execute not found in finally block")
        return False
    
    # Check for the handoff logs
    if '"📤 [HANDOFF] Calling coordinator now…"' not in content:
        print("❌ FAIL: Missing '📤 [HANDOFF] Calling coordinator now…' log")
        return False
    
    if '"📥 [HANDOFF] Coordinator call returned"' not in content:
        print("❌ FAIL: Missing '📥 [HANDOFF] Coordinator call returned' log")
        return False
    
    print("✅ PASS: route_and_execute is always called in finally block with handoff logs")
    return True


def test_before_after_logs():
    """Test that Before/After infer_missing_fields logs are present"""
    print("\n" + "="*80)
    print("TEST 4: Before/After infer_missing_fields debug logs")
    print("="*80)
    
    with open('main.py', 'r') as f:
        content = f.read()
    
    # Check for Before log
    if '"[DEBUG] Before infer_missing_fields:' not in content:
        print("❌ FAIL: Missing '[DEBUG] Before infer_missing_fields:' log")
        return False
    
    # Check for After log
    if '"[DEBUG] After infer_missing_fields:' not in content:
        print("❌ FAIL: Missing '[DEBUG] After infer_missing_fields:' log")
        return False
    
    # Check that safe_dump is used
    if "safe_dump(trade_info)" not in content:
        print("❌ FAIL: safe_dump should be used for logging trade_info")
        return False
    
    print("✅ PASS: Before/After infer_missing_fields debug logs are present with safe_dump")
    return True


def test_safe_dump_function():
    """Test that safe_dump utility function exists"""
    print("\n" + "="*80)
    print("TEST 5: safe_dump utility function exists")
    print("="*80)
    
    with open('main.py', 'r') as f:
        content = f.read()
    
    # Check for safe_dump function
    if "def safe_dump(" not in content:
        print("❌ FAIL: safe_dump function not found")
        return False
    
    # Check that it handles serialization errors
    if "json.dumps" not in content or "default=str" not in content:
        print("❌ FAIL: safe_dump should use json.dumps with default=str")
        return False
    
    print("✅ PASS: safe_dump utility function exists and handles serialization")
    return True


def main():
    """Run all tests"""
    print("\n" + "="*80)
    print("WATCHDOG EXECUTION FIX - TEST SUITE")
    print("="*80)
    print("Testing implementation of watchdog-protected infer_missing_fields")
    print("with guaranteed execution flow to coordinator")
    
    results = []
    
    # Run all tests
    results.append(("_have_all_fields lenient", test_have_all_fields_lenient()))
    results.append(("run_with_watchdog wrapper", test_watchdog_wrapper()))
    results.append(("Guaranteed execution", test_guaranteed_execution()))
    results.append(("Before/After logs", test_before_after_logs()))
    results.append(("safe_dump function", test_safe_dump_function()))
    
    # Summary
    print("\n" + "="*80)
    print("TEST SUMMARY")
    print("="*80)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status}: {name}")
    
    print("\n" + "-"*80)
    print(f"Results: {passed}/{total} tests passed")
    print("="*80)
    
    # Exit with appropriate code
    sys.exit(0 if passed == total else 1)


if __name__ == "__main__":
    main()
