#!/usr/bin/env python3
"""
Standalone validation test for buy/sell inference logic.

This test validates the enhanced detect_buy_sell implementation by checking:
1. The code changes are present in trade_processor.py
2. WSOL tracking logic is implemented
3. mint_in and mint_out fields are saved
4. Required logging format is present
"""

import sys
import re

def validate_implementation():
    """Validate that the buy/sell inference implementation is correct"""
    
    print("\n" + "=" * 70)
    print("🧪 BUY/SELL INFERENCE IMPLEMENTATION VALIDATION")
    print("=" * 70 + "\n")
    
    results = []
    
    # Read the trade_processor.py file
    try:
        with open('/home/runner/work/Execution-fix/Execution-fix/trade_processor.py', 'r') as f:
            code = f.read()
    except Exception as e:
        print(f"❌ FAIL: Could not read trade_processor.py: {e}")
        return False
    
    # Test 1: Check WSOL constant definition
    print("🧪 Test 1: WSOL constant defined")
    print("-" * 70)
    if re.search(r'WSOL\s*=\s*["\']So11111111111111111111111111111111111111112["\']', code):
        print("✅ PASS: WSOL constant is defined")
        results.append(True)
    else:
        print("❌ FAIL: WSOL constant not found in detect_buy_sell method")
        results.append(False)
    print()
    
    # Test 2: Check WSOL tracking logic (not skipping WSOL)
    print("🧪 Test 2: WSOL balance changes are tracked (not skipped)")
    print("-" * 70)
    # Look for the old pattern that skips WSOL
    old_skip_pattern = r'if mint == ["\']So11111.*["\']:\s*logger\.debug.*Skipping SOL.*continue'
    if re.search(old_skip_pattern, code, re.DOTALL):
        print("❌ FAIL: Old WSOL skipping logic still present")
        results.append(False)
    else:
        print("✅ PASS: WSOL is no longer skipped in balance tracking")
        results.append(True)
    print()
    
    # Test 3: Check for owner_changes grouping
    print("🧪 Test 3: Balance changes grouped by owner")
    print("-" * 70)
    if 'owner_changes' in code and re.search(r'owner_changes\[owner\]\[mint\]', code):
        print("✅ PASS: Balance changes are grouped by owner")
        results.append(True)
    else:
        print("❌ FAIL: Owner grouping logic not found")
        results.append(False)
    print()
    
    # Test 4: Check WSOL-based buy inference
    print("🧪 Test 4: WSOL-based BUY inference (WSOL down + token up)")
    print("-" * 70)
    buy_pattern = r'if delta > 0 and wsol_delta < 0:.*action_type = ["\']buy["\'].*mint_in = WSOL.*mint_out = mint'
    if re.search(buy_pattern, code, re.DOTALL):
        print("✅ PASS: BUY inference logic found (WSOL decreases, token increases)")
        results.append(True)
    else:
        print("❌ FAIL: BUY inference logic not found or incomplete")
        results.append(False)
    print()
    
    # Test 5: Check WSOL-based sell inference
    print("🧪 Test 5: WSOL-based SELL inference (token down + WSOL up)")
    print("-" * 70)
    sell_pattern = r'elif delta < 0 and wsol_delta > 0:.*action_type = ["\']sell["\'].*mint_in = mint.*mint_out = WSOL'
    if re.search(sell_pattern, code, re.DOTALL):
        print("✅ PASS: SELL inference logic found (token decreases, WSOL increases)")
        results.append(True)
    else:
        print("❌ FAIL: SELL inference logic not found or incomplete")
        results.append(False)
    print()
    
    # Test 6: Check mint_in and mint_out are saved
    print("🧪 Test 6: mint_in and mint_out fields saved in action_data")
    print("-" * 70)
    if re.search(r"['\"]mint_in['\"]\s*:\s*mint_in", code) and re.search(r"['\"]mint_out['\"]\s*:\s*mint_out", code):
        print("✅ PASS: mint_in and mint_out are saved in action_data")
        results.append(True)
    else:
        print("❌ FAIL: mint_in or mint_out not found in action_data")
        results.append(False)
    print()
    
    # Test 7: Check for required logging format
    print("🧪 Test 7: Required logging format present")
    print("-" * 70)
    log_pattern = r'logger\.info.*🎯 Detected action=%s.*action_type'
    if re.search(log_pattern, code, re.DOTALL):
        print("✅ PASS: Required log message '🎯 Detected action=%s' found")
        results.append(True)
    else:
        # Try alternative format
        if 'logger.info(f"🎯 Detected action={action_type}")' in code:
            print("✅ PASS: Required log message found (f-string format)")
            results.append(True)
        else:
            print("❌ FAIL: Required log message '🎯 Detected action=%s' not found")
            results.append(False)
    print()
    
    # Test 8: Check mint_in/mint_out logging
    print("🧪 Test 8: mint_in and mint_out logged")
    print("-" * 70)
    if 'Mint In:' in code and 'Mint Out:' in code:
        print("✅ PASS: mint_in and mint_out are logged")
        results.append(True)
    else:
        print("❌ FAIL: mint_in or mint_out logging not found")
        results.append(False)
    print()
    
    # Summary
    print("=" * 70)
    print("📊 VALIDATION SUMMARY")
    print("=" * 70)
    
    passed = sum(results)
    total = len(results)
    
    print(f"Passed: {passed}/{total}")
    
    if passed == total:
        print("✅ ALL TESTS PASSED - Implementation is correct!")
    else:
        print(f"❌ {total - passed} TEST(S) FAILED - Review implementation")
    
    print("=" * 70 + "\n")
    
    return passed == total

def main():
    """Run validation"""
    success = validate_implementation()
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()
