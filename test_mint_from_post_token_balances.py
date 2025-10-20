#!/usr/bin/env python3
"""
Test for mint inference from postTokenBalances enhancement.

This test validates that the _extract_mint_from_token_balances method:
1. Uses uiAmount instead of raw amount
2. Properly extracts meta from trade_info
3. Ignores WSOL
4. Chooses mint with largest absolute delta
5. Falls back to first non-WSOL mint if no delta
"""

import re


def test_extract_mint_method_signature():
    """Test that the method has the correct signature."""
    print("=" * 80)
    print("TEST: Method Signature")
    print("=" * 80)
    
    with open('trade_processor.py', 'r') as f:
        content = f.read()
    
    # Check method signature
    if re.search(r'def _extract_mint_from_token_balances\(self, meta: dict\)', content):
        print("  ✅ Method signature accepts meta dict parameter")
    else:
        print("  ❌ Method signature incorrect - should accept meta: dict")
        return 0
    
    return 1


def test_uses_ui_amount():
    """Test that the method uses uiAmount instead of raw amount."""
    print("=" * 80)
    print("TEST: Uses uiAmount")
    print("=" * 80)
    
    with open('trade_processor.py', 'r') as f:
        content = f.read()
    
    # Extract the method
    match = re.search(
        r'def _extract_mint_from_token_balances\(self, meta: dict\).*?(?=\n    def |\nclass |\Z)',
        content,
        re.DOTALL
    )
    
    if not match:
        print("  ❌ Could not find method")
        return 0
    
    method_content = match.group(0)
    
    tests = [
        (r'\.get\("uiAmount"\)', '✅ Uses uiAmount from uiTokenAmount'),
        (r'uiTokenAmount.*uiAmount', '✅ Accesses uiAmount correctly'),
        (r'WSOL.*So11111111111111111111111111111111111111112', '✅ Defines WSOL constant'),
        (r'if not mint or mint == WSOL', '✅ Ignores WSOL'),
    ]
    
    passed = 0
    for pattern, description in tests:
        if re.search(pattern, method_content, re.DOTALL):
            print(f"  {description}")
            passed += 1
        else:
            print(f"  ❌ Missing: {description}")
    
    print(f"\n  Result: {passed}/{len(tests)} checks passed\n")
    return 1 if passed == len(tests) else 0


def test_delta_based_selection():
    """Test that the method uses delta-based selection."""
    print("=" * 80)
    print("TEST: Delta-Based Selection")
    print("=" * 80)
    
    with open('trade_processor.py', 'r') as f:
        content = f.read()
    
    # Extract the method
    match = re.search(
        r'def _extract_mint_from_token_balances\(self, meta: dict\).*?(?=\n    def |\nclass |\Z)',
        content,
        re.DOTALL
    )
    
    if not match:
        print("  ❌ Could not find method")
        return 0
    
    method_content = match.group(0)
    
    tests = [
        (r'best.*=.*None.*0\.0', '✅ Initializes best tuple for tracking'),
        (r'delta = abs\(float\(post_amt\) - float\(pre_amt\)\)', '✅ Computes absolute delta'),
        (r'if delta > best\[1\]', '✅ Compares delta to find largest'),
        (r'best = \(mint, delta\)', '✅ Updates best mint when larger delta found'),
        (r'if best\[0\]:', '✅ Returns best mint if found'),
    ]
    
    passed = 0
    for pattern, description in tests:
        if re.search(pattern, method_content):
            print(f"  {description}")
            passed += 1
        else:
            print(f"  ❌ Missing: {description}")
    
    print(f"\n  Result: {passed}/{len(tests)} checks passed\n")
    return 1 if passed == len(tests) else 0


def test_fallback_logic():
    """Test that the method has proper fallback logic."""
    print("=" * 80)
    print("TEST: Fallback Logic")
    print("=" * 80)
    
    with open('trade_processor.py', 'r') as f:
        content = f.read()
    
    # Extract the method
    match = re.search(
        r'def _extract_mint_from_token_balances\(self, meta: dict\).*?(?=\n    def |\nclass |\Z)',
        content,
        re.DOTALL
    )
    
    if not match:
        print("  ❌ Could not find method")
        return 0
    
    method_content = match.group(0)
    
    tests = [
        (r'# 2\) Fallback:', '✅ Has fallback comment'),
        (r'for pb in post\.values\(\):', '✅ Iterates through post balances'),
        (r'if mint and mint != WSOL:', '✅ Checks for non-WSOL mint'),
        (r'return mint', '✅ Returns first valid mint'),
        (r'return None', '✅ Returns None if no mint found'),
    ]
    
    passed = 0
    for pattern, description in tests:
        if re.search(pattern, method_content):
            print(f"  {description}")
            passed += 1
        else:
            print(f"  ❌ Missing: {description}")
    
    print(f"\n  Result: {passed}/{len(tests)} checks passed\n")
    return 1 if passed == len(tests) else 0


def test_meta_extraction_in_inference():
    """Test that meta is properly extracted in infer_missing_fields."""
    print("=" * 80)
    print("TEST: Meta Extraction in Inference")
    print("=" * 80)
    
    with open('trade_processor.py', 'r') as f:
        content = f.read()
    
    # Find the inference code that calls the method
    match = re.search(
        r'# Also try extracting from token balances.*?logger\.warning.*could not extract mint from balances',
        content,
        re.DOTALL | re.IGNORECASE
    )
    
    if not match:
        print("  ❌ Could not find token balance extraction code")
        return 0
    
    inference_code = match.group(0)
    
    tests = [
        (r'meta = trade_info\.get\("meta"\)', '✅ Extracts meta from trade_info'),
        (r'if not meta:', '✅ Checks if meta is empty'),
        (r'meta = tx\.get\(\'meta\', \{\}\)', '✅ Falls back to extracting from transaction'),
        (r'self\._extract_mint_from_token_balances\(meta\)', '✅ Passes meta to method'),
        (r'Resolved token mint from postTokenBalances', '✅ Logs success with correct message'),
    ]
    
    passed = 0
    for pattern, description in tests:
        if re.search(pattern, inference_code, re.IGNORECASE):
            print(f"  {description}")
            passed += 1
        else:
            print(f"  ❌ Missing: {description}")
    
    print(f"\n  Result: {passed}/{len(tests)} checks passed\n")
    return 1 if passed == len(tests) else 0


def test_logging_format():
    """Test that logging uses correct emoji format."""
    print("=" * 80)
    print("TEST: Logging Format")
    print("=" * 80)
    
    with open('trade_processor.py', 'r') as f:
        content = f.read()
    
    # Find the inference code
    match = re.search(
        r'# Also try extracting from token balances.*?logger\.warning.*could not extract mint from balances',
        content,
        re.DOTALL | re.IGNORECASE
    )
    
    if not match:
        print("  ❌ Could not find token balance extraction code")
        return 0
    
    inference_code = match.group(0)
    
    tests = [
        (r'logger\.info.*✅.*Resolved token mint from postTokenBalances', '✅ INFO log uses ✅ emoji'),
        (r'logger\.warning.*⚠️', '✅ WARNING log uses ⚠️ emoji'),
    ]
    
    passed = 0
    for pattern, description in tests:
        if re.search(pattern, inference_code):
            print(f"  {description}")
            passed += 1
        else:
            print(f"  ❌ Missing: {description}")
    
    print(f"\n  Result: {passed}/{len(tests)} checks passed\n")
    return 1 if passed == len(tests) else 0


def main():
    """Run all tests."""
    print("\n" + "=" * 80)
    print("MINT INFERENCE FROM POSTTOKENBALANCES - VALIDATION")
    print("=" * 80 + "\n")
    
    tests = [
        test_extract_mint_method_signature,
        test_uses_ui_amount,
        test_delta_based_selection,
        test_fallback_logic,
        test_meta_extraction_in_inference,
        test_logging_format,
    ]
    
    results = [test() for test in tests]
    total = len(results)
    passed = sum(results)
    
    print("=" * 80)
    print("FINAL RESULTS")
    print("=" * 80)
    
    if passed == total:
        print(f"\n  ✅ ALL TESTS PASSED ({passed}/{total})")
        print("\n  Implementation Summary:")
        print("  ✅ Method accepts meta dict parameter")
        print("  ✅ Uses uiAmount from uiTokenAmount")
        print("  ✅ Ignores WSOL (So11111111111111111111111111111111111111112)")
        print("  ✅ Chooses mint with largest absolute delta")
        print("  ✅ Falls back to first non-WSOL mint if no delta")
        print("  ✅ Meta consistently extracted from trade_info")
        print("  ✅ Logging uses correct INFO/WARNING emoji format")
        print()
        return 0
    else:
        print(f"\n  ❌ SOME TESTS FAILED ({passed}/{total} passed)")
        print(f"  ❌ Please review the implementation")
        print()
        return 1


if __name__ == '__main__':
    exit(main())
