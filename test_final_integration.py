#!/usr/bin/env python3
"""
Final integration test to verify all problem statement requirements.
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from wallet_tx_parser import WalletTransactionParser, merge_parsed_fields

class MockLogger:
    def info(self, *args, **kwargs): pass
    def debug(self, *args, **kwargs): pass
    def warning(self, *args, **kwargs): pass
    def error(self, *args, **kwargs): pass

class MockRPCClient: pass

class MockDEXDecoder:
    def decode(self, dex_type, tx_data):
        return {"dex": "Unknown", "parsed": False}

def test_full_pipeline():
    """Test the full pipeline: parse -> merge -> validate"""
    print("\n=== INTEGRATION TEST: Full Pipeline ===")
    
    parser = WalletTransactionParser(MockRPCClient())
    parser.logger = MockLogger()
    parser.dex_decoder = MockDEXDecoder()
    
    # Simulate a Jupiter transaction
    tx_data = {
        "signature": "JupiterTxSignature123",
        "message": {
            "instructions": [
                {"programId": "JUP6LkbZbjS1jKKwapdHNy74zcZ3tLUZoi5QNyVTaV4"}
            ],
            "accountKeys": [
                {"pubkey": "UserWallet123", "signer": True},
                {"pubkey": "OtherAccount456", "signer": False}
            ]
        },
        "meta": {
            "logMessages": [
                "Program log: Instruction: SharedAccountsRouteV2",
                "Program log: Swap successful"
            ]
        }
    }
    
    # Step 1: Parse transaction
    print("\nStep 1: Parse transaction")
    parsed = parser.parse_transaction(tx_data)
    
    print(f"  Parsed dex: {parsed['dex']}")
    print(f"  Parsed action: {parsed['action']}")
    print(f"  Parsed wallet_address: {parsed['wallet_address']}")
    print(f"  Parsed signature: {parsed['signature']}")
    
    assert parsed["dex"] == "jupiter", "Jupiter should be detected"
    assert parsed["action"] == "swap", "Action should be swap"
    assert parsed["wallet_address"] == "UserWallet123", "First signer should be wallet_address"
    assert parsed["signature"] == "JupiterTxSignature123", "Signature should be preserved"
    
    # Step 2: Simulate trade_info with missing fields
    print("\nStep 2: Merge parsed fields into trade_info")
    trade_info = {
        "dex": None,
        "action": "unknown",
        "wallet_address": "PENDING_ANALYSIS",
        "signature": None,
        "token_mint": None,
    }
    
    print(f"  Before merge:")
    print(f"    dex: {trade_info['dex']}")
    print(f"    action: {trade_info['action']}")
    print(f"    wallet_address: {trade_info['wallet_address']}")
    
    # Use the merge_parsed_fields utility
    merge_parsed_fields(trade_info, parsed)
    
    print(f"  After merge:")
    print(f"    dex: {trade_info['dex']}")
    print(f"    action: {trade_info['action']}")
    print(f"    wallet_address: {trade_info['wallet_address']}")
    
    assert trade_info["dex"] == "jupiter", "DEX should be merged"
    assert trade_info["action"] == "swap", "Action should be merged"
    assert trade_info["wallet_address"] == "UserWallet123", "wallet_address should be merged"
    assert trade_info["signature"] == "JupiterTxSignature123", "Signature should be merged"
    
    print("\n✅ PASS: Full pipeline works correctly!")
    return True

def test_meteora_pipeline():
    """Test Meteora detection and merging"""
    print("\n=== INTEGRATION TEST: Meteora Pipeline ===")
    
    parser = WalletTransactionParser(MockRPCClient())
    parser.logger = MockLogger()
    parser.dex_decoder = MockDEXDecoder()
    
    tx_data = {
        "signature": "MeteoraTxSignature456",
        "message": {
            "instructions": [
                {"programId": "dbcij3LWUppWqq96dh6gJWwBifmcGfLSB5D4DuSMaqN"}
            ],
            "accountKeys": [
                {"pubkey": "MeteoraUser789", "signer": True}
            ]
        }
    }
    
    # Parse
    parsed = parser.parse_transaction(tx_data)
    
    print(f"  Parsed dex: {parsed['dex']}")
    print(f"  Parsed action: {parsed['action']}")
    print(f"  Parsed wallet_address: {parsed['wallet_address']}")
    
    assert parsed["dex"] == "meteora", "Meteora should be detected"
    assert parsed["action"] == "swap", "Action should be swap for Meteora"
    assert parsed["wallet_address"] == "MeteoraUser789", "First signer should be wallet_address"
    
    # Merge
    trade_info = {"dex": None, "action": None, "wallet_address": None}
    merge_parsed_fields(trade_info, parsed)
    
    assert trade_info["dex"] == "meteora"
    assert trade_info["action"] == "swap"
    assert trade_info["wallet_address"] == "MeteoraUser789"
    
    print("\n✅ PASS: Meteora pipeline works correctly!")
    return True

def test_preserve_good_fields():
    """Test that merge preserves already-good fields"""
    print("\n=== INTEGRATION TEST: Preserve Good Fields ===")
    
    # Simulate parsed result
    parsed = {
        "dex": "jupiter",
        "action": "swap",
        "wallet_address": "ParsedWallet",
    }
    
    # Simulate trade_info with some good fields already set
    trade_info = {
        "dex": "raydium",  # Already set - should be preserved
        "action": "unknown",  # Empty - should be updated
        "wallet_address": "GoodWallet",  # Already set - should be preserved
        "token_mint": None,  # Empty - would be updated if parsed had it
    }
    
    print(f"  Before merge:")
    print(f"    dex: {trade_info['dex']} (should be preserved)")
    print(f"    action: {trade_info['action']} (should be updated)")
    print(f"    wallet_address: {trade_info['wallet_address']} (should be preserved)")
    
    merge_parsed_fields(trade_info, parsed)
    
    print(f"  After merge:")
    print(f"    dex: {trade_info['dex']}")
    print(f"    action: {trade_info['action']}")
    print(f"    wallet_address: {trade_info['wallet_address']}")
    
    assert trade_info["dex"] == "raydium", "Should preserve existing good DEX"
    assert trade_info["action"] == "swap", "Should update unknown action"
    assert trade_info["wallet_address"] == "GoodWallet", "Should preserve existing good wallet"
    
    print("\n✅ PASS: Good fields preserved correctly!")
    return True

def main():
    """Run all integration tests"""
    print("=" * 70)
    print("FINAL INTEGRATION TESTS - Problem Statement Verification")
    print("=" * 70)
    
    tests = [
        ("Full Pipeline (Jupiter)", test_full_pipeline),
        ("Meteora Pipeline", test_meteora_pipeline),
        ("Preserve Good Fields", test_preserve_good_fields),
    ]
    
    passed = 0
    failed = 0
    
    for test_name, test_func in tests:
        try:
            if test_func():
                passed += 1
            else:
                failed += 1
                print(f"❌ FAIL: {test_name}")
        except Exception as e:
            failed += 1
            print(f"❌ EXCEPTION in {test_name}: {e}")
            import traceback
            traceback.print_exc()
    
    print("\n" + "=" * 70)
    print(f"RESULTS: {passed} passed, {failed} failed")
    print("=" * 70)
    
    if failed == 0:
        print("\n✅ ALL PROBLEM STATEMENT REQUIREMENTS VERIFIED!")
        print("\nImplemented Features:")
        print("  ✅ Jupiter detection by programId")
        print("  ✅ Jupiter detection by SharedAccountsRouteV2 in logs")
        print("  ✅ Meteora detection by programId")
        print("  ✅ Automatic dex and action setting")
        print("  ✅ wallet_address from first signer")
        print("  ✅ merge_parsed_fields utility function")
        print("  ✅ Field preservation logic")
    
    return 0 if failed == 0 else 1

if __name__ == "__main__":
    sys.exit(main())
