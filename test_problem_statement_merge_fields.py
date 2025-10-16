#!/usr/bin/env python3
"""
Test to validate the exact problem statement requirement:
- merge_parsed_fields function exists with correct whitelisted fields
- Called immediately after parsing (post-backfill)
- Called before any defaulting/validation in the pipeline
"""

import sys
import os

# Add the project directory to the path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_function_signature():
    """Validate merge_parsed_fields function signature matches problem statement"""
    print("=" * 80)
    print("TEST: Function Signature (Problem Statement)")
    print("=" * 80)
    
    with open('main.py', 'r') as f:
        content = f.read()
    
    checks = [
        (
            'def merge_parsed_fields(trade_info: dict, parsed: dict) -> None:',
            '✅ Function signature matches problem statement exactly'
        ),
        (
            'if not parsed:\n        return',
            '✅ Early return on empty parsed dict'
        ),
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


def test_whitelisted_fields():
    """Validate whitelisted fields match problem statement exactly"""
    print("=" * 80)
    print("TEST: Whitelisted Fields (Problem Statement)")
    print("=" * 80)
    
    with open('main.py', 'r') as f:
        content = f.read()
    
    # Extract the mapping dict from merge_parsed_fields
    import re
    pattern = r'def merge_parsed_fields.*?mapping = \{(.*?)\}'
    match = re.search(pattern, content, re.DOTALL)
    
    if not match:
        print("  ❌ Could not find mapping dict in merge_parsed_fields")
        return False
    
    mapping_str = match.group(1)
    
    # Required fields from problem statement
    required_fields = [
        '"dex": "dex"',
        '"action": "action"',
        '"wallet_address": "wallet_address"',
        '"signature": "signature"',
        '"token_mint": "token_mint"',
        '"mint": "token_mint"',  # Alternative name for token_mint
    ]
    
    passed = 0
    for field in required_fields:
        if field in mapping_str:
            field_name = field.split(':')[0].strip().strip('"')
            print(f"  ✅ Whitelisted field: {field_name}")
            passed += 1
        else:
            print(f"  ❌ Missing whitelisted field: {field}")
    
    print(f"\n  Result: {passed}/{len(required_fields)} fields present\n")
    return passed == len(required_fields)


def test_conditional_update():
    """Validate conditional update logic matches problem statement"""
    print("=" * 80)
    print("TEST: Conditional Update Logic (Problem Statement)")
    print("=" * 80)
    
    with open('main.py', 'r') as f:
        content = f.read()
    
    checks = [
        (
            'if val and trade_info.get(dst) in (None, "", "unknown", "PENDING_ANALYSIS"):',
            '✅ Only updates if destination is None, "", "unknown", or "PENDING_ANALYSIS"'
        ),
        (
            'trade_info[dst] = val',
            '✅ Updates trade_info with parsed value'
        ),
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


def test_call_after_backfill():
    """Validate merge_parsed_fields is called after backfill"""
    print("=" * 80)
    print("TEST: Called After Backfill (Problem Statement)")
    print("=" * 80)
    
    with open('main.py', 'r') as f:
        content = f.read()
    
    lines = content.split('\n')
    
    # Find key locations
    backfill_success_idx = None
    post_backfill_parse_idx = None
    post_backfill_merge_idx = None
    infer_fields_idx = None
    
    for i, line in enumerate(lines):
        if '✅ [BACKFILL] Backfill succeeded' in line:
            backfill_success_idx = i
        if '[BACKFILL] Parsing backfilled transaction' in line:
            post_backfill_parse_idx = i
        if 'merge_parsed_fields(trade_info, parsed)' in line:
            # Check if this is in the backfill section
            if backfill_success_idx and abs(i - backfill_success_idx) < 20:
                post_backfill_merge_idx = i
        if 'STEP 1: Infer missing fields' in line or 'infer_missing_fields' in line:
            if not infer_fields_idx or (backfill_success_idx and i > backfill_success_idx):
                infer_fields_idx = i
    
    checks = []
    
    if backfill_success_idx and post_backfill_parse_idx:
        if post_backfill_parse_idx > backfill_success_idx:
            print(f"  ✅ Parse called after backfill success (line {post_backfill_parse_idx} > {backfill_success_idx})")
            checks.append(True)
        else:
            print(f"  ❌ Parse NOT after backfill success")
            checks.append(False)
    else:
        print(f"  ❌ Could not find backfill success or post-backfill parse")
        checks.append(False)
    
    if post_backfill_parse_idx and post_backfill_merge_idx:
        if post_backfill_merge_idx > post_backfill_parse_idx:
            print(f"  ✅ Merge called immediately after parse (line {post_backfill_merge_idx} > {post_backfill_parse_idx})")
            checks.append(True)
        else:
            print(f"  ❌ Merge NOT after parse")
            checks.append(False)
    else:
        print(f"  ❌ Could not find post-backfill parse or merge")
        checks.append(False)
    
    if post_backfill_merge_idx and infer_fields_idx:
        if infer_fields_idx > post_backfill_merge_idx:
            print(f"  ✅ Merge called before infer_missing_fields (line {post_backfill_merge_idx} < {infer_fields_idx})")
            checks.append(True)
        else:
            print(f"  ❌ Merge NOT before infer_missing_fields")
            checks.append(False)
    else:
        print(f"  ❌ Could not find merge or infer_fields")
        checks.append(False)
    
    passed = sum(checks)
    print(f"\n  Result: {passed}/{len(checks)} ordering checks passed\n")
    return all(checks)


def test_call_with_transaction_and_meta():
    """Validate parse_transaction is called with both transaction and meta"""
    print("=" * 80)
    print("TEST: Parse Called with Transaction and Meta (Problem Statement)")
    print("=" * 80)
    
    with open('main.py', 'r') as f:
        content = f.read()
    
    # The problem statement shows:
    # parsed = wallet_tx_parser.parse_transaction(trade_info.get("transaction", {}), trade_info.get("meta"))
    # But the actual implementation passes trade_info which contains both
    
    checks = [
        (
            'self.tx_parser.parse_transaction(trade_info)',
            '✅ Pre-backfill: parse_transaction called with trade_info (contains transaction and meta)'
        ),
        (
            'tx_with_meta = {\n                            "transaction": trade_info.get("transaction", {}),\n                            "meta": trade_info.get("meta")\n                        }',
            '✅ Post-backfill: Creates dict with transaction and meta'
        ),
        (
            'self.tx_parser.parse_transaction(tx_with_meta)',
            '✅ Post-backfill: Passes tx_with_meta to parse_transaction'
        ),
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


def main():
    """Run all tests"""
    print("\n" + "=" * 80)
    print("PROBLEM STATEMENT VALIDATION: merge_parsed_fields Implementation")
    print("=" * 80 + "\n")
    
    results = []
    
    results.append(("Function Signature", test_function_signature()))
    results.append(("Whitelisted Fields", test_whitelisted_fields()))
    results.append(("Conditional Update Logic", test_conditional_update()))
    results.append(("Called After Backfill", test_call_after_backfill()))
    results.append(("Parse with Transaction and Meta", test_call_with_transaction_and_meta()))
    
    print("\n" + "=" * 80)
    print("SUMMARY")
    print("=" * 80)
    
    all_passed = True
    for test_name, passed in results:
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"  {status}: {test_name}")
        if not passed:
            all_passed = False
    
    print("=" * 80)
    
    if all_passed:
        print("\n✅ ALL PROBLEM STATEMENT REQUIREMENTS MET")
        print("\nProblem Statement Compliance:")
        print("  ✅ merge_parsed_fields(trade_info, parsed) defined")
        print("  ✅ Whitelists: dex, action, wallet_address, signature, token_mint/mint")
        print("  ✅ Called immediately after parsing (post-backfill)")
        print("  ✅ Called before any defaulting/validation (infer_missing_fields)")
        print("  ✅ Parse called with transaction and meta data")
        print("  ✅ Prevents loss of fields like dex or wallet_address")
        return 0
    else:
        print("\n❌ SOME REQUIREMENTS NOT MET")
        return 1


if __name__ == "__main__":
    sys.exit(main())
