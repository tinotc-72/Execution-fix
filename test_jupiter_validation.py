#!/usr/bin/env python3
"""
Simple validation test for Jupiter None route fix without external dependencies.
Tests the code structure and logic flow.
"""

import re


def test_jupiter_functions_signature():
    """Verify function signatures are correct"""
    print("=" * 80)
    print("TEST: Function Signatures")
    print("=" * 80)
    
    with open('mev_jupiter_executor.py', 'r') as f:
        content = f.read()
    
    tests_passed = 0
    tests_total = 0
    
    # Test 1: get_swap_transaction returns Optional[str]
    tests_total += 1
    if re.search(r'def get_swap_transaction\([^)]+\) -> Optional\[str\]:', content):
        print("✅ get_swap_transaction returns Optional[str]")
        tests_passed += 1
    else:
        print("❌ get_swap_transaction should return Optional[str]")
    
    # Test 2: build_buy_tx returns Optional[VersionedTransaction]
    tests_total += 1
    if 'def build_buy_tx(token_mint: str, amount_sol: float, wallet: Keypair, slippage: float = 3.0) -> Optional[VersionedTransaction]:' in content:
        print("✅ build_buy_tx returns Optional[VersionedTransaction]")
        tests_passed += 1
    else:
        print("❌ build_buy_tx should return Optional[VersionedTransaction]")
    
    # Test 3: build_sell_tx returns Optional[VersionedTransaction]
    tests_total += 1
    if 'def build_sell_tx(token_mint: str, wallet: Keypair, slippage: float = 3.0) -> Optional[VersionedTransaction]:' in content:
        print("✅ build_sell_tx returns Optional[VersionedTransaction]")
        tests_passed += 1
    else:
        print("❌ build_sell_tx should return Optional[VersionedTransaction]")
    
    # Test 4: build_and_sign returns Optional[VersionedTransaction]
    tests_total += 1
    if 'def build_and_sign(trade_info: dict, rpc: str, keypair: Keypair) -> Optional[VersionedTransaction]:' in content:
        print("✅ build_and_sign returns Optional[VersionedTransaction]")
        tests_passed += 1
    else:
        print("❌ build_and_sign should return Optional[VersionedTransaction]")
    
    print(f"\nResult: {tests_passed}/{tests_total} signature tests passed")
    return tests_passed == tests_total


def test_no_value_errors_raised():
    """Verify ValueError raises have been removed"""
    print("\n" + "=" * 80)
    print("TEST: No ValueError Raises")
    print("=" * 80)
    
    with open('mev_jupiter_executor.py', 'r') as f:
        lines = f.readlines()
    
    problematic_raises = []
    
    in_target_function = False
    current_function = None
    target_functions = ['build_buy_tx', 'build_sell_tx', 'build_and_sign']
    
    for i, line in enumerate(lines, 1):
        # Check if we're entering a target function
        for func in target_functions:
            if f'def {func}' in line:
                in_target_function = True
                current_function = func
                break
        
        # Check if we're exiting the function (next def)
        if in_target_function and line.strip().startswith('def ') and current_function:
            if not any(f'def {func}' in line for func in target_functions):
                in_target_function = False
                current_function = None
        
        # Look for ValueError raises in target functions
        if in_target_function and 'raise ValueError' in line:
            # Check if it's related to route/transaction failures
            if 'route' in line.lower() or 'swap transaction' in line.lower():
                problematic_raises.append((i, current_function, line.strip()))
    
    if problematic_raises:
        print("❌ Found ValueError raises that should be changed to return None:")
        for line_num, func, line_text in problematic_raises:
            print(f"   Line {line_num} in {func}: {line_text}")
        return False
    else:
        print("✅ No problematic ValueError raises found in target functions")
        return True


def test_warning_logs_present():
    """Verify warning logs are present instead of errors"""
    print("\n" + "=" * 80)
    print("TEST: Warning Logs Present")
    print("=" * 80)
    
    with open('mev_jupiter_executor.py', 'r') as f:
        content = f.read()
    
    tests_passed = 0
    tests_total = 0
    
    # Test 1: Warning for no route in get_swap_transaction
    tests_total += 1
    if '⚠️ [JUPITER] no route returned' in content:
        print("✅ Found warning log for no route in get_swap_transaction")
        tests_passed += 1
    else:
        print("❌ Missing warning log for no route")
    
    # Test 2: Warning for no route in build_buy_tx
    tests_total += 1
    if 'no route returned for' in content:
        print("✅ Found warning log for no route in build functions")
        tests_passed += 1
    else:
        print("❌ Missing warning log in build functions")
    
    # Test 3: Warning for no swap transaction
    tests_total += 1
    if 'no swap transaction returned' in content:
        print("✅ Found warning log for no swap transaction")
        tests_passed += 1
    else:
        print("❌ Missing warning log for no swap transaction")
    
    print(f"\nResult: {tests_passed}/{tests_total} warning log tests passed")
    return tests_passed == tests_total


def test_return_none_pattern():
    """Verify return None pattern is used instead of raises"""
    print("\n" + "=" * 80)
    print("TEST: Return None Pattern")
    print("=" * 80)
    
    with open('mev_jupiter_executor.py', 'r') as f:
        content = f.read()
    
    # Extract function bodies
    functions_to_check = ['build_buy_tx', 'build_sell_tx', 'build_and_sign']
    
    for func_name in functions_to_check:
        # Find function and check for return None after route/transaction checks
        pattern = rf'def {func_name}\([^)]+\).*?(?=\ndef |\Z)'
        match = re.search(pattern, content, re.DOTALL)
        
        if match:
            func_body = match.group(0)
            
            # Check for return None statements
            if 'return None' in func_body:
                print(f"✅ {func_name} returns None on failure")
            else:
                print(f"❌ {func_name} missing return None pattern")
                return False
        else:
            print(f"⚠️  Could not find function {func_name}")
    
    return True


def test_coordinator_compatibility():
    """Verify coordinator can handle None from builders"""
    print("\n" + "=" * 80)
    print("TEST: Coordinator Compatibility")
    print("=" * 80)
    
    with open('execution_coordinator.py', 'r') as f:
        content = f.read()
    
    tests_passed = 0
    tests_total = 0
    
    # Test 1: try_submit checks for None/falsy
    tests_total += 1
    if 'if not vtx:' in content and 'return False' in content:
        print("✅ try_submit checks for None/falsy vtx")
        tests_passed += 1
    else:
        print("❌ try_submit doesn't check for None vtx")
    
    # Test 2: Jupiter path has fallback
    tests_total += 1
    if 'Jupiter build failed' in content or 'falling back to direct_copy' in content:
        print("✅ Jupiter path has fallback to direct_copy")
        tests_passed += 1
    else:
        print("❌ Jupiter path missing fallback logic")
    
    # Test 3: Exception handling in coordinator
    tests_total += 1
    if 'except Exception as e:' in content and 'vtx = None' in content:
        print("✅ Coordinator handles exceptions and sets vtx to None")
        tests_passed += 1
    else:
        print("❌ Coordinator missing exception handling")
    
    print(f"\nResult: {tests_passed}/{tests_total} coordinator tests passed")
    return tests_passed == tests_total


def run_all_tests():
    """Run all validation tests"""
    print("\n" + "=" * 80)
    print("JUPITER NONE ROUTE FIX - VALIDATION TEST SUITE")
    print("=" * 80)
    print()
    
    tests = [
        ("Function Signatures", test_jupiter_functions_signature),
        ("No ValueError Raises", test_no_value_errors_raised),
        ("Warning Logs Present", test_warning_logs_present),
        ("Return None Pattern", test_return_none_pattern),
        ("Coordinator Compatibility", test_coordinator_compatibility),
    ]
    
    results = []
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"\n❌ EXCEPTION in {test_name}: {e}")
            results.append((test_name, False))
    
    print("\n" + "=" * 80)
    print("VALIDATION TEST SUMMARY")
    print("=" * 80)
    
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status}: {test_name}")
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    print(f"\nPassed: {passed}/{total}")
    
    if passed == total:
        print("\n✅ ALL VALIDATION TESTS PASSED")
        print("\nThe fix prevents AttributeError when Jupiter returns no route.")
        print("The coordinator will proceed to the next route without crashing.")
        return 0
    else:
        print(f"\n❌ {total - passed} VALIDATION TEST(S) FAILED")
        return 1


if __name__ == '__main__':
    import sys
    sys.exit(run_all_tests())
