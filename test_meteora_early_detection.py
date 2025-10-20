#!/usr/bin/env python3
"""
Test script to verify early Meteora detection in wallet_tx_parser.py

This script validates that:
1. Meteora program ID is detected early in transaction parsing
2. DEX is set to "meteora" when Meteora program is detected
3. Action is set to "swap" if action is unknown and Meteora is detected
"""

import sys
import re

def test_code_implementation():
    """Test that the code has the correct Meteora detection logic"""
    print("=" * 80)
    print("TEST: Code Implementation of Meteora Detection")
    print("=" * 80)
    
    with open('wallet_tx_parser.py', 'r') as f:
        content = f.read()
    
    success = True
    
    # Test 1: Check for METEORA_PID constant
    print("\n--- Test 1: METEORA_PID Constant ---")
    if 'METEORA_PID = "dbcij3LWUppWqq96dh6gJWwBifmcGfLSB5D4DuSMaqN"' in content:
        print("✅ PASS: Correct METEORA_PID constant found")
    else:
        print("❌ FAIL: METEORA_PID constant not found or incorrect")
        success = False
    
    # Test 2: Check for Meteora detection loop with parsed dict
    print("\n--- Test 2: Meteora Detection Loop ---")
    pattern2 = r'for\s+ix\s+in\s+\(tx\.get\("message",\s*\{\}\)\.get\("instructions"\)\s+or\s+\[\]\):'
    if re.search(pattern2, content, re.DOTALL):
        print("✅ PASS: Meteora detection loop with tx.get pattern found")
    else:
        print("❌ FAIL: Meteora detection loop not found or incorrect")
        success = False
    
    # Test 3: Check for DEX assignment to parsed dict
    print("\n--- Test 3: DEX Assignment Logic ---")
    if 'parsed["dex"] = "meteora"' in content:
        print("✅ PASS: DEX assignment to parsed dict found")
    else:
        print("❌ FAIL: DEX assignment logic not found")
        success = False
    
    # Test 4: Check for action setdefault
    print("\n--- Test 4: Action Setdefault Logic ---")
    if 'parsed.setdefault("action", "swap")' in content:
        print("✅ PASS: Action setdefault found")
    else:
        print("❌ FAIL: Action setdefault not found")
        success = False
    
    # Test 5: Check for wallet_address extraction from signers
    print("\n--- Test 5: Wallet Address Extraction ---")
    pattern5 = r'signers\s*=\s*\[k\["pubkey"\]\s+for\s+k\s+in\s+\(tx\.get\("message",\s*\{\}\)\.get\("accountKeys"\)\s+or\s+\[\]\)\s+if\s+k\.get\("signer"\)\]'
    if re.search(pattern5, content, re.DOTALL):
        print("✅ PASS: Wallet address extraction from signers found")
    else:
        print("❌ FAIL: Wallet address extraction not found or incorrect")
        success = False
    
    # Test 6: Check for wallet_address assignment
    print("\n--- Test 6: Wallet Address Assignment ---")
    if 'parsed["wallet_address"] = signers[0]' in content:
        print("✅ PASS: Wallet address assignment found")
    else:
        print("❌ FAIL: Wallet address assignment not found")
        success = False
    
    print("\n" + "=" * 80)
    if success:
        print("✅ ALL CODE TESTS PASSED")
        print("=" * 80)
        return 0
    else:
        print("❌ SOME CODE TESTS FAILED")
        print("=" * 80)
        return 1

def test_logging_format():
    """Verify that logging uses consistent emoji format"""
    print("\n" + "=" * 80)
    print("TEST: Verify Logging Format Consistency")
    print("=" * 80)
    
    # Check that the code uses INFO level with ✅ emoji
    with open('wallet_tx_parser.py', 'r') as f:
        content = f.read()
    
    # Find the Meteora detection log messages
    if 'self.logger.info(f"✅ [PARSER] Meteora detected:' in content:
        print("✅ PASS: Meteora detection uses INFO level with ✅ emoji")
    else:
        print("❌ FAIL: Meteora detection logging format incorrect")
        return 1
    
    # Check for WARNING emoji in unknown DEX log
    if 'self.logger.warning(f"⚠️ [PARSER] DEX=unknown' in content:
        print("✅ PASS: Unknown DEX uses WARNING level with ⚠️ emoji")
    else:
        print("❌ FAIL: Unknown DEX logging format incorrect")
        return 1
    
    print("\n✅ ALL LOGGING TESTS PASSED")
    print("=" * 80)
    return 0

def main():
    """Run all tests"""
    result1 = test_code_implementation()
    result2 = test_logging_format()
    
    if result1 == 0 and result2 == 0:
        print("\n🎉 ALL TESTS PASSED SUCCESSFULLY!")
        return 0
    else:
        print("\n❌ SOME TESTS FAILED")
        return 1

if __name__ == "__main__":
    sys.exit(main())

