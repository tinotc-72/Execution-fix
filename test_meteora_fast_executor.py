#!/usr/bin/env python3
"""
Test for Meteora FastExecutor integration.

Validates that:
1. MEVMeteoraExecutor accepts FastExecutor in __init__
2. No bundle parsing (result.get("success"), result.get("signature"))
3. Uses FastExecutor.send_and_confirm for submissions
4. Returns proper MeteoraTradeResult
"""

import re

def test_init_accepts_fast_executor():
    """Test that MEVMeteoraExecutor.__init__ accepts fast_executor parameter"""
    print("=" * 80)
    print("TEST: MEVMeteoraExecutor.__init__ accepts FastExecutor")
    print("=" * 80)
    
    with open('mev_meteora_executor.py', 'r') as f:
        code = f.read()
    
    tests = [
        (
            r'def __init__\(self, wallet_keypair: Keypair, rpc_client: SimpleRPC, fast_executor=None\):',
            '✅ __init__ accepts fast_executor parameter'
        ),
        (
            r'self\.fast_executor = fast_executor',
            '✅ Stores fast_executor as instance variable'
        ),
        (
            r'logger\..*FastExecutor available:',
            '✅ Logs FastExecutor availability'
        ),
    ]
    
    passed = 0
    for pattern, description in tests:
        if re.search(pattern, code):
            print(f"  {description}")
            passed += 1
        else:
            print(f"  ❌ {description.replace('✅', '')} - NOT FOUND")
    
    print(f"\n  Result: {passed}/{len(tests)} checks passed\n")
    return passed == len(tests)

def test_no_bundle_parsing():
    """Test that bundle parsing is removed"""
    print("=" * 80)
    print("TEST: No Bundle Parsing (result.get)")
    print("=" * 80)
    
    with open('mev_meteora_executor.py', 'r') as f:
        code = f.read()
    
    # Check for bundle parsing patterns that should be removed
    bad_patterns = [
        (r'result\.get\("success"\)', 'Bundle parsing: result.get("success")'),
        (r'result\.get\("signature"\)', 'Bundle parsing: result.get("signature") in _execute methods'),
        (r'_execute_with_jito.*result\.get', 'Bundle parsing in _execute_with_jito'),
        (r'_execute_standard.*result\.get', 'Bundle parsing in _execute_standard'),
    ]
    
    found_issues = 0
    for pattern, description in bad_patterns:
        # Exclude the definitions of exec_ok and exec_err helpers (those are OK)
        matches = re.finditer(pattern, code, re.DOTALL)
        for match in matches:
            context = code[max(0, match.start()-200):min(len(code), match.end()+200)]
            # Skip if it's in the helper function definitions or mev_meteora_copy_trade (being updated separately)
            if 'def exec_ok' not in context and 'def exec_err' not in context:
                print(f"  ❌ Found {description}")
                found_issues += 1
    
    if found_issues == 0:
        print("  ✅ No bundle parsing patterns found")
        print(f"\n  Result: PASS\n")
        return True
    else:
        print(f"\n  Result: FAIL ({found_issues} issues found)\n")
        return False

def test_uses_fast_executor_send_and_confirm():
    """Test that code uses FastExecutor.send_and_confirm"""
    print("=" * 80)
    print("TEST: Uses FastExecutor.send_and_confirm")
    print("=" * 80)
    
    with open('mev_meteora_executor.py', 'r') as f:
        code = f.read()
    
    tests = [
        (
            r'async def _execute_via_fast_executor\(self, vtx: VersionedTransaction\)',
            '✅ Has _execute_via_fast_executor method accepting VersionedTransaction'
        ),
        (
            r'self\.fast_executor\.send_and_confirm\(vtx\)',
            '✅ Calls fast_executor.send_and_confirm(vtx)'
        ),
        (
            r'if not sig:.*return MeteoraTradeResult\(success=False, error="submit failed \(Jito\+RPC\)"\)',
            '✅ Returns error with message "submit failed (Jito+RPC)" on failure'
        ),
        (
            r'return MeteoraTradeResult\(.*success=True.*signature=sig',
            '✅ Returns MeteoraTradeResult(success=True, signature=sig) on success'
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

def test_execute_buy_uses_fast_executor():
    """Test that execute_buy method uses FastExecutor"""
    print("=" * 80)
    print("TEST: execute_buy Uses FastExecutor")
    print("=" * 80)
    
    with open('mev_meteora_executor.py', 'r') as f:
        code = f.read()
    
    # Find execute_buy method
    execute_buy_match = re.search(r'async def execute_buy\(.*?\n(?:.*?\n)*?^    async def ', code, re.MULTILINE)
    if not execute_buy_match:
        # Try to find it without the next method
        execute_buy_match = re.search(r'async def execute_buy\(.*?\n(?:.*?\n)*?(?=^    async def |^class |^def |^async def )', code, re.MULTILINE)
    
    if not execute_buy_match:
        print("  ❌ Could not find execute_buy method")
        return False
    
    execute_buy_code = execute_buy_match.group(0)
    
    tests = [
        (
            r'vtx = VersionedTransaction',
            '✅ Creates VersionedTransaction'
        ),
        (
            r'result = await self\._execute_via_fast_executor\(vtx\)',
            '✅ Calls _execute_via_fast_executor(vtx)'
        ),
        (
            r'MessageV0\.try_compile',
            '✅ Converts Transaction to VersionedTransaction using MessageV0'
        ),
    ]
    
    passed = 0
    for pattern, description in tests:
        if re.search(pattern, execute_buy_code):
            print(f"  {description}")
            passed += 1
        else:
            print(f"  ❌ {description.replace('✅', '')} - NOT FOUND")
    
    # Check that old methods are NOT used
    if 'await self._execute_with_jito' in execute_buy_code:
        print("  ❌ Still uses _execute_with_jito (should be removed)")
    elif 'await self._execute_standard' in execute_buy_code:
        print("  ❌ Still uses _execute_standard (should be removed)")
    else:
        print("  ✅ Does not use old _execute_with_jito or _execute_standard methods")
        passed += 1
    
    print(f"\n  Result: {passed}/{len(tests)+1} checks passed\n")
    return passed == len(tests)+1

def test_mev_meteora_copy_trade():
    """Test that mev_meteora_copy_trade uses FastExecutor"""
    print("=" * 80)
    print("TEST: mev_meteora_copy_trade Uses FastExecutor")
    print("=" * 80)
    
    with open('mev_meteora_executor.py', 'r') as f:
        code = f.read()
    
    # Find mev_meteora_copy_trade function
    func_match = re.search(r'async def mev_meteora_copy_trade\(.*?\n(?:.*?\n)*?(?=^async def |^def |^class |\Z)', code, re.MULTILINE)
    
    if not func_match:
        print("  ❌ Could not find mev_meteora_copy_trade function")
        return False
    
    func_code = func_match.group(0)
    
    tests = [
        (
            r'sig = await fast_executor\.send_and_confirm\(vtx\)',
            '✅ Calls fast_executor.send_and_confirm(vtx)'
        ),
        (
            r'if not sig:.*return None',
            '✅ Returns None on submission failure'
        ),
        (
            r'return sig',
            '✅ Returns signature string on success'
        ),
    ]
    
    passed = 0
    for pattern, description in tests:
        if re.search(pattern, func_code, re.DOTALL):
            print(f"  {description}")
            passed += 1
        else:
            print(f"  ❌ {description.replace('✅', '')} - NOT FOUND")
    
    # Check that old bundle code is NOT used
    bad_patterns = [
        ('jito_service.send_bundle', 'Old jito_service.send_bundle call'),
        ('result.get("signature")', 'Bundle parsing: result.get("signature")'),
        ('result.get("success")', 'Bundle parsing: result.get("success")'),
        ('exec_ok("meteora"', 'Old exec_ok return value'),
        ('exec_err("meteora"', 'Old exec_err return value'),
    ]
    
    issues = 0
    for pattern, description in bad_patterns:
        if pattern in func_code:
            print(f"  ❌ Still has {description}")
            issues += 1
    
    if issues == 0:
        print("  ✅ No old bundle parsing code found")
        passed += 1
    
    print(f"\n  Result: {passed}/{len(tests)+1} checks passed\n")
    return passed == len(tests)+1

def main():
    """Run all validation tests."""
    print("\n" + "=" * 80)
    print("METEORA FASTEXECUTOR INTEGRATION TESTS")
    print("=" * 80)
    print()
    
    tests = [
        ("Init Accepts FastExecutor", test_init_accepts_fast_executor()),
        ("No Bundle Parsing", test_no_bundle_parsing()),
        ("Uses FastExecutor.send_and_confirm", test_uses_fast_executor_send_and_confirm()),
        ("execute_buy Uses FastExecutor", test_execute_buy_uses_fast_executor()),
        ("mev_meteora_copy_trade Uses FastExecutor", test_mev_meteora_copy_trade()),
    ]
    
    passed = sum(1 for _, result in tests if result)
    total = len(tests)
    
    print("=" * 80)
    print("FINAL RESULTS")
    print("=" * 80)
    print(f"\n  Tests Passed: {passed}/{total}")
    
    if passed == total:
        print("\n  🎉 ALL TESTS PASSED!")
        print("\n  Implementation verified:")
        print("  ✅ MEVMeteoraExecutor accepts FastExecutor")
        print("  ✅ No bundle parsing (result.get)")
        print("  ✅ Uses FastExecutor.send_and_confirm(vtx)")
        print("  ✅ Returns proper MeteoraTradeResult")
        print("  ✅ mev_meteora_copy_trade updated to use FastExecutor")
        print("\n" + "=" * 80)
        return 0
    else:
        print("\n  ❌ SOME TESTS FAILED")
        print("=" * 80)
        return 1

if __name__ == '__main__':
    import sys
    sys.exit(main())
