#!/usr/bin/env python3
"""
Test to validate the ensure_meta_in_trade_info enhancement.

This test validates:
1. Function signature matches problem statement (single parameter)
2. Function gets backfilled_tx from inside trade_info
3. Function is called before mint inference
4. Mint inference logic remains unchanged
"""

import re


def test_function_signature():
    """Test that ensure_meta_in_trade_info has the correct signature."""
    print("=" * 80)
    print("TEST 1: Function Signature")
    print("=" * 80)
    
    with open('trade_processor.py', 'r') as f:
        content = f.read()
    
    # Check the method signature
    if re.search(r'def ensure_meta_in_trade_info\(self, trade_info: dict\) -> None:', content):
        print("  ✅ Method has correct signature: (self, trade_info: dict) -> None")
        return 1
    else:
        print("  ❌ Method signature does not match")
        return 0


def test_function_implementation():
    """Test that the function implementation matches problem statement."""
    print("=" * 80)
    print("TEST 2: Function Implementation")
    print("=" * 80)
    
    with open('trade_processor.py', 'r') as f:
        content = f.read()
    
    # Find the method
    match = re.search(
        r'def ensure_meta_in_trade_info\(self, trade_info: dict\) -> None:.*?(?=\n    def |\Z)',
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
        (r'if backfilled and backfilled\.get\("meta"\):', '✅ Checks if backfilled has meta'),
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


def test_called_at_start():
    """Test that function is called at start of infer_missing_fields."""
    print("=" * 80)
    print("TEST 3: Called at Start of infer_missing_fields")
    print("=" * 80)
    
    with open('trade_processor.py', 'r') as f:
        content = f.read()
    
    # Find the start of infer_missing_fields
    match = re.search(
        r'def infer_missing_fields.*?logger\.info.*?\n(.*?)(?=\n        # Last-chance fetch)',
        content,
        re.DOTALL
    )
    
    if not match:
        print("  ❌ Could not find infer_missing_fields start")
        return 0
    
    method_start = match.group(1)
    
    if re.search(r'self\.ensure_meta_in_trade_info\(trade_info\)', method_start):
        print("  ✅ ensure_meta_in_trade_info is called at start of infer_missing_fields")
        return 1
    else:
        print("  ❌ ensure_meta_in_trade_info is NOT called at start")
        return 0


def test_called_before_mint_inference():
    """Test that function is called before mint inference."""
    print("=" * 80)
    print("TEST 4: Called Before Mint Inference")
    print("=" * 80)
    
    with open('trade_processor.py', 'r') as f:
        content = f.read()
    
    # Find the mint inference section
    match = re.search(
        r'# 6\. Infer token mint if missing.*?# Try enhanced log extraction',
        content,
        re.DOTALL
    )
    
    if not match:
        print("  ❌ Could not find mint inference section")
        return 0
    
    section = match.group(0)
    
    tests = [
        (r'# Ensure meta is present in trade_info for inference helpers', '✅ Has comment before inference'),
        (r'self\.ensure_meta_in_trade_info\(trade_info\)', '✅ Calls ensure_meta_in_trade_info before inference'),
    ]
    
    passed = 0
    for pattern, description in tests:
        if re.search(pattern, section):
            print(f"  {description}")
            passed += 1
        else:
            print(f"  ❌ Missing: {description}")
    
    print(f"\n  Result: {passed}/{len(tests)} checks passed\n")
    return 1 if passed == len(tests) else 0


def test_mint_inference_unchanged():
    """Test that mint inference logic remains unchanged."""
    print("=" * 80)
    print("TEST 5: Mint Inference Logic Unchanged")
    print("=" * 80)
    
    with open('trade_processor.py', 'r') as f:
        content = f.read()
    
    tests = [
        (r'meta = trade_info\.get\("meta"\) or \{\}', '✅ Gets meta from trade_info'),
        (r'if not meta:.*?tx = trade_info\.get\(\'transaction\'\) or trade_info\.get\(\'transaction_full\'\)', '✅ Fallback to transaction.meta'),
        (r'mint = self\._extract_mint_from_token_balances\(meta\)', '✅ Passes meta to extraction method'),
        (r'logger\.info\(f"✅ \[MINT_INFERENCE\] Resolved token mint from postTokenBalances: \{mint\}"\)', '✅ Success log unchanged'),
    ]
    
    passed = 0
    for pattern, description in tests:
        if re.search(pattern, content, re.DOTALL):
            print(f"  {description}")
            passed += 1
        else:
            print(f"  ❌ Missing: {description}")
    
    print(f"\n  Result: {passed}/{len(tests)} checks passed\n")
    return 1 if passed == len(tests) else 0


def main():
    """Run all tests."""
    print("\n" + "=" * 80)
    print("ENSURE_META_IN_TRADE_INFO ENHANCEMENT - VALIDATION")
    print("=" * 80 + "\n")
    
    results = []
    results.append(test_function_signature())
    results.append(test_function_implementation())
    results.append(test_called_at_start())
    results.append(test_called_before_mint_inference())
    results.append(test_mint_inference_unchanged())
    
    print("=" * 80)
    print("FINAL RESULTS")
    print("=" * 80)
    
    total = len(results)
    passed = sum(results)
    
    if passed == total:
        print(f"\n  ✅ ALL TESTS PASSED ({passed}/{total})\n")
        print("  Implementation Summary:")
        print("  ✅ Function has correct signature (single parameter)")
        print("  ✅ Gets backfilled_tx from inside trade_info")
        print("  ✅ Called at start of infer_missing_fields")
        print("  ✅ Called before mint inference")
        print("  ✅ Mint inference logic unchanged")
    else:
        print(f"\n  ❌ SOME TESTS FAILED ({passed}/{total} passed)\n")
        print("  ❌ Please review the implementation")
    
    print()
    return 0 if passed == total else 1


if __name__ == "__main__":
    exit(main())
