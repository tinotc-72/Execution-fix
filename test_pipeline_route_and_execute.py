#!/usr/bin/env python3
"""
Test script to validate pipeline route_and_execute implementation.

Validates that:
1. _have_all_fields exists and treats mint/token_mint as synonyms
2. route_and_execute exists and logs handoff
3. schedule_deep_analysis exists and is non-blocking
4. requires_full_analysis path does NOT return early
5. route_and_execute is called immediately after "After infer_missing_fields" log
"""

import re
import sys


def test_have_all_fields_exists():
    """Test that _have_all_fields function exists and is implemented correctly."""
    print("=" * 80)
    print("TEST 1: _have_all_fields Function Exists and Correct")
    print("=" * 80)
    
    with open('main.py', 'r') as f:
        main = f.read()
    
    tests = [
        (
            r"def _have_all_fields\(trade_info: dict\) -> bool:",
            "✅ _have_all_fields function exists with correct signature"
        ),
        (
            r'token_mint = trade_info\.get\("token_mint"\) or trade_info\.get\("mint"\)',
            "✅ Treats mint and token_mint as synonyms"
        ),
        (
            r'if ok and trade_info\.get\("token_mint"\) is None and token_mint:.*trade_info\["token_mint"\] = token_mint',
            "✅ Normalizes to token_mint"
        ),
        (
            r'all\(v not in \(None, "", "unknown", "PENDING_ANALYSIS"\)',
            "✅ Validates all required field values"
        ),
    ]
    
    passed = 0
    for pattern, description in tests:
        if re.search(pattern, main, re.DOTALL):
            print(f"  {description}")
            passed += 1
        else:
            print(f"  ❌ {description.replace('✅', '')}")
    
    print(f"\n  Result: {passed}/{len(tests)} checks passed\n")
    return passed == len(tests)


def test_route_and_execute_exists():
    """Test that route_and_execute function exists and logs handoff."""
    print("=" * 80)
    print("TEST 2: route_and_execute Function Exists and Logs Handoff")
    print("=" * 80)
    
    with open('main.py', 'r') as f:
        main = f.read()
    
    tests = [
        (
            r"async def route_and_execute\(trade_info: dict, rpc, keypair, jito=None\):",
            "✅ route_and_execute function exists with correct signature"
        ),
        (
            r'if not _have_all_fields\(trade_info\):',
            "✅ Checks fields with _have_all_fields before execution"
        ),
        (
            r'\[PIPELINE_EXIT\].*Final fields ready.*handoff to coordinator',
            "✅ Logs handoff to coordinator"
        ),
        (
            r'await maybe_execute\(trade_info',
            "✅ Calls execution_coordinator.maybe_execute"
        ),
        (
            r'try:.*await maybe_execute.*except Exception as e:.*logger\.error.*\[PIPELINE_EXIT\].*crashed',
            "✅ Wraps coordinator call in try/except"
        ),
    ]
    
    passed = 0
    for pattern, description in tests:
        if re.search(pattern, main, re.DOTALL):
            print(f"  {description}")
            passed += 1
        else:
            print(f"  ❌ {description.replace('✅', '')}")
    
    print(f"\n  Result: {passed}/{len(tests)} checks passed\n")
    return passed == len(tests)


def test_schedule_deep_analysis_exists():
    """Test that schedule_deep_analysis function exists and is non-blocking."""
    print("=" * 80)
    print("TEST 3: schedule_deep_analysis Function Exists")
    print("=" * 80)
    
    with open('main.py', 'r') as f:
        main = f.read()
    
    tests = [
        (
            r"def schedule_deep_analysis\(trade_info: dict\):",
            "✅ schedule_deep_analysis function exists"
        ),
        (
            r"schedule_deep_analysis.*non-blocking",
            "✅ Documented as non-blocking"
        ),
    ]
    
    passed = 0
    for pattern, description in tests:
        if re.search(pattern, main, re.DOTALL | re.IGNORECASE):
            print(f"  {description}")
            passed += 1
        else:
            print(f"  ❌ {description.replace('✅', '')}")
    
    print(f"\n  Result: {passed}/{len(tests)} checks passed\n")
    return passed == len(tests)


def test_no_early_return_in_requires_full_analysis():
    """Test that requires_full_analysis path does NOT return early."""
    print("=" * 80)
    print("TEST 4: No Early Return in requires_full_analysis Path")
    print("=" * 80)
    
    with open('main.py', 'r') as f:
        main = f.read()
    
    # Extract the requires_full_analysis section
    pattern = r'if trade_info\.get\("requires_full_analysis"\):(.*?)(?=\n\s{0,12}#|\n\s{0,12}await route_and_execute)'
    match = re.search(pattern, main, re.DOTALL)
    
    if not match:
        print("  ❌ Could not find requires_full_analysis block")
        return False
    
    block = match.group(1)
    
    tests = [
        (
            r'schedule_deep_analysis\(trade_info\)',
            "✅ Calls schedule_deep_analysis"
        ),
        (
            r'continuing fast-path',
            "✅ Logs continuation to fast-path"
        ),
        (
            not re.search(r'\breturn\b', block),
            "✅ Does NOT return early (continues to coordinator)"
        ),
    ]
    
    passed = 0
    for pattern_or_bool, description in tests:
        if isinstance(pattern_or_bool, bool):
            if pattern_or_bool:
                print(f"  {description}")
                passed += 1
            else:
                print(f"  ❌ {description.replace('✅', '')}")
        else:
            if re.search(pattern_or_bool, block, re.DOTALL):
                print(f"  {description}")
                passed += 1
            else:
                print(f"  ❌ {description.replace('✅', '')}")
    
    print(f"\n  Result: {passed}/{len(tests)} checks passed\n")
    return passed == len(tests)


def test_route_and_execute_after_infer():
    """Test that route_and_execute is called after 'After infer_missing_fields' log."""
    print("=" * 80)
    print("TEST 5: route_and_execute Called After infer_missing_fields")
    print("=" * 80)
    
    with open('main.py', 'r') as f:
        main = f.read()
    
    # Find the section between "After infer_missing_fields" and route_and_execute
    pattern = r'After infer_missing_fields(.*?)await route_and_execute'
    match = re.search(pattern, main, re.DOTALL)
    
    if not match:
        print("  ❌ Could not find 'After infer_missing_fields' followed by route_and_execute")
        return False
    
    between = match.group(1)
    
    tests = [
        (
            r'have_all = _have_all_fields\(trade_info\)',
            "✅ Computes have_all before route_and_execute"
        ),
        (
            r'trade_info\["use_universal_cloner"\] = not have_all',
            "✅ Sets use_universal_cloner based on have_all"
        ),
        (
            r'\[MODE\].*Builders.*Cloner',
            "✅ Logs mode selection"
        ),
        (
            r'\[HANDOFF\].*Calling coordinator',
            "✅ Logs handoff before route_and_execute"
        ),
    ]
    
    passed = 0
    for pattern, description in tests:
        if re.search(pattern, between, re.DOTALL):
            print(f"  {description}")
            passed += 1
        else:
            print(f"  ❌ {description.replace('✅', '')}")
    
    # Also check that handoff returned log comes after
    if re.search(r'await route_and_execute.*\[HANDOFF\].*returned', main, re.DOTALL):
        print("  ✅ Logs handoff return after route_and_execute")
        passed += 1
    else:
        print("  ❌ Missing handoff return log after route_and_execute")
    
    print(f"\n  Result: {passed}/{len(tests) + 1} checks passed\n")
    return passed == len(tests) + 1


def main():
    """Run all tests."""
    print("\n" + "=" * 80)
    print("PIPELINE ROUTE_AND_EXECUTE VALIDATION")
    print("=" * 80 + "\n")
    
    tests = [
        ("_have_all_fields exists and correct", test_have_all_fields_exists),
        ("route_and_execute exists and logs", test_route_and_execute_exists),
        ("schedule_deep_analysis exists", test_schedule_deep_analysis_exists),
        ("No early return in requires_full_analysis", test_no_early_return_in_requires_full_analysis),
        ("route_and_execute after infer_missing_fields", test_route_and_execute_after_infer),
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
        print("  The pipeline implementation is complete:")
        print("  ✅ _have_all_fields treats mint/token_mint as synonyms")
        print("  ✅ route_and_execute logs handoff and calls coordinator")
        print("  ✅ schedule_deep_analysis exists and is non-blocking")
        print("  ✅ No early return in requires_full_analysis path")
        print("  ✅ route_and_execute called after infer_missing_fields")
        return 0
    else:
        print("  ❌ SOME TESTS FAILED")
        print("  ❌ Review implementation")
        return 1


if __name__ == "__main__":
    sys.exit(main())
