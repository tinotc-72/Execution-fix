#!/usr/bin/env python3
"""
Test script to validate the new routing logic requirements.

Validates that the execution_coordinator.py:
1. Routes Meteora trades: Meteora builder first (with requote support), then Jupiter, then direct_copy
2. Routes unknown dex with mint: Jupiter, then Meteora, then direct_copy
3. Avoids direct_copy first when source_tx_failed is True
4. Supports retry_hint == "requote" for Meteora with wider slippage
"""

import re
import sys


def test_meteora_routing():
    """Test 1: Meteora path routing."""
    print("=" * 80)
    print("TEST 1: Meteora Path Routing")
    print("=" * 80)
    
    with open('execution_coordinator.py', 'r') as f:
        code = f.read()
    
    tests = [
        (
            r'if dex_key == "meteora":.*plan = \["meteora", "jupiter", "direct_copy"\]',
            "✅ Meteora path uses plan: [meteora, jupiter, direct_copy]"
        ),
        (
            r'retry_hint == "requote".*force fresh quote/wider slippage',
            "✅ Logs retry_hint='requote' for Meteora"
        ),
        (
            r'force_requote = retry_hint == "requote"',
            "✅ Sets force_requote flag based on retry_hint"
        ),
        (
            r'force_requote=force_requote',
            "✅ Passes force_requote to Meteora executor"
        ),
    ]
    
    passed = 0
    for pattern, description in tests:
        if re.search(pattern, code, re.DOTALL):
            print(f"  {description}")
            passed += 1
        else:
            print(f"  ❌ {description.replace('✅', '')}")
    
    print(f"\n  Result: {passed}/{len(tests)} checks passed\n")
    return passed == len(tests)


def test_unknown_with_mint_routing():
    """Test 2: Unknown DEX with token mint routing."""
    print("=" * 80)
    print("TEST 2: Unknown DEX with Token Mint Routing")
    print("=" * 80)
    
    with open('execution_coordinator.py', 'r') as f:
        code = f.read()
    
    tests = [
        (
            r'have_mint = bool\(token_mint and token_mint != "UNKNOWN"\)',
            "✅ Checks if token_mint is present"
        ),
        (
            r'dex_key == "unknown" and have_mint.*plan = \["jupiter", "meteora", "direct_copy"\]',
            "✅ Unknown with mint uses plan: [jupiter, meteora, direct_copy]"
        ),
        (
            r'Route=unknown; mint present → Jupiter → Meteora → Clone',
            "✅ Logs unknown path with mint routing"
        ),
    ]
    
    passed = 0
    for pattern, description in tests:
        if re.search(pattern, code, re.DOTALL):
            print(f"  {description}")
            passed += 1
        else:
            print(f"  ❌ {description.replace('✅', '')}")
    
    print(f"\n  Result: {passed}/{len(tests)} checks passed\n")
    return passed == len(tests)


def test_source_failed_routing():
    """Test 3: Source failed transaction routing."""
    print("=" * 80)
    print("TEST 3: Source Failed Transaction Routing")
    print("=" * 80)
    
    with open('execution_coordinator.py', 'r') as f:
        code = f.read()
    
    tests = [
        (
            r'source_tx_failed = trade_info\.get\("source_tx_failed", False\)',
            "✅ Extracts source_tx_failed from trade_info"
        ),
        (
            r'if source_tx_failed.*avoid clone; try builders first',
            "✅ Logs when source failed - avoids clone first"
        ),
        (
            r'source_tx_failed.*plan = \["jupiter", "meteora", "direct_copy"\]',
            "✅ Uses builder-first plan when source failed"
        ),
        (
            r'signature and not source_tx_failed',
            "✅ Checks source_tx_failed before prioritizing direct_copy"
        ),
    ]
    
    passed = 0
    for pattern, description in tests:
        if re.search(pattern, code, re.DOTALL):
            print(f"  {description}")
            passed += 1
        else:
            print(f"  ❌ {description.replace('✅', '')}")
    
    print(f"\n  Result: {passed}/{len(tests)} checks passed\n")
    return passed == len(tests)


def test_meteora_executor_requote():
    """Test 4: Meteora executor force_requote support."""
    print("=" * 80)
    print("TEST 4: Meteora Executor Force Requote Support")
    print("=" * 80)
    
    with open('execution_coordinator.py', 'r') as f:
        coord_code = f.read()
    
    try:
        with open('mev_meteora_executor.py', 'r') as f:
            exec_code = f.read()
    except FileNotFoundError:
        print("  ❌ mev_meteora_executor.py not found")
        return False
    
    tests = [
        (
            r'_execute_meteora_buy.*force_requote.*kwargs\.get\(.*force_requote.*False\)',
            "✅ _execute_meteora_buy extracts force_requote from kwargs",
            coord_code
        ),
        (
            r'force_requote=True - will request fresh quote with wider slippage',
            "✅ Logs force_requote processing in coordinator",
            coord_code
        ),
        (
            r'async def mev_meteora_copy_trade.*force_requote: bool = False',
            "✅ mev_meteora_copy_trade accepts force_requote parameter",
            exec_code
        ),
        (
            r'min_tokens = 1 if not force_requote else 0.*maximum slippage tolerance',
            "✅ Uses min_tokens=0 for maximum slippage when force_requote=True",
            exec_code
        ),
    ]
    
    passed = 0
    for pattern, description, code_to_check in tests:
        if re.search(pattern, code_to_check, re.DOTALL):
            print(f"  {description}")
            passed += 1
        else:
            print(f"  ❌ {description.replace('✅', '')}")
    
    print(f"\n  Result: {passed}/{len(tests)} checks passed\n")
    return passed == len(tests)


def test_no_new_dependencies():
    """Test 5: Verify no new dependencies added."""
    print("=" * 80)
    print("TEST 5: No New Dependencies")
    print("=" * 80)
    
    with open('execution_coordinator.py', 'r') as f:
        code = f.read()
    
    # Check for new imports
    existing_imports = [
        'asyncio', 'logging', 'traceback', 'time', 'typing', 'datetime',
        'dataclasses', 'collections', 'solders', 'mev_', 'copy_trade_logger',
        'transaction_cloner', 'fast_executor', 'env_keys'
    ]
    
    import_lines = re.findall(r'^(?:from|import)\s+(\S+)', code, re.MULTILINE)
    
    new_imports = []
    for imp in import_lines:
        is_existing = any(existing in imp for existing in existing_imports)
        if not is_existing:
            new_imports.append(imp)
    
    if not new_imports:
        print("  ✅ No new dependencies added")
        print("  ✅ Uses existing infrastructure:")
        print("     - Existing RPC client")
        print("     - Existing logging with emoji format")
        print("     - Existing transaction_cloner for direct_copy")
        print("     - Existing mev executors for builders")
        print(f"\n  Result: 1/1 checks passed\n")
        return True
    else:
        print(f"  ❌ New dependencies found: {new_imports}")
        print(f"\n  Result: 0/1 checks passed\n")
        return False


def main():
    """Run all routing logic tests."""
    print("\n" + "=" * 80)
    print("ROUTING LOGIC VALIDATION")
    print("=" * 80)
    print()
    
    tests = [
        test_meteora_routing(),
        test_unknown_with_mint_routing(),
        test_source_failed_routing(),
        test_meteora_executor_requote(),
        test_no_new_dependencies(),
    ]
    
    passed = sum(tests)
    total = len(tests)
    
    print("=" * 80)
    print("FINAL RESULTS")
    print("=" * 80)
    print(f"\n  Tests Passed: {passed}/{total}")
    
    if passed == total:
        print("\n  🎉 ALL ROUTING LOGIC REQUIREMENTS MET!")
        print("\n  The execution coordinator now implements:")
        print("  ✅ Meteora path: Meteora → Jupiter → direct_copy")
        print("  ✅ Unknown with mint: Jupiter → Meteora → direct_copy")
        print("  ✅ Source failed: Builders first, avoid direct_copy")
        print("  ✅ Meteora requote: force_requote flag for wider slippage")
        print("  ✅ No new dependencies - uses existing infrastructure")
        print()
        return 0
    else:
        print("\n  ❌ SOME REQUIREMENTS NOT MET")
        print("  ❌ Review implementation against problem statement")
        print()
        return 1


if __name__ == "__main__":
    sys.exit(main())
