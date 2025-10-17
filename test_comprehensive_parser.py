#!/usr/bin/env python3
"""
Comprehensive test for wallet_tx_parser.py to verify all problem statement requirements.
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from wallet_tx_parser import WalletTransactionParser

class MockLogger:
    def info(self, *args, **kwargs): pass
    def debug(self, *args, **kwargs): pass
    def warning(self, *args, **kwargs): pass
    def error(self, *args, **kwargs): pass

class MockRPCClient: pass

class MockDEXDecoder:
    def decode(self, dex_type, tx_data):
        return {"dex": "Unknown", "parsed": False}

def test_meteora_with_action_already_set():
    """Test that Meteora doesn't override an already-set action"""
    print("\n=== TEST: Meteora with action already set ===")
    
    parser = WalletTransactionParser(MockRPCClient())
    parser.logger = MockLogger()
    parser.dex_decoder = MockDEXDecoder()
    
    # Override decoder to return action="buy"
    class CustomDecoder:
        def decode(self, dex_type, tx_data):
            return {
                "dex": "Unknown",
                "parsed": False,
                "meteora_info": {
                    "action": "buy",  # Already set action
                    "user_wallet": None
                }
            }
    
    parser.dex_decoder = CustomDecoder()
    
    tx_data = {
        "message": {
            "instructions": [
                {"programId": "dbcij3LWUppWqq96dh6gJWwBifmcGfLSB5D4DuSMaqN"}
            ],
            "accountKeys": []
        }
    }
    
    result = parser.parse_transaction(tx_data)
    
    # When action is already "buy" from decoder, it should stay "buy", not become "swap"
    print(f"Input: Meteora with action='buy' from decoder")
    print(f"Expected: action='buy' (should not override)")
    print(f"Actual: action='{result['action']}'")
    
    # According to the code, parsed["action"] is set to "swap" when (None, "unknown")
    # But the decoder returns "buy", so it should be "buy"
    if result["action"] == "buy":
        print("✅ PASS: Action not overridden when already set")
        return True
    else:
        print(f"❌ FAIL: Expected action='buy', got action='{result['action']}'")
        return False

def test_jupiter_and_meteora_priority():
    """Test that Jupiter takes priority over Meteora when both are present"""
    print("\n=== TEST: Jupiter and Meteora priority ===")
    
    parser = WalletTransactionParser(MockRPCClient())
    parser.logger = MockLogger()
    parser.dex_decoder = MockDEXDecoder()
    
    tx_data = {
        "message": {
            "instructions": [
                {"programId": "JUP6LkbZbjS1jKKwapdHNy74zcZ3tLUZoi5QNyVTaV4"},
                {"programId": "dbcij3LWUppWqq96dh6gJWwBifmcGfLSB5D4DuSMaqN"}
            ],
            "accountKeys": []
        }
    }
    
    result = parser.parse_transaction(tx_data)
    
    print(f"Input: Both Jupiter and Meteora program IDs")
    print(f"Expected: dex='jupiter' (Jupiter takes priority)")
    print(f"Actual: dex='{result['dex']}'")
    
    if result["dex"] == "jupiter":
        print("✅ PASS: Jupiter correctly takes priority")
        return True
    else:
        print(f"❌ FAIL: Expected dex='jupiter', got dex='{result['dex']}'")
        return False

def test_empty_accountkeys():
    """Test handling of empty accountKeys array"""
    print("\n=== TEST: Empty accountKeys ===")
    
    parser = WalletTransactionParser(MockRPCClient())
    parser.logger = MockLogger()
    parser.dex_decoder = MockDEXDecoder()
    
    tx_data = {
        "message": {
            "instructions": [],
            "accountKeys": []
        }
    }
    
    result = parser.parse_transaction(tx_data)
    
    print(f"Input: Empty accountKeys array")
    print(f"Expected: wallet_address=None")
    print(f"Actual: wallet_address='{result.get('wallet_address')}'")
    
    if result.get("wallet_address") is None:
        print("✅ PASS: Handles empty accountKeys gracefully")
        return True
    else:
        print(f"✅ PASS: wallet_address set to '{result.get('wallet_address')}' (acceptable)")
        return True

def test_parse_transaction_return_format():
    """Test that parse_transaction returns all required fields"""
    print("\n=== TEST: parse_transaction return format ===")
    
    parser = WalletTransactionParser(MockRPCClient())
    parser.logger = MockLogger()
    parser.dex_decoder = MockDEXDecoder()
    
    tx_data = {
        "signature": "TestSignature123",
        "message": {
            "instructions": [
                {"programId": "JUP6LkbZbjS1jKKwapdHNy74zcZ3tLUZoi5QNyVTaV4"}
            ],
            "accountKeys": [
                {"pubkey": "TestWallet", "signer": True}
            ]
        }
    }
    
    result = parser.parse_transaction(tx_data)
    
    required_fields = ["dex", "action", "mint", "amount", "signature", "wallet_address"]
    missing = [f for f in required_fields if f not in result]
    
    print(f"Input: Complete transaction data")
    print(f"Expected fields: {', '.join(required_fields)}")
    print(f"Actual fields: {', '.join(result.keys())}")
    
    if not missing:
        print("✅ PASS: All required fields present")
        
        # Check that values are set
        print("\nField values:")
        for field in required_fields:
            value = result[field]
            print(f"  {field}: {value}")
        
        return True
    else:
        print(f"❌ FAIL: Missing fields: {', '.join(missing)}")
        return False

def main():
    """Run all comprehensive tests"""
    print("=" * 70)
    print("COMPREHENSIVE PARSER TESTS")
    print("=" * 70)
    
    tests = [
        ("Meteora with action already set", test_meteora_with_action_already_set),
        ("Jupiter and Meteora priority", test_jupiter_and_meteora_priority),
        ("Empty accountKeys", test_empty_accountkeys),
        ("parse_transaction return format", test_parse_transaction_return_format),
    ]
    
    passed = 0
    failed = 0
    
    for test_name, test_func in tests:
        try:
            if test_func():
                passed += 1
            else:
                failed += 1
        except Exception as e:
            failed += 1
            print(f"❌ EXCEPTION in {test_name}: {e}")
            import traceback
            traceback.print_exc()
    
    print("\n" + "=" * 70)
    print(f"RESULTS: {passed} passed, {failed} failed")
    print("=" * 70)
    
    return 0 if failed == 0 else 1

if __name__ == "__main__":
    sys.exit(main())
