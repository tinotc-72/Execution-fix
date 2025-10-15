#!/usr/bin/env python3
"""
Test suite for route_and_execute implementation.

Validates that:
1. route_and_execute function exists
2. Function has the correct signature
3. Hard guard validation logic is implemented
4. Emoji logging is present
5. Function is called after infer_missing_fields
"""

import sys


def test_route_and_execute_exists():
    """Test that route_and_execute function exists in main.py"""
    print("=" * 80)
    print("TEST 1: route_and_execute Function Exists")
    print("=" * 80)
    
    with open('main.py', 'r') as f:
        content = f.read()
    
    if 'async def route_and_execute(' in content or 'def route_and_execute(' in content:
        print("✅ PASS: route_and_execute function exists")
        return True
    else:
        print("❌ FAIL: route_and_execute function not found")
        return False


def test_function_signature():
    """Test that route_and_execute has correct signature"""
    print("=" * 80)
    print("TEST 2: Function Signature")
    print("=" * 80)
    
    with open('main.py', 'r') as f:
        content = f.read()
    
    checks = [
        ('async def route_and_execute(trade_info: dict, rpc, keypair, jito=None):', '✅ Correct async function signature'),
        ('def route_and_execute(trade_info: dict, rpc, keypair, jito=None):', '✅ Correct function signature (sync)'),
    ]
    
    for pattern, description in checks:
        if pattern in content:
            print(f"  {description}")
            return True
    
    print("  ❌ Function signature doesn't match expected pattern")
    return False


def test_hard_guard_logic():
    """Test that hard guard validation logic is implemented"""
    print("=" * 80)
    print("TEST 3: Hard Guard Validation Logic")
    print("=" * 80)
    
    with open('main.py', 'r') as f:
        content = f.read()
    
    checks = [
        ('required_ok = all(trade_info.get(k) not in (None, "", "unknown", "PENDING_ANALYSIS")', '✅ Hard guard check implemented'),
        ('for k in ("dex", "action", "wallet_address", "token_mint")', '✅ Checks all required fields'),
        ('if not required_ok:', '✅ Validation conditional present'),
    ]
    
    passed = 0
    for pattern, description in checks:
        if pattern in content:
            print(f"  {description}")
            passed += 1
        else:
            print(f"  ❌ {description.replace('✅', '')} - NOT FOUND")
    
    print(f"\n  Result: {passed}/{len(checks)} checks passed\n")
    return passed == len(checks)


def test_emoji_logging():
    """Test that emoji logging is present"""
    print("=" * 80)
    print("TEST 4: Emoji Logging")
    print("=" * 80)
    
    with open('main.py', 'r') as f:
        content = f.read()
    
    checks = [
        ('logger.warning("🛑 [PIPELINE_EXIT] Fields incomplete, skipping execution")', '✅ Warning log with emoji'),
        ('logger.info("🧭 [PIPELINE_EXIT] Final fields ready → handoff to coordinator")', '✅ Info log with emoji'),
    ]
    
    passed = 0
    for pattern, description in checks:
        if pattern in content:
            print(f"  {description}")
            passed += 1
        else:
            print(f"  ❌ {description.replace('✅', '')} - NOT FOUND")
    
    print(f"\n  Result: {passed}/{len(checks)} checks passed\n")
    return passed == len(checks)


def test_maybe_execute_call():
    """Test that maybe_execute is called correctly"""
    print("=" * 80)
    print("TEST 5: maybe_execute Call")
    print("=" * 80)
    
    with open('main.py', 'r') as f:
        content = f.read()
    
    checks = [
        ('await maybe_execute(', '✅ Calls maybe_execute with await'),
        ('maybe_execute(trade_info,', '✅ Passes trade_info'),
    ]
    
    passed = 0
    for pattern, description in checks:
        if pattern in content:
            print(f"  {description}")
            passed += 1
        else:
            print(f"  ❌ {description.replace('✅', '')} - NOT FOUND")
    
    print(f"\n  Result: {passed}/{len(checks)} checks passed\n")
    return passed == len(checks)


def test_called_after_inference():
    """Test that route_and_execute is called after infer_missing_fields"""
    print("=" * 80)
    print("TEST 6: Called After infer_missing_fields")
    print("=" * 80)
    
    with open('main.py', 'r') as f:
        lines = f.readlines()
    
    # Find the debug log line
    debug_log_line = -1
    route_and_execute_line = -1
    
    for i, line in enumerate(lines):
        if 'After infer_missing_fields' in line and 'logger.debug' in line:
            debug_log_line = i
        if 'await route_and_execute(' in line:
            route_and_execute_line = i
    
    if debug_log_line == -1:
        print("  ❌ 'After infer_missing_fields' debug log not found")
        return False
    
    if route_and_execute_line == -1:
        print("  ❌ route_and_execute call not found")
        return False
    
    # Check that route_and_execute is called within a few lines after the debug log
    if route_and_execute_line > debug_log_line and route_and_execute_line - debug_log_line <= 5:
        print(f"  ✅ route_and_execute called after 'After infer_missing_fields' debug log")
        print(f"     Debug log at line {debug_log_line + 1}")
        print(f"     route_and_execute at line {route_and_execute_line + 1}")
        return True
    else:
        print(f"  ❌ route_and_execute not called immediately after debug log")
        print(f"     Debug log at line {debug_log_line + 1}")
        print(f"     route_and_execute at line {route_and_execute_line + 1}")
        return False


def test_import_maybe_execute():
    """Test that maybe_execute is imported from execution_coordinator"""
    print("=" * 80)
    print("TEST 7: maybe_execute Import")
    print("=" * 80)
    
    with open('main.py', 'r') as f:
        content = f.read()
    
    if 'from execution_coordinator import' in content and 'maybe_execute' in content:
        print("  ✅ maybe_execute imported from execution_coordinator")
        return True
    else:
        print("  ❌ maybe_execute import not found")
        return False


def main():
    """Run all tests"""
    print("\n" + "=" * 80)
    print("ROUTE_AND_EXECUTE IMPLEMENTATION VALIDATION")
    print("=" * 80 + "\n")
    
    tests = [
        ("route_and_execute exists", test_route_and_execute_exists),
        ("Function signature", test_function_signature),
        ("Hard guard logic", test_hard_guard_logic),
        ("Emoji logging", test_emoji_logging),
        ("maybe_execute call", test_maybe_execute_call),
        ("Called after inference", test_called_after_inference),
        ("maybe_execute import", test_import_maybe_execute),
    ]
    
    results = []
    for name, test_func in tests:
        try:
            passed = test_func()
            results.append((name, passed))
        except Exception as e:
            print(f"  ❌ Test failed with exception: {e}")
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
        print("  The route_and_execute implementation is complete:")
        print("  ✅ Function exists with correct signature")
        print("  ✅ Hard guard validation implemented")
        print("  ✅ Emoji logging present")
        print("  ✅ Calls maybe_execute correctly")
        print("  ✅ Called after infer_missing_fields")
        print("  ✅ Proper import from execution_coordinator")
        return 0
    else:
        print("  ❌ SOME TESTS FAILED")
        print("  ❌ Review implementation")
        return 1


if __name__ == "__main__":
    sys.exit(main())
