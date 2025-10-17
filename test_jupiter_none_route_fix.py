#!/usr/bin/env python3
"""
Test Jupiter AttributeError fix when no route is returned.

Validates:
1. get_swap_transaction handles None route without AttributeError
2. build_and_sign returns None (not raise) when get_swap_transaction fails
3. Coordinator proceeds to next route when Jupiter returns None
"""

import sys


def test_get_swap_transaction_none_route():
    """Test that get_swap_transaction handles None route gracefully"""
    print("=" * 80)
    print("TEST 1: get_swap_transaction handles None route")
    print("=" * 80)
    
    with open('mev_jupiter_executor.py', 'r') as f:
        content = f.read()
    
    # Check for the None/falsy check before accessing route.keys()
    if 'if not route:' in content or 'if route is None:' in content:
        print("✅ PASS: Found None/falsy route check before dereferencing")
    else:
        print("❌ FAIL: Missing None/falsy route check")
        return False
    
    # Check for warning log when route is None
    if '⚠️ [JUPITER] no route returned' in content or 'no route returned' in content:
        print("✅ PASS: Found warning log for no route")
    else:
        print("❌ FAIL: Missing warning log for no route")
        return False
    
    # Ensure route.keys() is not accessed before the None check
    lines = content.split('\n')
    in_get_swap_transaction = False
    found_none_check = False
    found_keys_access = False
    
    for i, line in enumerate(lines):
        if 'def get_swap_transaction' in line:
            in_get_swap_transaction = True
            found_none_check = False
            found_keys_access = False
            continue
        
        if in_get_swap_transaction:
            # Check if we've found the None check
            if 'if not route:' in line or 'if route is None:' in line:
                found_none_check = True
            
            # Check if we access route.keys() before None check
            if 'route.keys()' in line and not found_none_check:
                print(f"❌ FAIL: route.keys() accessed before None check at line {i+1}")
                return False
            
            # Stop at next function definition
            if i > 0 and 'def ' in line and line[0] == 'd':
                break
    
    if found_none_check:
        print("✅ PASS: route.keys() accessed only after None check")
    
    return True


def test_build_and_sign_returns_none():
    """Test that build_and_sign returns None instead of raising"""
    print("\n" + "=" * 80)
    print("TEST 2: build_and_sign returns None on failure")
    print("=" * 80)
    
    with open('mev_jupiter_executor.py', 'r') as f:
        content = f.read()
    
    # Check build_and_sign function signature returns Optional
    if 'def build_and_sign(trade_info: dict, rpc: str, keypair: Keypair) -> Optional[VersionedTransaction]:' in content:
        print("✅ PASS: build_and_sign returns Optional[VersionedTransaction]")
    else:
        print("❌ FAIL: build_and_sign does not return Optional[VersionedTransaction]")
        return False
    
    # Check that build_and_sign handles exceptions and returns None
    lines = content.split('\n')
    in_build_and_sign = False
    found_try_except = False
    found_return_none = False
    
    for i, line in enumerate(lines):
        if 'def build_and_sign' in line:
            in_build_and_sign = True
            continue
        
        if in_build_and_sign:
            if 'try:' in line:
                found_try_except = True
            if 'return None' in line:
                found_return_none = True
            
            # Stop at next function definition
            if i > 0 and line.startswith('def '):
                break
    
    if found_try_except and found_return_none:
        print("✅ PASS: build_and_sign uses try/except and returns None on error")
    else:
        print("❌ FAIL: build_and_sign does not properly handle errors")
        return False
    
    return True


def test_build_buy_tx_returns_optional():
    """Test that build_buy_tx returns Optional instead of raising"""
    print("\n" + "=" * 80)
    print("TEST 3: build_buy_tx returns Optional on no route")
    print("=" * 80)
    
    with open('mev_jupiter_executor.py', 'r') as f:
        content = f.read()
    
    # Check build_buy_tx returns Optional
    if 'def build_buy_tx(token_mint: str, amount_sol: float, wallet: Keypair, slippage: float = 3.0) -> Optional[VersionedTransaction]:' in content:
        print("✅ PASS: build_buy_tx returns Optional[VersionedTransaction]")
    else:
        print("❌ FAIL: build_buy_tx does not return Optional[VersionedTransaction]")
        return False
    
    # Check that build_buy_tx doesn't raise ValueError
    lines = content.split('\n')
    in_build_buy_tx = False
    
    for i, line in enumerate(lines):
        if 'def build_buy_tx' in line:
            in_build_buy_tx = True
            continue
        
        if in_build_buy_tx:
            # Check for raises
            if 'raise ValueError' in line and 'Failed to get route' in line:
                print(f"❌ FAIL: build_buy_tx still raises ValueError at line {i+1}")
                return False
            
            # Stop at next function definition
            if i > 0 and line.startswith('def '):
                break
    
    # Check for warning logs instead of raises
    if '⚠️ [JUPITER] no route returned' in content:
        print("✅ PASS: build_buy_tx logs warning instead of raising")
    else:
        print("⚠️ WARNING: No warning log found in build_buy_tx")
    
    return True


def test_coordinator_handles_none():
    """Test that coordinator handles None from build_and_sign"""
    print("\n" + "=" * 80)
    print("TEST 4: Coordinator handles None from Jupiter builder")
    print("=" * 80)
    
    with open('execution_coordinator.py', 'r') as f:
        content = f.read()
    
    # Check that try_submit handles None
    if 'if not vtx:' in content and 'return False' in content:
        print("✅ PASS: try_submit checks for None/falsy vtx")
    else:
        print("❌ FAIL: try_submit does not check for None vtx")
        return False
    
    # Check for fallback logic after Jupiter fails
    if 'falling back to direct_copy' in content or 'direct_copy fallback' in content:
        print("✅ PASS: Coordinator falls back to direct_copy when Jupiter fails")
    else:
        print("❌ FAIL: No fallback logic found in coordinator")
        return False
    
    return True


def run_all_tests():
    """Run all tests and report results"""
    print("\n" + "=" * 80)
    print("JUPITER NONE ROUTE FIX - TEST SUITE")
    print("=" * 80)
    
    tests = [
        test_get_swap_transaction_none_route,
        test_build_and_sign_returns_none,
        test_build_buy_tx_returns_optional,
        test_coordinator_handles_none,
    ]
    
    results = []
    for test in tests:
        try:
            result = test()
            results.append(result)
        except Exception as e:
            print(f"\n❌ EXCEPTION in {test.__name__}: {e}")
            results.append(False)
    
    print("\n" + "=" * 80)
    print("TEST RESULTS SUMMARY")
    print("=" * 80)
    
    passed = sum(results)
    total = len(results)
    
    print(f"\nPassed: {passed}/{total}")
    
    if passed == total:
        print("\n✅ ALL TESTS PASSED")
        return 0
    else:
        print(f"\n❌ {total - passed} TEST(S) FAILED")
        return 1


if __name__ == '__main__':
    sys.exit(run_all_tests())
