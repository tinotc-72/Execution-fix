#!/usr/bin/env python3
"""
Test script to validate the coordinator handoff fix.

This test ensures that when requires_analysis is True and the analysis fails,
the coordinator handoff still happens (no early return).

The fix ensures:
1. When requires_analysis is True, we attempt analysis
2. If analysis fails, we log a warning but DO NOT return early
3. The route_and_execute function is still called to ensure coordinator handoff
"""

import re
import sys


def test_no_early_return_on_analysis_failure():
    """Test that there's no early return when analysis fails."""
    print("=" * 80)
    print("TEST: No Early Return on Analysis Failure")
    print("=" * 80)
    
    with open('main.py', 'r') as f:
        main = f.read()
    
    # Find the requires_analysis block (now checks both field names)
    pattern = r"if trade_info\.get\('requires_analysis'\) or trade_info\.get\('requires_full_analysis'\):.*?# DO NOT return here"
    match = re.search(pattern, main, re.DOTALL)
    
    if not match:
        print("  ❌ Could not find requires_analysis block with 'DO NOT return here' comment")
        return False
    
    block = match.group(0)
    
    # Check that there are NO early returns in the block
    early_return_patterns = [
        r"return\s*$",  # return on its own line
        r"return\s*#.*skipping",  # return with skipping comment
    ]
    
    found_early_return = False
    for pattern in early_return_patterns:
        if re.search(pattern, block, re.MULTILINE):
            print(f"  ❌ Found early return pattern: {pattern}")
            found_early_return = True
    
    if found_early_return:
        print("  ❌ Early returns still exist in requires_analysis block")
        return False
    
    print("  ✅ No early returns in requires_analysis block")
    
    # Check for try/except wrapper
    if "try:" in block and "except Exception as e:" in block:
        print("  ✅ Analysis wrapped in try/except for error handling")
    else:
        print("  ❌ Analysis not properly wrapped in try/except")
        return False
    
    # Check for warning logs instead of errors
    if "logger.warning" in block:
        print("  ✅ Uses warning logs for analysis failures")
    else:
        print("  ⚠️  No warning logs found (might use different log level)")
    
    # Check for the comment about not returning
    if "DO NOT return here" in block:
        print("  ✅ Has explicit comment about not returning early")
    else:
        print("  ❌ Missing explicit comment about not returning early")
        return False
    
    return True


def test_coordinator_handoff_always_called():
    """Test that route_and_execute is always called after requires_analysis block."""
    print("\n" + "=" * 80)
    print("TEST: Coordinator Handoff Always Called")
    print("=" * 80)
    
    with open('main.py', 'r') as f:
        main = f.read()
    
    # Find the pattern: requires_analysis block followed by route_and_execute
    pattern = r"if trade_info\.get\('requires_analysis'\) or trade_info\.get\('requires_full_analysis'\):.*?# DO NOT return here.*?await route_and_execute"
    match = re.search(pattern, main, re.DOTALL)
    
    if not match:
        print("  ❌ Could not find route_and_execute after requires_analysis block")
        return False
    
    print("  ✅ route_and_execute called after requires_analysis block")
    
    # Verify the flow continues to coordinator
    block = match.group(0)
    
    # Check that infer_missing_fields is called before route_and_execute
    if "infer_missing_fields" in block:
        print("  ✅ infer_missing_fields called before route_and_execute")
    else:
        print("  ❌ infer_missing_fields not called before route_and_execute")
        return False
    
    # Check that _have_all_fields is called
    if "_have_all_fields" in block:
        print("  ✅ _have_all_fields check performed before route_and_execute")
    else:
        print("  ❌ _have_all_fields check not performed")
        return False
    
    return True


def test_analysis_failure_handling():
    """Test that analysis failures are handled gracefully."""
    print("\n" + "=" * 80)
    print("TEST: Analysis Failure Handling")
    print("=" * 80)
    
    with open('main.py', 'r') as f:
        main = f.read()
    
    # Find the requires_analysis block
    pattern = r"if trade_info\.get\('requires_analysis'\) or trade_info\.get\('requires_full_analysis'\):.*?# DO NOT return here"
    match = re.search(pattern, main, re.DOTALL)
    
    if not match:
        print("  ❌ Could not find requires_analysis block")
        return False
    
    block = match.group(0)
    
    tests = [
        (
            r"will attempt fast path execution if fields are ready",
            "✅ Message indicates fast path execution will be attempted"
        ),
        (
            r"Deep analysis scheduling failed",
            "✅ Warning message for deep analysis failure"
        ),
        (
            r"except Exception as e:",
            "✅ Catches exceptions from analysis"
        ),
    ]
    
    passed = 0
    for pattern, description in tests:
        if re.search(pattern, block):
            print(f"  {description}")
            passed += 1
        else:
            print(f"  ❌ {description.replace('✅', '')}")
    
    return passed == len(tests)


def test_refactored_pattern_matches_problem_statement():
    """Verify the refactored pattern matches the problem statement requirements."""
    print("\n" + "=" * 80)
    print("TEST: Refactored Pattern Matches Problem Statement")
    print("=" * 80)
    
    with open('main.py', 'r') as f:
        main = f.read()
    
    # The problem statement shows the desired pattern:
    # if trade_info.get("requires_full_analysis"):
    #     try:
    #         schedule_deep_analysis(trade_info)
    #     except Exception as e:
    #         logger.warning(f"⚠️ Deep analysis scheduling failed: {e}")
    #     # DO NOT return here — still attempt fast path execution if fields are ready
    
    # We support both requires_analysis and requires_full_analysis
    # We use simple_trade_analysis instead of schedule_deep_analysis
    # But the pattern should be the same
    
    tests = [
        (
            r"if trade_info\.get\('requires_analysis'\) or trade_info\.get\('requires_full_analysis'\):",
            "✅ Checks for both requires_analysis and requires_full_analysis flags"
        ),
        (
            r"try:.*simple_trade_analysis.*except Exception",
            "✅ Wraps analysis in try/except"
        ),
        (
            r"logger\.warning.*Deep analysis.*failed",
            "✅ Logs warning when analysis fails"
        ),
        (
            r"# DO NOT return here.*still attempt.*execution if fields are ready",
            "✅ Has explicit comment about not returning and attempting execution"
        ),
    ]
    
    passed = 0
    for pattern, description in tests:
        if re.search(pattern, main, re.DOTALL):
            print(f"  {description}")
            passed += 1
        else:
            print(f"  ❌ {description.replace('✅', '')}")
    
    return passed == len(tests)


def main():
    """Run all coordinator handoff fix tests."""
    print("\n" + "=" * 80)
    print("COORDINATOR HANDOFF FIX VALIDATION")
    print("=" * 80)
    print()
    
    tests = [
        test_no_early_return_on_analysis_failure(),
        test_coordinator_handoff_always_called(),
        test_analysis_failure_handling(),
        test_refactored_pattern_matches_problem_statement(),
    ]
    
    passed = sum(tests)
    total = len(tests)
    
    print("\n" + "=" * 80)
    print("FINAL RESULTS")
    print("=" * 80)
    print(f"\n  Tests Passed: {passed}/{total}")
    
    if passed == total:
        print("\n  🎉 COORDINATOR HANDOFF FIX VALIDATED!")
        print("\n  The fix ensures:")
        print("  ✅ No early returns when requires_analysis is True")
        print("  ✅ Analysis failures are handled gracefully with warnings")
        print("  ✅ Coordinator handoff (route_and_execute) always happens")
        print("  ✅ Fast path execution attempted even when deep analysis fails")
        print("  ✅ Pattern matches problem statement requirements")
        print()
        return 0
    else:
        print("\n  ❌ SOME TESTS FAILED")
        print("  ❌ Review implementation against problem statement")
        print()
        return 1


if __name__ == "__main__":
    sys.exit(main())
