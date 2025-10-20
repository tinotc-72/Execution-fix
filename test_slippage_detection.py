#!/usr/bin/env python3
"""
Test to validate slippage detection and meta attachment helpers.

This test validates:
1. ensure_meta_in_trade_info helper exists and works correctly
2. annotate_source_failure helper exists and detects slippage errors
3. Both helpers are called at the start of infer_missing_fields
4. Mint inference logic remains unchanged
"""

import re
import sys


def test_helpers_exist():
    """Test that both helper methods exist in TradeProcessor class."""
    print("=" * 80)
    print("TEST 1: Helper Methods Exist")
    print("=" * 80)
    
    with open('trade_processor.py', 'r') as f:
        content = f.read()
    
    tests = [
        (r'def ensure_meta_in_trade_info\(self, trade_info: dict\) -> None:',
         '✅ ensure_meta_in_trade_info method exists with correct signature'),
        (r'def annotate_source_failure\(self, trade_info: dict\) -> None:',
         '✅ annotate_source_failure method exists with correct signature'),
    ]
    
    passed = 0
    for pattern, description in tests:
        if re.search(pattern, content):
            print(f"  {description}")
            passed += 1
        else:
            print(f"  ❌ Missing: {description}")
    
    print(f"\n  Result: {passed}/{len(tests)} checks passed\n")
    return 1 if passed == len(tests) else 0


def test_ensure_meta_implementation():
    """Test ensure_meta_in_trade_info implementation."""
    print("=" * 80)
    print("TEST 2: ensure_meta_in_trade_info Implementation")
    print("=" * 80)
    
    with open('trade_processor.py', 'r') as f:
        content = f.read()
    
    # Find the method
    match = re.search(
        r'def ensure_meta_in_trade_info\(self.*?\n(?:    .*?\n)*?(?=\n    def |\Z)',
        content,
        re.DOTALL
    )
    
    if not match:
        print("  ❌ Could not find ensure_meta_in_trade_info method")
        return 0
    
    method = match.group(0)
    
    tests = [
        (r'if "meta" not in trade_info:', '✅ Checks if meta is missing'),
        (r'backfilled = trade_info\.get\("backfilled_tx"\)', '✅ Gets backfilled_tx from trade_info'),
        (r'if backfilled and backfilled\.get\("meta"\):', '✅ Checks backfilled has meta'),
        (r'trade_info\["meta"\] = backfilled\["meta"\]', '✅ Attaches meta from backfilled'),
    ]
    
    passed = 0
    for pattern, description in tests:
        if re.search(pattern, method):
            print(f"  {description}")
            passed += 1
        else:
            print(f"  ❌ Missing: {description}")
    
    print(f"\n  Result: {passed}/{len(tests)} checks passed\n")
    return 1 if passed == len(tests) else 0


def test_annotate_source_failure_implementation():
    """Test annotate_source_failure implementation."""
    print("=" * 80)
    print("TEST 3: annotate_source_failure Implementation")
    print("=" * 80)
    
    with open('trade_processor.py', 'r') as f:
        content = f.read()
    
    # Find the method
    match = re.search(
        r'def annotate_source_failure\(self.*?\n(?:    .*?\n)*?(?=\n    def |\Z)',
        content,
        re.DOTALL
    )
    
    if not match:
        print("  ❌ Could not find annotate_source_failure method")
        return 0
    
    method = match.group(0)
    
    tests = [
        (r'meta = trade_info\.get\("meta"\) or {}', '✅ Gets meta safely'),
        (r'err = meta\.get\("err"\)', '✅ Gets error from meta'),
        (r'if not err:\s+return', '✅ Returns early if no error'),
        (r'trade_info\["source_tx_failed"\] = True', '✅ Sets source_tx_failed flag'),
        (r'logs = " "\.join\(meta\.get\("logMessages"\) or \[\]\)', '✅ Joins log messages'),
        (r'"Exceeded slippage tolerance" in logs', '✅ Checks for slippage message'),
        (r'"6004" in str\(err\)', '✅ Checks for 6004 error code'),
        (r'trade_info\["retry_hint"\] = "requote"', '✅ Sets retry_hint for slippage'),
        (r'logger\.warning\(.*ExceededSlippage.*6004.*re-quote', '✅ Logs warning with emoji'),
    ]
    
    passed = 0
    for pattern, description in tests:
        if re.search(pattern, method):
            print(f"  {description}")
            passed += 1
        else:
            print(f"  ❌ Missing: {description}")
    
    print(f"\n  Result: {passed}/{len(tests)} checks passed\n")
    return 1 if passed == len(tests) else 0


def test_helpers_called_at_start():
    """Test that helpers are called at the start of infer_missing_fields."""
    print("=" * 80)
    print("TEST 4: Helpers Called at Start of infer_missing_fields")
    print("=" * 80)
    
    with open('trade_processor.py', 'r') as f:
        content = f.read()
    
    # Find the infer_missing_fields method start
    match = re.search(
        r'def infer_missing_fields\(self.*?\n.*?logger\.info.*?\n(.*?)(?=\n        # Last-chance fetch)',
        content,
        re.DOTALL
    )
    
    if not match:
        print("  ❌ Could not find method start")
        return 0
    
    method_start = match.group(1)
    
    tests = [
        (r'# 0\) Make sure meta is attached', '✅ Has comment for step 0'),
        (r'self\.ensure_meta_in_trade_info\(trade_info\)',
         '✅ Calls ensure_meta_in_trade_info'),
        (r'# 0b\) Mark error context', '✅ Has comment for step 0b'),
        (r'self\.annotate_source_failure\(trade_info\)', '✅ Calls annotate_source_failure'),
    ]
    
    passed = 0
    for pattern, description in tests:
        if re.search(pattern, method_start):
            print(f"  {description}")
            passed += 1
        else:
            print(f"  ❌ Missing: {description}")
    
    print(f"\n  Result: {passed}/{len(tests)} checks passed\n")
    return 1 if passed == len(tests) else 0


def test_mint_inference_unchanged():
    """Test that mint inference from token balances is unchanged."""
    print("=" * 80)
    print("TEST 5: Mint Inference Remains Unchanged")
    print("=" * 80)
    
    with open('trade_processor.py', 'r') as f:
        content = f.read()
    
    # Find _extract_mint_from_token_balances
    match = re.search(
        r'def _extract_mint_from_token_balances\(self, meta: dict\).*?(?=\n    def |\Z)',
        content,
        re.DOTALL
    )
    
    if not match:
        print("  ❌ Could not find _extract_mint_from_token_balances method")
        return 0
    
    method = match.group(0)
    
    tests = [
        (r'def _extract_mint_from_token_balances\(self, meta: dict\) -> Optional\[str\]:',
         '✅ Method signature accepts meta: dict'),
        (r'\.get\("uiTokenAmount"\)', '✅ Uses uiTokenAmount'),
        (r'\.get\("uiAmount"\)', '✅ Uses uiAmount (not raw amount)'),
        (r'WSOL = "So11111111111111111111111111111111111111112"', '✅ Defines WSOL'),
        (r'if not mint or mint == WSOL:\s+continue', '✅ Ignores WSOL'),
        (r'delta = abs\(float\(post_amt\) - float\(pre_amt\)\)', '✅ Calculates delta'),
        (r'if delta > best\[1\]:', '✅ Chooses largest delta'),
        (r'# 2\) Fallback: first non-WSOL mint', '✅ Has fallback logic'),
        (r'✅ \[MINT_INFERENCE\] Resolved token mint from postTokenBalances',
         '✅ Success log unchanged'),
    ]
    
    passed = 0
    for pattern, description in tests:
        if re.search(pattern, method if 'def _extract_mint_from_token_balances' in pattern else content):
            print(f"  {description}")
            passed += 1
        else:
            print(f"  ❌ Missing: {description}")
    
    print(f"\n  Result: {passed}/{len(tests)} checks passed\n")
    return 1 if passed == len(tests) else 0


def test_no_new_dependencies():
    """Test that no new dependencies were introduced."""
    print("=" * 80)
    print("TEST 6: No New Dependencies")
    print("=" * 80)
    
    with open('trade_processor.py', 'r') as f:
        content = f.read()
    
    # Check imports section (first 200 lines)
    imports_section = '\n'.join(content.split('\n')[:200])
    
    # These should NOT be added
    forbidden_imports = [
        'requests',
        'httpx',
        'anchorpy',
        'solana.rpc',
    ]
    
    tests = []
    for imp in forbidden_imports:
        if imp not in imports_section:
            tests.append(f'✅ No new import: {imp}')
        else:
            tests.append(f'❌ Found new import: {imp}')
    
    # Verify logger is used (existing)
    if 'logger.warning' in content and '⚠️' in content:
        tests.append('✅ Uses existing logger with emoji')
    else:
        tests.append('❌ Logger not used correctly')
    
    passed = len([t for t in tests if '✅' in t])
    
    for test in tests:
        print(f"  {test}")
    
    print(f"\n  Result: {passed}/{len(tests)} checks passed\n")
    return 1 if passed == len(tests) else 0


def test_correct_placement():
    """Test that helpers are placed before infer_missing_fields."""
    print("=" * 80)
    print("TEST 7: Correct Method Placement")
    print("=" * 80)
    
    with open('trade_processor.py', 'r') as f:
        lines = f.readlines()
    
    ensure_meta_line = None
    annotate_failure_line = None
    infer_missing_line = None
    
    for i, line in enumerate(lines):
        if 'def ensure_meta_in_trade_info' in line:
            ensure_meta_line = i
        if 'def annotate_source_failure' in line:
            annotate_failure_line = i
        if 'def infer_missing_fields' in line:
            infer_missing_line = i
    
    tests = []
    if ensure_meta_line is not None:
        tests.append('✅ ensure_meta_in_trade_info method found')
    else:
        tests.append('❌ ensure_meta_in_trade_info method not found')
    
    if annotate_failure_line is not None:
        tests.append('✅ annotate_source_failure method found')
    else:
        tests.append('❌ annotate_source_failure method not found')
    
    if infer_missing_line is not None:
        tests.append('✅ infer_missing_fields method found')
    else:
        tests.append('❌ infer_missing_fields method not found')
    
    if all([ensure_meta_line, annotate_failure_line, infer_missing_line]):
        if ensure_meta_line < annotate_failure_line < infer_missing_line:
            tests.append('✅ Methods are in correct order (ensure_meta → annotate → infer)')
        else:
            tests.append('❌ Methods are not in correct order')
    
    passed = len([t for t in tests if '✅' in t])
    
    for test in tests:
        print(f"  {test}")
    
    print(f"\n  Result: {passed}/{len(tests)} checks passed\n")
    return 1 if passed == len(tests) else 0


def main():
    """Run all tests."""
    print("\n" + "=" * 80)
    print("SLIPPAGE DETECTION & META ATTACHMENT - VALIDATION")
    print("=" * 80 + "\n")
    
    results = []
    results.append(test_helpers_exist())
    results.append(test_ensure_meta_implementation())
    results.append(test_annotate_source_failure_implementation())
    results.append(test_helpers_called_at_start())
    results.append(test_mint_inference_unchanged())
    results.append(test_no_new_dependencies())
    results.append(test_correct_placement())
    
    print("=" * 80)
    print(f"FINAL RESULT: {sum(results)}/{len(results)} tests passed")
    print("=" * 80)
    
    if sum(results) == len(results):
        print("\n✅ ALL TESTS PASSED - Implementation is correct!")
        return 0
    else:
        print(f"\n❌ SOME TESTS FAILED - {len(results) - sum(results)} test(s) failed")
        return 1


if __name__ == '__main__':
    sys.exit(main())
