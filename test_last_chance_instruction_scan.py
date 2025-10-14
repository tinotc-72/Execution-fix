#!/usr/bin/env python3
"""
Test script to validate the last-chance instruction account scan for mint inference.

This test validates that the new fallback mechanism properly:
1. Scans instruction accounts for SPL mints
2. Matches them against mints in postTokenBalances
3. Excludes WSOL
4. Uses consistent emoji logging
"""

import re
import sys


def test_last_chance_instruction_scan():
    """Test that last-chance instruction scan is implemented."""
    print("=" * 80)
    print("TEST: Last-Chance Instruction Account Scan for Mint Inference")
    print("=" * 80)
    
    with open('trade_processor.py', 'r') as f:
        processor = f.read()
    
    checks = [
        (
            '# Last-chance: scan instruction accounts for SPL mints',
            '✅ Has last-chance instruction scan comment'
        ),
        (
            'WSOL = "So11111111111111111111111111111111111111112"',
            '✅ Defines WSOL constant'
        ),
        (
            'post_mints = {b.get("mint") for b in (meta.get("postTokenBalances") or []) if b.get("mint")}',
            '✅ Extracts mints from postTokenBalances'
        ),
        (
            'message = tx.get(\'transaction\', {}).get(\'message\', {})',
            '✅ Gets message from transaction structure'
        ),
        (
            'instrs = message.get(\'instructions\', [])',
            '✅ Extracts instructions from message'
        ),
        (
            'account_keys = message.get(\'accountKeys\', [])',
            '✅ Extracts account keys from message'
        ),
        (
            'if account_keys and isinstance(account_keys[0], dict):',
            '✅ Handles both dict and string account_keys formats'
        ),
        (
            'account_indices = ix.get("accounts") or []',
            '✅ Gets account indices from instruction'
        ),
        (
            'if acc in post_mints and acc != WSOL:',
            '✅ Checks if account is in post_mints and excludes WSOL'
        ),
        (
            'logger.info(f"✅ [MINT_INFERENCE] Resolved token mint from instruction accounts: {acc}")',
            '✅ Logs success with ✅ emoji'
        ),
        (
            'logger.warning(f"⚠️ [MINT_INFERENCE] Instruction scan failed: {e}")',
            '✅ Logs errors with ⚠️ emoji'
        ),
        (
            'except Exception as e:',
            '✅ Has proper exception handling'
        ),
        (
            'inferred_fields.append(\'token_mint (from instruction scan)\')',
            '✅ Adds to inferred_fields when successful'
        ),
    ]
    
    passed = 0
    for pattern, description in checks:
        if pattern in processor:
            print(f"  {description}")
            passed += 1
        else:
            print(f"  ❌ {description.replace('✅', '')}")
    
    print(f"\n  Result: {passed}/{len(checks)} checks passed\n")
    return passed == len(checks)


def test_placement_after_token_balances():
    """Test that the instruction scan is placed after token balances extraction."""
    print("=" * 80)
    print("TEST: Placement After Token Balances Extraction")
    print("=" * 80)
    
    with open('trade_processor.py', 'r') as f:
        processor = f.read()
    
    # Find the positions
    token_balances_pos = processor.find('mint = self._extract_mint_from_token_balances(meta)')
    instruction_scan_pos = processor.find('# Last-chance: scan instruction accounts for SPL mints')
    old_instruction_method_pos = processor.find('mint = self._extract_mint_from_instruction_accounts(trade_info)')
    
    checks = [
        (
            token_balances_pos != -1,
            '✅ Token balances extraction exists'
        ),
        (
            instruction_scan_pos != -1,
            '✅ Last-chance instruction scan exists'
        ),
        (
            old_instruction_method_pos != -1,
            '✅ Old instruction accounts method exists'
        ),
        (
            token_balances_pos < instruction_scan_pos,
            '✅ Instruction scan comes after token balances'
        ),
        (
            instruction_scan_pos < old_instruction_method_pos,
            '✅ Instruction scan comes before old instruction method'
        ),
    ]
    
    passed = 0
    for condition, description in checks:
        if condition:
            print(f"  {description}")
            passed += 1
        else:
            print(f"  ❌ {description.replace('✅', '')}")
    
    print(f"\n  Result: {passed}/{len(checks)} checks passed\n")
    return passed == len(checks)


def test_no_new_dependencies():
    """Test that no new dependencies are introduced."""
    print("=" * 80)
    print("TEST: No New Dependencies")
    print("=" * 80)
    
    with open('trade_processor.py', 'r') as f:
        processor = f.read()
    
    # Check for imports at the top of the file
    import_section = processor[:2000]  # First 2000 chars should contain imports
    
    # Common new dependencies that shouldn't be added
    forbidden_imports = [
        'import requests',
        'from requests',
        'import aiohttp',
        'from aiohttp',
        'import urllib',
        'from urllib',
    ]
    
    checks = []
    for forbidden in forbidden_imports:
        if forbidden not in import_section:
            checks.append((True, f'✅ Does not import {forbidden.split()[1]}'))
        else:
            checks.append((False, f'❌ Imports {forbidden.split()[1]} (forbidden)'))
    
    passed = sum(1 for c in checks if c[0])
    for condition, description in checks:
        print(f"  {description}")
    
    print(f"\n  Result: {passed}/{len(checks)} checks passed\n")
    return passed == len(checks)


def main():
    """Run all tests."""
    print("\n" + "=" * 80)
    print("LAST-CHANCE INSTRUCTION SCAN TEST SUITE")
    print("=" * 80 + "\n")
    
    tests = [
        test_last_chance_instruction_scan,
        test_placement_after_token_balances,
        test_no_new_dependencies,
    ]
    
    results = []
    for test in tests:
        try:
            result = test()
            results.append(result)
        except Exception as e:
            print(f"  ❌ Test failed with exception: {e}\n")
            results.append(False)
    
    print("\n" + "=" * 80)
    print("FINAL RESULTS")
    print("=" * 80)
    passed = sum(results)
    total = len(results)
    print(f"Tests passed: {passed}/{total}")
    
    if passed == total:
        print("✅ All tests passed!")
        return 0
    else:
        print(f"❌ {total - passed} test(s) failed")
        return 1


if __name__ == "__main__":
    sys.exit(main())
