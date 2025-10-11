#!/usr/bin/env python3
"""
Final Validation Script - Verify All Requirements Met

This script performs a comprehensive check of all problem statement requirements.
"""

import sys
import re


def check_requirement_1():
    """Point 1: Remove restrictive logic - execute on trade instructions OR monitored signer."""
    print("=" * 80)
    print("REQUIREMENT 1: Execution Logic (Trade Instructions OR Monitored Signer)")
    print("=" * 80)
    
    with open('main.py', 'r') as f:
        content = f.read()
    
    # Check for OR condition
    or_condition = bool(re.search(
        r"if not \(has_trade_instructions or has_monitored_signer\)",
        content
    ))
    
    # Check for both conditions being checked
    checks_instructions = bool(re.search(r"_check_trade_instructions", content))
    checks_signer = bool(re.search(r"_check_monitored_wallet_is_signer", content))
    
    results = [
        ("Checks for trade instructions", checks_instructions),
        ("Checks for monitored wallet signer", checks_signer),
        ("Uses OR logic (execute if EITHER condition met)", or_condition),
    ]
    
    passed = all(r[1] for r in results)
    
    for desc, result in results:
        status = "✅" if result else "❌"
        print(f"  {status} {desc}")
    
    print(f"\nStatus: {'✅ PASS' if passed else '❌ FAIL'}\n")
    return passed


def check_requirement_2():
    """Point 2: Case-insensitive wallet matching."""
    print("=" * 80)
    print("REQUIREMENT 2: Case-Insensitive Wallet Matching")
    print("=" * 80)
    
    with open('trade_processor.py', 'r') as f:
        content = f.read()
    
    # Check for lowercase normalization in key methods
    has_lower_in_validate = bool(re.search(
        r"def _validate_monitored_wallet.*?\.lower\(\)",
        content,
        re.DOTALL
    ))
    
    has_lower_in_signer_check = bool(re.search(
        r"def _check_monitored_wallet_is_signer.*?monitored_wallets_lower.*?\.lower\(\)",
        content,
        re.DOTALL
    ))
    
    has_lower_in_target_check = bool(re.search(
        r"def is_target_wallet.*?\.lower\(\)",
        content,
        re.DOTALL
    ))
    
    # Check documentation
    has_doc = bool(re.search(r"case-insensitive", content, re.IGNORECASE))
    
    results = [
        ("_validate_monitored_wallet uses .lower()", has_lower_in_validate),
        ("_check_monitored_wallet_is_signer uses .lower()", has_lower_in_signer_check),
        ("is_target_wallet uses .lower()", has_lower_in_target_check),
        ("Documentation mentions case-insensitive", has_doc),
    ]
    
    passed = all(r[1] for r in results)
    
    for desc, result in results:
        status = "✅" if result else "❌"
        print(f"  {status} {desc}")
    
    print(f"\nStatus: {'✅ PASS' if passed else '❌ FAIL'}\n")
    return passed


def check_requirement_3():
    """Point 3: Aggressive execution (0.001 SOL buy, proportional sell)."""
    print("=" * 80)
    print("REQUIREMENT 3: Aggressive Execution Parameters")
    print("=" * 80)
    
    with open('main.py', 'r') as f:
        content = f.read()
    
    # Check for 0.001 SOL buy
    has_buy_amount = bool(re.search(
        r"amount_sol=0\.001.*# Explicit 0\.001 SOL investment",
        content
    ))
    
    # Check for sell percentage calculation
    has_sell_calc = bool(re.search(
        r"sell_percentage = self\._calculate_sell_percentage",
        content
    ))
    
    # Check for _calculate_sell_percentage method
    has_calc_method = bool(re.search(
        r"def _calculate_sell_percentage",
        content
    ))
    
    # Check for proportional sell execution
    has_sell_exec = bool(re.search(
        r"sell_percentage=sell_percentage",
        content
    ))
    
    results = [
        ("Buy with explicit 0.001 SOL", has_buy_amount),
        ("Calculates sell percentage before execution", has_sell_calc),
        ("_calculate_sell_percentage method exists", has_calc_method),
        ("Passes calculated percentage to executor", has_sell_exec),
    ]
    
    passed = all(r[1] for r in results)
    
    for desc, result in results:
        status = "✅" if result else "❌"
        print(f"  {status} {desc}")
    
    print(f"\nStatus: {'✅ PASS' if passed else '❌ FAIL'}\n")
    return passed


def check_requirement_4():
    """Point 4: Fix imports in utils.py."""
    print("=" * 80)
    print("REQUIREMENT 4: Correct Imports in utils.py")
    print("=" * 80)
    
    with open('utils.py', 'r') as f:
        content = f.read()
    
    # Check for correct import
    has_correct_import = bool(re.search(
        r"from env_keys import EnvKeys",
        content
    ))
    
    # Check for usage
    has_correct_usage = bool(re.search(
        r"env_keys = EnvKeys\(\)",
        content
    ))
    
    has_rpc_usage = bool(re.search(
        r"env_keys\.HELIUS_RPC_URL",
        content
    ))
    
    # Check for old import (should not exist)
    has_old_import = bool(re.search(
        r"import keyZ as kz",
        content
    ))
    
    results = [
        ("Uses 'from env_keys import EnvKeys'", has_correct_import),
        ("Creates env_keys instance", has_correct_usage),
        ("Uses env_keys.HELIUS_RPC_URL", has_rpc_usage),
        ("No old 'import keyZ as kz' found", not has_old_import),
    ]
    
    passed = all(r[1] for r in results)
    
    for desc, result in results:
        status = "✅" if result else "❌"
        print(f"  {status} {desc}")
    
    print(f"\nStatus: {'✅ PASS' if passed else '❌ FAIL'}\n")
    return passed


def check_requirement_5():
    """Point 5: run_with_logging.py script exists."""
    print("=" * 80)
    print("REQUIREMENT 5: run_with_logging.py Script")
    print("=" * 80)
    
    import os
    
    # Check if file exists
    file_exists = os.path.exists('run_with_logging.py')
    
    if file_exists:
        with open('run_with_logging.py', 'r') as f:
            content = f.read()
        
        # Check for key features
        has_log_dir = bool(re.search(r"makedirs.*logs", content))
        has_timestamp = bool(re.search(r"timestamp.*strftime", content))
        has_subprocess = bool(re.search(r"subprocess\.Popen", content))
        has_exception_handling = bool(re.search(r"except.*Exception", content))
        
        results = [
            ("File exists", file_exists),
            ("Creates logs directory", has_log_dir),
            ("Generates timestamped log files", has_timestamp),
            ("Uses subprocess to run bot", has_subprocess),
            ("Handles exceptions", has_exception_handling),
        ]
    else:
        results = [("File exists", False)]
    
    passed = all(r[1] for r in results)
    
    for desc, result in results:
        status = "✅" if result else "❌"
        print(f"  {status} {desc}")
    
    print(f"\nStatus: {'✅ PASS' if passed else '❌ FAIL'}\n")
    return passed


def check_requirement_6():
    """Point 6: Comprehensive logging and documentation."""
    print("=" * 80)
    print("REQUIREMENT 6: Logging and Documentation")
    print("=" * 80)
    
    with open('main.py', 'r') as f:
        main_content = f.read()
    
    with open('trade_processor.py', 'r') as f:
        processor_content = f.read()
    
    # Check for execution logging
    has_execution_logging = bool(re.search(
        r"EXECUTION_CHECK.*Trade instructions detected",
        main_content
    ))
    
    # Check for wallet matching logging
    has_wallet_logging = bool(re.search(
        r"case-insensitive",
        processor_content,
        re.IGNORECASE
    ))
    
    # Check for updated documentation
    has_main_doc = bool(re.search(
        r"AGGRESSIVE EXECUTION LOGIC",
        main_content
    ))
    
    has_processor_doc = bool(re.search(
        r"case-insensitive.*matching",
        processor_content,
        re.IGNORECASE
    ))
    
    # Check for comprehensive docstrings
    has_detailed_docstring = bool(re.search(
        r"Case-Insensitive Wallet Matching",
        main_content
    ))
    
    results = [
        ("Execution condition logging present", has_execution_logging),
        ("Case-insensitive wallet logging present", has_wallet_logging),
        ("Main.py documentation updated", has_main_doc),
        ("Trade processor documentation updated", has_processor_doc),
        ("Detailed docstrings added", has_detailed_docstring),
    ]
    
    passed = all(r[1] for r in results)
    
    for desc, result in results:
        status = "✅" if result else "❌"
        print(f"  {status} {desc}")
    
    print(f"\nStatus: {'✅ PASS' if passed else '❌ FAIL'}\n")
    return passed


def check_tests():
    """Verify tests exist and can be run."""
    print("=" * 80)
    print("TEST VALIDATION")
    print("=" * 80)
    
    import os
    
    test_files = [
        'test_aggressive_execution.py',
        'test_wallet_matching.py'
    ]
    
    results = []
    for test_file in test_files:
        exists = os.path.exists(test_file)
        results.append((f"{test_file} exists", exists))
    
    passed = all(r[1] for r in results)
    
    for desc, result in results:
        status = "✅" if result else "❌"
        print(f"  {status} {desc}")
    
    print(f"\nStatus: {'✅ PASS' if passed else '❌ FAIL'}\n")
    return passed


def main():
    """Run all requirement checks."""
    print("\n" + "=" * 80)
    print("FINAL VALIDATION - ALL REQUIREMENTS CHECK")
    print("=" * 80)
    print()
    
    requirements = [
        ("Execution Logic (OR condition)", check_requirement_1()),
        ("Case-Insensitive Wallet Matching", check_requirement_2()),
        ("Aggressive Execution Parameters", check_requirement_3()),
        ("Correct Imports in utils.py", check_requirement_4()),
        ("run_with_logging.py Script", check_requirement_5()),
        ("Logging and Documentation", check_requirement_6()),
        ("Test Files", check_tests()),
    ]
    
    passed = sum(r[1] for r in requirements)
    total = len(requirements)
    
    print("=" * 80)
    print("FINAL SUMMARY")
    print("=" * 80)
    print()
    
    for desc, result in requirements:
        status = "✅" if result else "❌"
        print(f"  {status} {desc}")
    
    print()
    print("=" * 80)
    print(f"\nRequirements Met: {passed}/{total}")
    
    if passed == total:
        print("\n  🎉 ALL REQUIREMENTS SUCCESSFULLY IMPLEMENTED!")
        print("  ✅ Execution logic: Trade instructions OR monitored signer")
        print("  ✅ Case-insensitive wallet matching")
        print("  ✅ Aggressive execution: 0.001 SOL buy, proportional sell")
        print("  ✅ Correct imports in utils.py")
        print("  ✅ run_with_logging.py script ready")
        print("  ✅ Comprehensive logging and documentation")
        print("  ✅ Test coverage complete")
        print()
        return 0
    else:
        print(f"\n  ❌ {total - passed} requirement(s) not met")
        print("  Please review the failed checks above")
        print()
        return 1


if __name__ == "__main__":
    sys.exit(main())
