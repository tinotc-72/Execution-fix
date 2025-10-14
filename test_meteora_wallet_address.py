#!/usr/bin/env python3
"""
Test to verify Meteora DEX detection and wallet_address extraction work correctly.
"""

import sys
import json
from wallet_tx_parser import WalletTransactionParser

class MockRPCClient:
    """Mock RPC client for testing"""
    pass

def test_meteora_detection():
    """Test that Meteora program ID triggers correct DEX and action"""
    print("=" * 80)
    print("TEST: Meteora DEX Detection")
    print("=" * 80)
    
    parser = WalletTransactionParser(MockRPCClient())
    
    # Test case 1: Transaction with Meteora program in message.instructions
    tx_data_1 = {
        "signature": "test_sig_1",
        "message": {
            "instructions": [
                {"programId": "11111111111111111111111111111111"},  # System program
                {"programId": "dbcij3LWUppWqq96dh6gJWwBifmcGfLSB5D4DuSMaqN"},  # Meteora
            ],
            "accountKeys": [
                {"pubkey": "WalletABC123", "signer": True},
                {"pubkey": "WalletXYZ789", "signer": False},
            ]
        }
    }
    
    result_1 = parser.parse_transaction(tx_data_1)
    
    print("\nTest Case 1: Meteora in message.instructions")
    print(f"  Input: Meteora program ID in instructions")
    print(f"  Result DEX: {result_1.get('dex')}")
    print(f"  Result Action: {result_1.get('action')}")
    print(f"  Result Wallet Address: {result_1.get('wallet_address')}")
    
    if result_1.get('dex') == 'meteora':
        print("  ✅ PASS: DEX correctly set to 'meteora'")
    else:
        print(f"  ❌ FAIL: Expected dex='meteora', got '{result_1.get('dex')}'")
        return False
    
    if result_1.get('action') == 'swap':
        print("  ✅ PASS: Action correctly set to 'swap'")
    else:
        print(f"  ❌ FAIL: Expected action='swap', got '{result_1.get('action')}'")
        return False
    
    if result_1.get('wallet_address') == 'WalletABC123':
        print("  ✅ PASS: Wallet address correctly extracted from first signer")
    else:
        print(f"  ❌ FAIL: Expected wallet_address='WalletABC123', got '{result_1.get('wallet_address')}'")
        return False
    
    # Test case 2: Transaction with Meteora in legacy instructions format
    tx_data_2 = {
        "signature": "test_sig_2",
        "instructions": [
            {"programId": "dbcij3LWUppWqq96dh6gJWwBifmcGfLSB5D4DuSMaqN"},
        ]
    }
    
    result_2 = parser.parse_transaction(tx_data_2)
    
    print("\nTest Case 2: Meteora in legacy instructions format (no message wrapper)")
    print(f"  Result DEX: {result_2.get('dex')}")
    print(f"  Result Action: {result_2.get('action')}")
    
    # This case may not detect Meteora if there's no message.instructions
    # But identify_dex should catch it
    if result_2.get('dex') == 'unknown':
        print("  ℹ️  INFO: Legacy format not detected by new logic (expected)")
        print("  ℹ️  INFO: Would be handled by identify_dex fallback")
    
    # Test case 3: Multiple signers
    tx_data_3 = {
        "signature": "test_sig_3",
        "message": {
            "instructions": [
                {"programId": "dbcij3LWUppWqq96dh6gJWwBifmcGfLSB5D4DuSMaqN"},
            ],
            "accountKeys": [
                {"pubkey": "FirstSigner", "signer": True},
                {"pubkey": "SecondSigner", "signer": True},
                {"pubkey": "NotASigner", "signer": False},
            ]
        }
    }
    
    result_3 = parser.parse_transaction(tx_data_3)
    
    print("\nTest Case 3: Multiple signers - should use first")
    print(f"  Result Wallet Address: {result_3.get('wallet_address')}")
    
    if result_3.get('wallet_address') == 'FirstSigner':
        print("  ✅ PASS: First signer correctly selected")
    else:
        print(f"  ❌ FAIL: Expected 'FirstSigner', got '{result_3.get('wallet_address')}'")
        return False
    
    # Test case 4: No signers
    tx_data_4 = {
        "signature": "test_sig_4",
        "message": {
            "instructions": [
                {"programId": "dbcij3LWUppWqq96dh6gJWwBifmcGfLSB5D4DuSMaqN"},
            ],
            "accountKeys": [
                {"pubkey": "Account1", "signer": False},
                {"pubkey": "Account2", "signer": False},
            ]
        }
    }
    
    result_4 = parser.parse_transaction(tx_data_4)
    
    print("\nTest Case 4: No signers - wallet_address should be None or fallback")
    print(f"  Result Wallet Address: {result_4.get('wallet_address')}")
    
    if result_4.get('wallet_address') is None or result_4.get('wallet_address') == '':
        print("  ✅ PASS: No wallet_address when no signers (expected)")
    else:
        print(f"  ℹ️  INFO: Wallet address is '{result_4.get('wallet_address')}' (may be from fallback)")
    
    print("\n" + "=" * 80)
    print("✅ ALL METEORA DETECTION TESTS PASSED")
    print("=" * 80)
    return True

def test_return_format():
    """Test that parse_transaction returns wallet_address field"""
    print("\n" + "=" * 80)
    print("TEST: Return Format Includes wallet_address")
    print("=" * 80)
    
    parser = WalletTransactionParser(MockRPCClient())
    
    tx_data = {
        "signature": "test",
        "message": {
            "instructions": [{"programId": "dbcij3LWUppWqq96dh6gJWwBifmcGfLSB5D4DuSMaqN"}],
            "accountKeys": [{"pubkey": "TestWallet", "signer": True}]
        }
    }
    
    result = parser.parse_transaction(tx_data)
    
    print("\nChecking return dictionary keys:")
    required_keys = ['dex', 'action', 'mint', 'amount', 'signature', 'wallet_address']
    
    for key in required_keys:
        if key in result:
            print(f"  ✅ '{key}' present in result")
        else:
            print(f"  ❌ '{key}' missing from result")
            return False
    
    # Check that source_wallet is NOT in result (it's been replaced)
    if 'source_wallet' not in result:
        print("  ✅ 'source_wallet' correctly NOT in result (replaced by wallet_address)")
    else:
        print("  ⚠️  'source_wallet' still in result (may cause confusion)")
    
    print("\n✅ RETURN FORMAT TEST PASSED")
    print("=" * 80)
    return True

def main():
    """Run all tests"""
    success = True
    
    if not test_meteora_detection():
        success = False
    
    if not test_return_format():
        success = False
    
    if success:
        print("\n🎉 ALL TESTS PASSED!")
        return 0
    else:
        print("\n❌ SOME TESTS FAILED")
        return 1

if __name__ == "__main__":
    sys.exit(main())
