#!/usr/bin/env python3
"""
Test suite to validate the pipeline exit handoff implementation.

Validates that after infer_missing_fields:
1. Helper function _have_all_fields is used to check for complete fields
2. token_mint is normalized from mint field
3. use_universal_cloner is set to False when all fields are present
4. maybe_execute is called directly (not through route_and_execute)
5. Proper logging before/after with PIPELINE_EXIT messages
"""

import re
import sys


def test_helper_function_usage():
    """Test that _have_all_fields helper is used after infer_missing_fields"""
    print("=" * 80)
    print("TEST 1: Helper Function Usage")
    print("=" * 80)
    
    with open('main.py', 'r') as f:
        content = f.read()
    
    # Find the section after infer_missing_fields
    pattern = r"trade_info = self\.trade_processor\.infer_missing_fields\(trade_info\).*?(have_all = _have_all_fields\(trade_info\))"
    match = re.search(pattern, content, re.DOTALL)
    
    if not match:
        print("  ❌ _have_all_fields not called after infer_missing_fields")
        return False
    
    print("  ✅ _have_all_fields called after infer_missing_fields")
    return True


def test_token_mint_normalization():
    """Test that token_mint is normalized from mint field"""
    print("\n" + "=" * 80)
    print("TEST 2: Token Mint Normalization")
    print("=" * 80)
    
    with open('main.py', 'r') as f:
        content = f.read()
    
    # Look for the normalization pattern
    pattern = r'trade_info\["token_mint"\] = trade_info\.get\("token_mint"\) or trade_info\.get\("mint"\)'
    
    if not re.search(pattern, content):
        print("  ❌ Token mint normalization not found")
        return False
    
    print("  ✅ Token mint is normalized from mint field")
    return True


def test_use_universal_cloner_flag():
    """Test that use_universal_cloner is set based on have_all"""
    print("\n" + "=" * 80)
    print("TEST 3: use_universal_cloner Flag")
    print("=" * 80)
    
    with open('main.py', 'r') as f:
        content = f.read()
    
    # Look for the pattern: have_all = ... followed by use_universal_cloner = not have_all
    pattern = r"have_all = _have_all_fields\(trade_info\).*?trade_info\[\"use_universal_cloner\"\] = not have_all"
    
    if not re.search(pattern, content, re.DOTALL):
        print("  ❌ use_universal_cloner not set to 'not have_all'")
        return False
    
    print("  ✅ use_universal_cloner is set to False when all fields present (not have_all)")
    return True


def test_maybe_execute_direct_call():
    """Test that maybe_execute is called directly when have_all is True"""
    print("\n" + "=" * 80)
    print("TEST 4: Direct maybe_execute Call")
    print("=" * 80)
    
    with open('main.py', 'r') as f:
        content = f.read()
    
    # Look for the pattern: if have_all: ... await maybe_execute(...)
    pattern = r"if have_all:.*?await maybe_execute\("
    
    if not re.search(pattern, content, re.DOTALL):
        print("  ❌ maybe_execute not called directly when have_all is True")
        return False
    
    print("  ✅ maybe_execute is called directly when all fields are present")
    
    # Verify it's NOT using route_and_execute
    if "route_and_execute" in re.search(r"if have_all:.*?(?=else:|# STEP)", content, re.DOTALL).group(0):
        print("  ❌ Still using route_and_execute instead of direct maybe_execute")
        return False
    
    print("  ✅ Not using route_and_execute wrapper")
    return True


def test_pipeline_exit_logging():
    """Test that proper PIPELINE_EXIT logging is present"""
    print("\n" + "=" * 80)
    print("TEST 5: PIPELINE_EXIT Logging")
    print("=" * 80)
    
    with open('main.py', 'r') as f:
        content = f.read()
    
    # Look for success log when have_all is True
    success_pattern = r'if have_all:.*?logger\.info\(".*PIPELINE_EXIT.*Final fields ready.*coordinator"'
    
    if not re.search(success_pattern, content, re.DOTALL | re.IGNORECASE):
        print("  ❌ Missing success PIPELINE_EXIT log")
        return False
    
    print("  ✅ Success PIPELINE_EXIT log present")
    
    # Look for warning log when have_all is False
    warning_pattern = r'else:.*?logger\.warning\(".*PIPELINE_EXIT.*Incomplete fields"'
    
    if not re.search(warning_pattern, content, re.DOTALL | re.IGNORECASE):
        print("  ❌ Missing incomplete fields warning log")
        return False
    
    print("  ✅ Incomplete fields warning log present")
    return True


def test_async_handling():
    """Test that async is properly handled with await"""
    print("\n" + "=" * 80)
    print("TEST 6: Async Handling")
    print("=" * 80)
    
    with open('main.py', 'r') as f:
        content = f.read()
    
    # Look for await before maybe_execute
    pattern = r"await maybe_execute\(trade_info,"
    
    if not re.search(pattern, content):
        print("  ❌ maybe_execute not properly awaited")
        return False
    
    print("  ✅ maybe_execute is properly awaited")
    return True


def test_rpc_url_extraction():
    """Test that rpc_url is extracted from rpc_client"""
    print("\n" + "=" * 80)
    print("TEST 7: RPC URL Extraction")
    print("=" * 80)
    
    with open('main.py', 'r') as f:
        content = f.read()
    
    # Look for rpc_url extraction pattern
    pattern = r'rpc_url = self\.rpc_client\.rpc_url if hasattr\(self\.rpc_client, ["\']rpc_url["\']\) else self\.rpc_client'
    
    if not re.search(pattern, content):
        print("  ❌ RPC URL not properly extracted")
        return False
    
    print("  ✅ RPC URL is properly extracted from rpc_client")
    return True


def test_complete_flow():
    """Test the complete flow matches problem statement"""
    print("\n" + "=" * 80)
    print("TEST 8: Complete Flow Validation")
    print("=" * 80)
    
    with open('main.py', 'r') as f:
        content = f.read()
    
    # Extract the section after infer_missing_fields
    pattern = r"trade_info = self\.trade_processor\.infer_missing_fields\(trade_info\).*?(?=# STEP 2:)"
    match = re.search(pattern, content, re.DOTALL)
    
    if not match:
        print("  ❌ Could not find the complete flow section")
        return False
    
    flow = match.group(0)
    
    # Check the flow has all required components in order
    checks = [
        (r"have_all = _have_all_fields\(trade_info\)", "✅ Step 1: Check for all fields"),
        (r'trade_info\["token_mint"\] = trade_info\.get\("token_mint"\) or trade_info\.get\("mint"\)', 
         "✅ Step 2: Normalize token_mint"),
        (r'trade_info\["use_universal_cloner"\] = not have_all', 
         "✅ Step 3: Set use_universal_cloner flag"),
        (r"if have_all:", "✅ Step 4: Check if all fields present"),
        (r'logger\.info\(".*PIPELINE_EXIT.*Final fields ready', 
         "✅ Step 5: Log success message"),
        (r"await maybe_execute\(", "✅ Step 6: Call maybe_execute"),
        (r"else:.*logger\.warning\(.*PIPELINE_EXIT.*Incomplete", 
         "✅ Step 7: Log incomplete fields warning"),
    ]
    
    passed = 0
    for pattern, description in checks:
        if re.search(pattern, flow, re.DOTALL):
            print(f"  {description}")
            passed += 1
        else:
            print(f"  ❌ {description.replace('✅', '')}")
    
    print(f"\n  Flow steps: {passed}/{len(checks)} validated")
    return passed == len(checks)


def main():
    """Run all tests"""
    print("\n" + "=" * 80)
    print("PIPELINE EXIT HANDOFF IMPLEMENTATION VALIDATION")
    print("=" * 80 + "\n")
    
    tests = [
        ("Helper function usage", test_helper_function_usage),
        ("Token mint normalization", test_token_mint_normalization),
        ("use_universal_cloner flag", test_use_universal_cloner_flag),
        ("Direct maybe_execute call", test_maybe_execute_direct_call),
        ("PIPELINE_EXIT logging", test_pipeline_exit_logging),
        ("Async handling", test_async_handling),
        ("RPC URL extraction", test_rpc_url_extraction),
        ("Complete flow validation", test_complete_flow),
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
        print()
        print("  The pipeline exit handoff implementation is complete:")
        print("  ✅ Helper function checks for all required fields")
        print("  ✅ Token mint is normalized from mint field")
        print("  ✅ use_universal_cloner set to False when all fields present")
        print("  ✅ maybe_execute called directly (not through route_and_execute)")
        print("  ✅ Proper PIPELINE_EXIT logging before/after")
        print("  ✅ Async properly handled with await")
        print("  ✅ RPC URL properly extracted from client")
        print()
        return 0
    else:
        print("  ❌ SOME TESTS FAILED")
        print("  ❌ Review implementation against problem statement")
        print()
        return 1


if __name__ == "__main__":
    sys.exit(main())
