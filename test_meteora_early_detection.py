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
    """Test that the code has the correct early Meteora detection logic"""
    print("=" * 80)
    print("TEST: Code Implementation of Early Meteora Detection")
    print("=" * 80)
    
    with open('wallet_tx_parser.py', 'r') as f:
        content = f.read()
    
    success = True
    
    # Test 1: Check for early Meteora detection loop
    print("\n--- Test 1: Early Meteora Detection Loop ---")
    pattern1 = r'for\s+ix\s+in\s+instructions:.*?pid\s*=\s*ix\.get\("programId"\)\s+or\s+ix\.get\("program"\).*?if\s+pid\s*==\s*meteora_program_id:'
    if re.search(pattern1, content, re.DOTALL):
        print("✅ PASS: Early Meteora detection loop found")
    else:
        print("❌ FAIL: Early Meteora detection loop not found or incorrect")
        success = False
    
    # Test 2: Check for DEX override
    print("\n--- Test 2: DEX Override Logic ---")
    if 'if early_meteora_detected:' in content and 'dex = "meteora"' in content:
        print("✅ PASS: DEX override logic found")
    else:
        print("❌ FAIL: DEX override logic not found")
        success = False
    
    # Test 3: Check for action override
    print("\n--- Test 3: Action Override Logic ---")
    pattern3 = r'if\s+early_meteora_detected\s+and\s+action\s+in\s+\(None,\s*"unknown"\):'
    if re.search(pattern3, content):
        print("✅ PASS: Action override condition found")
    else:
        print("❌ FAIL: Action override condition not found")
        success = False
    
    if 'action = "swap"' in content:
        print("✅ PASS: Action set to 'swap' found")
    else:
        print("❌ FAIL: Action set to 'swap' not found")
        success = False
    
    # Test 4: Check Meteora program ID constant
    print("\n--- Test 4: Meteora Program ID Constant ---")
    if 'meteora_program_id = "dbcij3LWUppWqq96dh6gJWwBifmcGfLSB5D4DuSMaqN"' in content:
        print("✅ PASS: Correct Meteora program ID constant found")
    else:
        print("❌ FAIL: Meteora program ID constant not found or incorrect")
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
    
    # Find the early Meteora detection log messages
    if 'self.logger.info(f"✅ [PARSER] Early Meteora detection:' in content:
        print("✅ PASS: Early detection uses INFO level with ✅ emoji")
    else:
        print("❌ FAIL: Early detection logging format incorrect")
        return 1
    
    if 'self.logger.info(f"✅ [PARSER] Applied early Meteora detection override: dex=meteora")' in content:
        print("✅ PASS: DEX override uses INFO level with ✅ emoji")
    else:
        print("❌ FAIL: DEX override logging format incorrect")
        return 1
    
    if 'self.logger.info(f"✅ [PARSER] Applied early Meteora action override: action=swap")' in content:
        print("✅ PASS: Action override uses INFO level with ✅ emoji")
    else:
        print("❌ FAIL: Action override logging format incorrect")
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

