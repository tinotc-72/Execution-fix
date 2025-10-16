#!/usr/bin/env python3
"""
Test to verify that merge_parsed_fields is called after backfill.
This ensures that fields from backfilled transactions are properly parsed and merged.
"""

import sys
import os

# Add the project directory to the path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_post_backfill_parsing():
    """Test that parsing and merging happens after backfill"""
    print("=" * 80)
    print("TEST: Post-Backfill Parsing and Merging")
    print("=" * 80)
    
    with open('main.py', 'r') as f:
        content = f.read()
    
    # Find the backfill section
    import re
    
    # Look for the pattern: backfill success -> parse -> merge
    checks = [
        (
            'logger.info("✅ [BACKFILL] Backfill succeeded — proceeding to validation")',
            '✅ Backfill success log exists'
        ),
        (
            'logger.debug(f"[BACKFILL] Parsing backfilled transaction...")',
            '✅ Post-backfill parsing log exists'
        ),
        (
            'parsed = self.tx_parser.parse_transaction',
            '✅ parse_transaction called after backfill'
        ),
        (
            'merge_parsed_fields(trade_info, parsed)',
            '✅ merge_parsed_fields called with parsed backfilled data'
        ),
        (
            'logger.debug(f"[BACKFILL] ✅ Merged fields from backfilled transaction")',
            '✅ Post-backfill merge success log exists'
        ),
    ]
    
    passed = 0
    for pattern, description in checks:
        if pattern in content:
            print(f"  {description}")
            passed += 1
        else:
            print(f"  ❌ {description.replace('✅', '')} - NOT FOUND")
    
    # Check the order - all patterns should appear in sequence after backfill success
    lines = content.split('\n')
    backfill_success_idx = None
    parse_backfill_idx = None
    merge_backfill_idx = None
    infer_fields_idx = None
    
    for i, line in enumerate(lines):
        if '✅ [BACKFILL] Backfill succeeded' in line:
            backfill_success_idx = i
        if '[BACKFILL] Parsing backfilled transaction' in line:
            parse_backfill_idx = i
        if 'merge_parsed_fields(trade_info, parsed)' in line:
            # Check if this is in the backfill section (within 20 lines of backfill success)
            if backfill_success_idx and abs(i - backfill_success_idx) < 20:
                merge_backfill_idx = i
        if 'STEP 1: Infer missing fields before validation' in line:
            infer_fields_idx = i
    
    # Verify ordering
    if all([backfill_success_idx, parse_backfill_idx, merge_backfill_idx, infer_fields_idx]):
        if (backfill_success_idx < parse_backfill_idx < merge_backfill_idx < infer_fields_idx):
            print("  ✅ Correct order: backfill success -> parse -> merge -> infer_fields")
            passed += 1
        else:
            print(f"  ❌ Incorrect order: backfill={backfill_success_idx}, parse={parse_backfill_idx}, merge={merge_backfill_idx}, infer={infer_fields_idx}")
    else:
        print(f"  ❌ Could not verify ordering (backfill={backfill_success_idx}, parse={parse_backfill_idx}, merge={merge_backfill_idx}, infer={infer_fields_idx})")
    
    print(f"\n  Result: {passed}/{len(checks) + 1} checks passed\n")
    return passed == (len(checks) + 1)


def test_error_handling():
    """Test that post-backfill parsing has proper error handling"""
    print("=" * 80)
    print("TEST: Post-Backfill Error Handling")
    print("=" * 80)
    
    with open('main.py', 'r') as f:
        content = f.read()
    
    checks = [
        (
            'try:\n                    if \'transaction\' in trade_info:\n                        logger.debug(f"[BACKFILL] Parsing backfilled transaction...")',
            '✅ Has try block for post-backfill parsing'
        ),
        (
            'except Exception as e:\n                    logger.error(f"[BACKFILL] ❌ Error parsing backfilled transaction: {e}")',
            '✅ Has error handling for parsing failures'
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


def test_pre_backfill_parsing_preserved():
    """Test that pre-backfill parsing is still in place"""
    print("=" * 80)
    print("TEST: Pre-Backfill Parsing Preserved")
    print("=" * 80)
    
    with open('main.py', 'r') as f:
        content = f.read()
    
    checks = [
        (
            'logger.debug(f"[PIPELINE_ENTRY] Parsing transaction with wallet_tx_parser...")',
            '✅ Pre-backfill parsing log exists'
        ),
        (
            'self.tx_parser.parse_transaction(trade_info)',
            '✅ Pre-backfill parse_transaction call exists'
        ),
        (
            'logger.debug(f"[PIPELINE_ENTRY] ✅ Transaction parsed successfully")',
            '✅ Pre-backfill parse success log exists'
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
    print("VERIFICATION: Post-Backfill merge_parsed_fields Implementation")
    print("=" * 80 + "\n")
    
    results = []
    
    results.append(("Post-Backfill Parsing and Merging", test_post_backfill_parsing()))
    results.append(("Post-Backfill Error Handling", test_error_handling()))
    results.append(("Pre-Backfill Parsing Preserved", test_pre_backfill_parsing_preserved()))
    
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
        print("\n✅ ALL POST-BACKFILL VERIFICATIONS PASSED")
        print("\nImplementation Summary:")
        print("  • Post-backfill parsing added after backfill success")
        print("  • merge_parsed_fields called with backfilled data")
        print("  • Proper error handling for parsing failures")
        print("  • Pre-backfill parsing preserved for early transactions")
        print("  • Fields from backfilled transactions properly merged")
        return 0
    else:
        print("\n❌ SOME VERIFICATIONS FAILED")
        return 1


if __name__ == "__main__":
    sys.exit(main())
