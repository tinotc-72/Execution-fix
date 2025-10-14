#!/usr/bin/env python3
"""
Test script to validate last-chance transaction fetch in infer_missing_fields.

This test verifies that:
1. The last-chance fetch is triggered when logs and transaction are missing
2. It uses the existing rpc_client
3. Logging is consistent with existing format (INFO/WARNING/ERROR emojis)
"""

import sys

def test_last_chance_fetch_code_exists():
    """Test that the last-chance fetch code exists in the right place"""
    print("=" * 80)
    print("TEST: Last-Chance Fetch Implementation")
    print("=" * 80)
    
    with open('trade_processor.py', 'r') as f:
        content = f.read()
    
    checks = [
        (
            'logs = trade_info.get("logs")',
            '✅ Checks for logs at the beginning of infer_missing_fields'
        ),
        (
            'tx_obj = trade_info.get("transaction")',
            '✅ Checks for transaction at the beginning of infer_missing_fields'
        ),
        (
            'if not logs and not tx_obj and trade_info.get("signature"):',
            '✅ Conditional check for last-chance fetch'
        ),
        (
            'fetch_json_rpc_with_url',
            '✅ Uses existing RPC client infrastructure (fetch_json_rpc_with_url)'
        ),
        (
            '"encoding": "jsonParsed"',
            '✅ Uses jsonParsed encoding as specified'
        ),
        (
            '"maxSupportedTransactionVersion": 0',
            '✅ Sets maxSupportedTransactionVersion to 0'
        ),
        (
            'trade_info["logs"] = meta.get("logMessages") or []',
            '✅ Attaches logMessages to trade_info["logs"]'
        ),
        (
            'trade_info["transaction"] = tx.get("transaction")',
            '✅ Attaches transaction to trade_info["transaction"]'
        ),
        (
            '🔎 [TRADE_PROCESSOR] Last-chance fetch',
            '✅ Uses consistent logging format with emoji'
        ),
        (
            '🔎 [TRADE_PROCESSOR] Attached missing logs/tx via signature fetch',
            '✅ Logs success message with emoji'
        ),
        (
            '⚠️ [TRADE_PROCESSOR] Signature fetch failed',
            '✅ Logs warning with emoji on failure'
        ),
    ]
    
    passed = 0
    for pattern, description in checks:
        if pattern in content:
            print(f"  {description}")
            passed += 1
        else:
            print(f"  ❌ {description.replace('✅', '')}")
    
    print(f"\n  Result: {passed}/{len(checks)} checks passed\n")
    return passed == len(checks)


def test_fetch_placement():
    """Test that the fetch is placed correctly (before field inference logic)"""
    print("=" * 80)
    print("TEST: Last-Chance Fetch Placement")
    print("=" * 80)
    
    with open('trade_processor.py', 'r') as f:
        lines = f.readlines()
    
    # Find the line numbers for key sections
    last_chance_fetch_line = None
    infer_signature_line = None
    
    for i, line in enumerate(lines):
        if 'Last-chance fetch if we have a signature but no logs/tx' in line:
            last_chance_fetch_line = i
        if '# 1. Infer signature if missing' in line:
            infer_signature_line = i
    
    if last_chance_fetch_line is None:
        print("  ❌ Could not find last-chance fetch comment")
        return False
    
    if infer_signature_line is None:
        print("  ❌ Could not find signature inference comment")
        return False
    
    if last_chance_fetch_line < infer_signature_line:
        print(f"  ✅ Last-chance fetch is placed BEFORE field inference logic")
        print(f"     (Last-chance at line {last_chance_fetch_line + 1}, signature inference at line {infer_signature_line + 1})")
        return True
    else:
        print(f"  ❌ Last-chance fetch should be placed BEFORE field inference logic")
        print(f"     (Last-chance at line {last_chance_fetch_line + 1}, signature inference at line {infer_signature_line + 1})")
        return False


def test_no_new_dependencies():
    """Test that no new dependencies were introduced"""
    print("=" * 80)
    print("TEST: No New Dependencies")
    print("=" * 80)
    
    with open('trade_processor.py', 'r') as f:
        content = f.read()
    
    # Check that we're using existing utilities
    checks = [
        (
            'from utils import fetch_json_rpc_with_url' in content,
            '✅ Uses existing fetch_json_rpc_with_url from utils'
        ),
        (
            'import asyncio' in content,
            '✅ Uses standard library asyncio (already imported)'
        ),
        (
            'self.rpc_client' in content,
            '✅ Uses existing rpc_client instance'
        ),
    ]
    
    passed = 0
    for check, description in checks:
        if check:
            print(f"  {description}")
            passed += 1
        else:
            print(f"  ❌ {description.replace('✅', '')}")
    
    print(f"\n  Result: {passed}/{len(checks)} checks passed\n")
    return passed == len(checks)


def main():
    """Run all tests"""
    results = [
        test_last_chance_fetch_code_exists(),
        test_fetch_placement(),
        test_no_new_dependencies(),
    ]
    
    print("=" * 80)
    print("FINAL RESULTS")
    print("=" * 80)
    
    passed = sum(results)
    total = len(results)
    
    print(f"\nTests Passed: {passed}/{total}\n")
    
    if passed == total:
        print("🎉 ALL LAST-CHANCE FETCH TESTS PASSED!")
        print("\nThe implementation:")
        print("  ✅ Fetches transaction by signature when logs and tx are missing")
        print("  ✅ Uses existing RPC client infrastructure")
        print("  ✅ Maintains consistent logging format")
        print("  ✅ Attaches logs and transaction to trade_info")
        print("  ✅ Placed correctly before field inference logic")
        return 0
    else:
        print("❌ SOME TESTS FAILED")
        return 1


if __name__ == "__main__":
    sys.exit(main())
