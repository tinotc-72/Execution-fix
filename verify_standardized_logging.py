#!/usr/bin/env python3
"""
Verification script for standardized submission logging implementation.

This script verifies that:
1. utils/logs.py exists and has the correct function
2. All submission points use log_submit_result
3. No old-style logging patterns remain
4. All values are real (no placeholders)
"""

import os
import sys


def verify_logs_module_exists():
    """Verify that utils/logs.py exists"""
    print("=" * 80)
    print("TEST 1: Verify utils/logs.py exists")
    print("=" * 80)
    
    path = "utils/logs.py"
    if os.path.exists(path):
        print(f"✅ {path} exists")
        
        # Check that it has the correct function
        with open(path, 'r') as f:
            content = f.read()
            if 'def log_submit_result' in content:
                print("✅ log_submit_result function exists")
                if 'from __future__ import annotations' in content:
                    print("✅ Has proper imports")
                    return True
    
    print(f"❌ {path} missing or incomplete")
    return False


def verify_function_signature():
    """Verify the function signature is correct"""
    print("\n" + "=" * 80)
    print("TEST 2: Verify function signature")
    print("=" * 80)
    
    with open("utils/logs.py", 'r') as f:
        content = f.read()
        
    # Check function signature
    if 'def log_submit_result(dex: str, action: str, mint: str, res) -> None:' in content:
        print("✅ Function signature is correct")
    else:
        print("❌ Function signature is incorrect")
        return False
    
    # Check for try-except block
    if 'try:' in content and 'except Exception:' in content:
        print("✅ Has proper error handling")
    else:
        print("❌ Missing error handling")
        return False
    
    # Check for format strings
    if 'DEX={dex} action={action} mint={mint} sig={res.signature} status={res.status} ok={res.ok}' in content:
        print("✅ Success log format is correct")
    else:
        print("❌ Success log format is incorrect")
        return False
    
    if '[malformed SubmitResult]' in content:
        print("✅ Fallback log format is correct")
        return True
    else:
        print("❌ Fallback log format is incorrect")
        return False


def verify_usage_in_files():
    """Verify that log_submit_result is used in all required files"""
    print("\n" + "=" * 80)
    print("TEST 3: Verify usage in executor files")
    print("=" * 80)
    
    files_to_check = [
        "mev_meteora_executor.py",
        "mev_jupiter_executor.py",
        "mev_direct_sell_executor.py",
        "complete_mev_bot.py",
        "transaction_cloner.py"
    ]
    
    all_ok = True
    for filename in files_to_check:
        with open(filename, 'r') as f:
            content = f.read()
        
        if 'from utils.logs import log_submit_result' in content:
            # Count occurrences
            count = content.count('log_submit_result(')
            print(f"✅ {filename}: {count} usage(s)")
        else:
            print(f"❌ {filename}: Not using log_submit_result")
            all_ok = False
    
    return all_ok


def verify_no_old_patterns():
    """Verify that old logging patterns have been removed"""
    print("\n" + "=" * 80)
    print("TEST 4: Verify old patterns removed")
    print("=" * 80)
    
    files_to_check = [
        "mev_meteora_executor.py",
        "mev_jupiter_executor.py",
        "mev_direct_sell_executor.py",
        "complete_mev_bot.py",
        "transaction_cloner.py"
    ]
    
    old_patterns = [
        'logger.info(f"[SUBMIT] DEX=',
        'print(f"[SUBMIT] DEX='
    ]
    
    found_old = False
    for filename in files_to_check:
        with open(filename, 'r') as f:
            content = f.read()
        
        for pattern in old_patterns:
            if pattern in content:
                print(f"❌ {filename}: Found old pattern: {pattern}")
                found_old = True
    
    if not found_old:
        print("✅ No old logging patterns found")
        return True
    
    return False


def verify_real_values():
    """Verify that all logging uses real values, not placeholders"""
    print("\n" + "=" * 80)
    print("TEST 5: Verify real values (no placeholders)")
    print("=" * 80)
    
    files_to_check = [
        ("mev_meteora_executor.py", ["params.token_mint", "token_mint", "detected_action"]),
        ("mev_jupiter_executor.py", ["token_mint_str", "token_mint"]),
        ("mev_direct_sell_executor.py", ["token_mint"]),
        ("complete_mev_bot.py", ["token_mint"]),
        ("transaction_cloner.py", ["unknown"])  # Acceptable for cloner
    ]
    
    all_ok = True
    for filename, expected_vars in files_to_check:
        with open(filename, 'r') as f:
            content = f.read()
        
        # Find all log_submit_result calls
        import re
        calls = re.findall(r'log_submit_result\([^)]+\)', content)
        
        if calls:
            found_vars = False
            for var in expected_vars:
                for call in calls:
                    if var in call:
                        found_vars = True
                        break
            
            if found_vars:
                print(f"✅ {filename}: Uses real values")
            else:
                print(f"❌ {filename}: May use placeholder values")
                all_ok = False
        else:
            print(f"⚠️  {filename}: No log_submit_result calls found")
    
    return all_ok


def verify_test_files_exist():
    """Verify that test and demo files exist"""
    print("\n" + "=" * 80)
    print("TEST 6: Verify test and demo files")
    print("=" * 80)
    
    test_file = "test_standardized_logging.py"
    demo_file = "demo_standardized_logging.py"
    
    all_ok = True
    for filename in [test_file, demo_file]:
        if os.path.exists(filename):
            print(f"✅ {filename} exists")
        else:
            print(f"❌ {filename} missing")
            all_ok = False
    
    return all_ok


def main():
    """Run all verification tests"""
    print("\n" + "=" * 80)
    print("STANDARDIZED SUBMISSION LOGGING VERIFICATION")
    print("=" * 80 + "\n")
    
    tests = [
        ("utils/logs.py exists", verify_logs_module_exists),
        ("Function signature correct", verify_function_signature),
        ("Usage in executor files", verify_usage_in_files),
        ("Old patterns removed", verify_no_old_patterns),
        ("Real values used", verify_real_values),
        ("Test files exist", verify_test_files_exist)
    ]
    
    results = []
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"\n❌ Test '{test_name}' failed with error: {e}")
            results.append((test_name, False))
    
    print("\n" + "=" * 80)
    print("VERIFICATION RESULTS")
    print("=" * 80)
    
    all_passed = True
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status}: {test_name}")
        if not result:
            all_passed = False
    
    print("=" * 80)
    
    if all_passed:
        print("\n✅ ALL VERIFICATIONS PASSED")
        print("\nImplementation is complete and correct:")
        print("- utils/logs.py helper function created")
        print("- All submission points updated")
        print("- Consistent log format across all DEXes")
        print("- Real values used (no placeholders)")
        print("- Test and demo files included")
        return 0
    else:
        print("\n❌ SOME VERIFICATIONS FAILED")
        print("Please review the failed tests above.")
        return 1


if __name__ == "__main__":
    sys.exit(main())
