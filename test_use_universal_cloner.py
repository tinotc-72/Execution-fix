#!/usr/bin/env python3
"""
Test suite for use_universal_cloner flag handling in maybe_execute function.
Validates the logic from the problem statement.
"""

import sys
import re


def test_prefer_clone_variable():
    """Test that prefer_clone variable is extracted from use_universal_cloner"""
    print("=" * 80)
    print("TEST 1: prefer_clone Variable Extraction")
    print("=" * 80)
    
    with open('execution_coordinator.py', 'r') as f:
        content = f.read()
    
    # Extract maybe_execute function
    maybe_execute_match = re.search(
        r'async def maybe_execute.*?(?=\n(?:async def|def|class|@dataclass|\Z))', 
        content, 
        re.DOTALL
    )
    if not maybe_execute_match:
        print("  ❌ Could not find maybe_execute function")
        return False
    
    maybe_execute_content = maybe_execute_match.group(0)
    
    checks = [
        (r'prefer_clone = bool\(trade_info\.get\("use_universal_cloner"\)\)', 
         "Extracts prefer_clone from use_universal_cloner"),
        (r'if not prefer_clone:', "Checks if prefer_clone is False"),
        (r'if have_mint:', "Checks if have_mint when prefer_clone is True"),
    ]
    
    passed = 0
    for pattern, description in checks:
        if re.search(pattern, maybe_execute_content):
            print(f"  ✅ {description}")
            passed += 1
        else:
            print(f"  ❌ {description}")
    
    print(f"\n  Result: {passed}/{len(checks)} checks passed")
    return passed == len(checks)


def test_meteora_with_prefer_clone_false():
    """Test meteora route when use_universal_cloner=False"""
    print("\n" + "=" * 80)
    print("TEST 2: Meteora Route - use_universal_cloner=False")
    print("=" * 80)
    
    with open('execution_coordinator.py', 'r') as f:
        content = f.read()
    
    # Extract the meteora routing logic
    meteora_match = re.search(
        r'if dex == "meteora":.*?(?=\n    # Route 2:|if dex == "unknown")', 
        content, 
        re.DOTALL
    )
    if not meteora_match:
        print("  ❌ Could not find meteora routing logic")
        return False
    
    meteora_content = meteora_match.group(0)
    
    checks = [
        (r'if not prefer_clone:', "Has 'if not prefer_clone' branch"),
        (r'meteora_build_and_sign', "Tries meteora_build_and_sign first"),
        (r'jupiter_build_buy_tx', "Tries jupiter_build_buy_tx as fallback"),
        (r'execute_direct_copy_fallback', "Tries direct_copy as final fallback"),
        (r'⚠️ Meteora build failed — trying Jupiter', "Logs Jupiter fallback"),
        (r'⚠️ Builders failed — falling back to direct_copy', "Logs direct_copy fallback"),
    ]
    
    passed = 0
    for pattern, description in checks:
        if re.search(pattern, meteora_content):
            print(f"  ✅ {description}")
            passed += 1
        else:
            print(f"  ❌ {description}")
    
    print(f"\n  Result: {passed}/{len(checks)} checks passed")
    return passed == len(checks)


def test_meteora_with_prefer_clone_true():
    """Test meteora route when use_universal_cloner=True"""
    print("\n" + "=" * 80)
    print("TEST 3: Meteora Route - use_universal_cloner=True")
    print("=" * 80)
    
    with open('execution_coordinator.py', 'r') as f:
        content = f.read()
    
    # Extract the meteora routing logic
    meteora_match = re.search(
        r'if dex == "meteora":.*?(?=\n    # Route 2:|if dex == "unknown")', 
        content, 
        re.DOTALL
    )
    if not meteora_match:
        print("  ❌ Could not find meteora routing logic")
        return False
    
    meteora_content = meteora_match.group(0)
    
    checks = [
        (r'else:.*?# Prefer clone', "Has 'else' branch for prefer_clone=True"),
        (r'if have_mint:.*?meteora_build_and_sign', "Tries meteora if mint exists"),
        (r'return await execute_direct_copy_fallback\(\)', "Falls back to clone"),
    ]
    
    passed = 0
    for pattern, description in checks:
        if re.search(pattern, meteora_content, re.DOTALL):
            print(f"  ✅ {description}")
            passed += 1
        else:
            print(f"  ❌ {description}")
    
    print(f"\n  Result: {passed}/{len(checks)} checks passed")
    return passed == len(checks)


def test_unknown_route_no_meteora():
    """Test that unknown route doesn't use Meteora"""
    print("\n" + "=" * 80)
    print("TEST 4: Unknown Route - No Meteora")
    print("=" * 80)
    
    with open('execution_coordinator.py', 'r') as f:
        content = f.read()
    
    # Extract the unknown routing logic - include the full block until the next route
    unknown_match = re.search(
        r'# Route 2: dex == "unknown".*?if dex == "unknown" and have_mint:.*?(?=\n    # Unknown & no mint|\Z)', 
        content, 
        re.DOTALL
    )
    if not unknown_match:
        print("  ❌ Could not find unknown routing logic")
        return False
    
    unknown_content = unknown_match.group(0)
    
    # Check that meteora is NOT in the unknown path
    has_meteora = 'meteora_build_and_sign' in unknown_content
    has_jupiter = 'jupiter_build_buy_tx' in unknown_content
    has_direct_copy = 'execute_direct_copy_fallback' in unknown_content
    has_correct_log = '🧭 [COORDINATOR] Route=unknown; mint present → Jupiter → Clone' in unknown_content
    
    results = [
        (not has_meteora, "Does NOT try meteora_build_and_sign"),
        (has_jupiter, "Tries jupiter_build_buy_tx"),
        (has_direct_copy, "Falls back to direct_copy"),
        (has_correct_log, "Logs correct route message"),
    ]
    
    passed = 0
    for result, description in results:
        if result:
            print(f"  ✅ {description}")
            passed += 1
        else:
            print(f"  ❌ {description}")
    
    print(f"\n  Result: {passed}/{len(results)} checks passed")
    return passed == len(results)


def test_docstring_updated():
    """Test that docstring reflects new logic"""
    print("\n" + "=" * 80)
    print("TEST 5: Docstring Updated")
    print("=" * 80)
    
    with open('execution_coordinator.py', 'r') as f:
        content = f.read()
    
    # Extract docstring
    docstring_match = re.search(
        r'async def maybe_execute.*?""".*?"""', 
        content, 
        re.DOTALL
    )
    if not docstring_match:
        print("  ❌ Could not find docstring")
        return False
    
    docstring = docstring_match.group(0)
    
    checks = [
        ('use_universal_cloner=False' in docstring, "Mentions use_universal_cloner=False"),
        ('use_universal_cloner=True' in docstring, "Mentions use_universal_cloner=True"),
        ('try builders if mint exists' in docstring or 'Try builders if mint exists' in docstring, 
         "Mentions trying builders if mint exists"),
    ]
    
    passed = 0
    for check, description in checks:
        if check:
            print(f"  ✅ {description}")
            passed += 1
        else:
            print(f"  ❌ {description}")
    
    print(f"\n  Result: {passed}/{len(checks)} checks passed")
    return passed == len(checks)


def main():
    """Run all tests"""
    print("\n🚀 Testing use_universal_cloner Flag Implementation")
    print("=" * 80)
    
    tests = [
        ("prefer_clone Variable", test_prefer_clone_variable),
        ("Meteora - prefer_clone=False", test_meteora_with_prefer_clone_false),
        ("Meteora - prefer_clone=True", test_meteora_with_prefer_clone_true),
        ("Unknown Route - No Meteora", test_unknown_route_no_meteora),
        ("Docstring Updated", test_docstring_updated),
    ]
    
    results = []
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"\n❌ Test '{test_name}' failed with exception: {e}")
            import traceback
            traceback.print_exc()
            results.append((test_name, False))
    
    # Summary
    print("\n" + "=" * 80)
    print("TEST SUMMARY")
    print("=" * 80)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"  {status}: {test_name}")
    
    print(f"\n  Total: {passed}/{total} tests passed")
    
    if passed == total:
        print("\n  🎉 ALL TESTS PASSED!")
        print("\n  The use_universal_cloner flag logic implements:")
        print("  ✅ Extracts prefer_clone from use_universal_cloner")
        print("  ✅ Meteora + prefer_clone=False: try meteora → jupiter → clone")
        print("  ✅ Meteora + prefer_clone=True: try meteora if mint exists, else clone")
        print("  ✅ Unknown + mint: try jupiter → clone (NO meteora)")
        print("  ✅ Docstring reflects new logic")
        return 0
    else:
        print(f"\n  ❌ {total - passed} test(s) failed")
        return 1


if __name__ == "__main__":
    sys.exit(main())
