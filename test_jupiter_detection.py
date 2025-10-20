#!/usr/bin/env python3
"""
Test Jupiter detection and wallet_address extraction fix.

Requirements:
1. Detect Jupiter by programId "JUP6LkbZbjS1jKKwapdHNy74zcZ3tLUZoi5QNyVTaV4"
2. Detect Jupiter when logs include "Instruction: SharedAccountsRouteV2"
3. Set parsed["dex"]="jupiter" and default parsed["action"]="swap"
4. Set wallet_address to first signer when available
5. Fallback to accountKeys[0] (fee payer) when no signers present
"""

import sys
from wallet_tx_parser import WalletTransactionParser

class MockRPCClient:
    pass

def test_jupiter_detection():
    """Test Jupiter detection requirements"""
    print("=" * 80)
    print("JUPITER DETECTION AND WALLET_ADDRESS FIX VALIDATION")
    print("=" * 80)
    
    parser = WalletTransactionParser(MockRPCClient())
    
    # Test Case 1: Jupiter detection by programId
    print("\n--- Test 1: Jupiter Detection by programId ---")
    tx_1 = {
        "message": {
            "instructions": [
                {"programId": "JUP6LkbZbjS1jKKwapdHNy74zcZ3tLUZoi5QNyVTaV4"}
            ],
            "accountKeys": [
                {"pubkey": "WalletABC", "signer": True}
            ]
        }
    }
    
    result_1 = parser.parse_transaction(tx_1)
    
    print(f"Input: Jupiter programId in instructions")
    print(f"Expected: dex='jupiter', action='swap'")
    print(f"Actual: dex='{result_1.get('dex')}', action='{result_1.get('action')}'")
    
    if result_1.get('dex') == 'jupiter' and result_1.get('action') == 'swap':
        print("✅ PASS: Jupiter correctly detected by programId")
    else:
        print("❌ FAIL: Jupiter detection by programId failed")
        return False
    
    # Test Case 2: Jupiter detection from logs with SharedAccountsRouteV2
    print("\n--- Test 2: Jupiter Detection from logs (SharedAccountsRouteV2) ---")
    tx_2 = {
        "message": {
            "instructions": [
                {"programId": "SomeOtherProgram"}
            ],
            "accountKeys": [
                {"pubkey": "WalletXYZ", "signer": True}
            ]
        },
        "meta": {
            "logMessages": [
                "Program 11111111111111111111111111111111 invoke [1]",
                "Instruction: SharedAccountsRouteV2",
                "Program 11111111111111111111111111111111 success"
            ]
        }
    }
    
    result_2 = parser.parse_transaction(tx_2)
    
    print(f"Input: Logs contain 'SharedAccountsRouteV2'")
    print(f"Expected: dex='jupiter', action='swap'")
    print(f"Actual: dex='{result_2.get('dex')}', action='{result_2.get('action')}'")
    
    if result_2.get('dex') == 'jupiter' and result_2.get('action') == 'swap':
        print("✅ PASS: Jupiter correctly detected from SharedAccountsRouteV2 log")
    else:
        print("❌ FAIL: Jupiter detection from SharedAccountsRouteV2 log failed")
        return False
    
    # Test Case 3: Jupiter detection from logs with JUP6LkbZ
    print("\n--- Test 3: Jupiter Detection from logs (JUP6LkbZ) ---")
    tx_3 = {
        "message": {
            "instructions": [
                {"programId": "SomeOtherProgram"}
            ],
            "accountKeys": [
                {"pubkey": "WalletDEF", "signer": True}
            ]
        },
        "meta": {
            "logMessages": [
                "Program JUP6LkbZbjS1jKKwapdHNy74zcZ3tLUZoi5QNyVTaV4 invoke [1]",
                "Program log: Swap executed",
                "Program JUP6LkbZbjS1jKKwapdHNy74zcZ3tLUZoi5QNyVTaV4 success"
            ]
        }
    }
    
    result_3 = parser.parse_transaction(tx_3)
    
    print(f"Input: Logs contain 'JUP6LkbZ'")
    print(f"Expected: dex='jupiter', action='swap'")
    print(f"Actual: dex='{result_3.get('dex')}', action='{result_3.get('action')}'")
    
    if result_3.get('dex') == 'jupiter' and result_3.get('action') == 'swap':
        print("✅ PASS: Jupiter correctly detected from JUP6LkbZ in logs")
    else:
        print("❌ FAIL: Jupiter detection from JUP6LkbZ in logs failed")
        return False
    
    # Test Case 4: wallet_address with signer flags
    print("\n--- Test 4: wallet_address with signer flags ---")
    tx_4 = {
        "message": {
            "instructions": [
                {"programId": "JUP6LkbZbjS1jKKwapdHNy74zcZ3tLUZoi5QNyVTaV4"}
            ],
            "accountKeys": [
                {"pubkey": "FirstSigner123", "signer": True},
                {"pubkey": "SecondSigner456", "signer": True},
                {"pubkey": "NotASigner789", "signer": False}
            ]
        }
    }
    
    result_4 = parser.parse_transaction(tx_4)
    
    print(f"Input: Multiple signers with signer flags")
    print(f"Expected: wallet_address='FirstSigner123'")
    print(f"Actual: wallet_address='{result_4.get('wallet_address')}'")
    
    if result_4.get('wallet_address') == 'FirstSigner123':
        print("✅ PASS: First signer correctly selected when signer flags present")
    else:
        print("❌ FAIL: First signer selection failed")
        return False
    
    # Test Case 5: wallet_address fallback to index 0 (fee payer) - dict format
    print("\n--- Test 5: wallet_address fallback to index 0 (dict format) ---")
    tx_5 = {
        "message": {
            "instructions": [
                {"programId": "JUP6LkbZbjS1jKKwapdHNy74zcZ3tLUZoi5QNyVTaV4"}
            ],
            "accountKeys": [
                {"pubkey": "FeePayerWallet789"},  # No signer flag
                {"pubkey": "OtherAccount123"}
            ]
        }
    }
    
    result_5 = parser.parse_transaction(tx_5)
    
    print(f"Input: No signer flags, dict format")
    print(f"Expected: wallet_address='FeePayerWallet789' (index 0)")
    print(f"Actual: wallet_address='{result_5.get('wallet_address')}'")
    
    if result_5.get('wallet_address') == 'FeePayerWallet789':
        print("✅ PASS: Correctly falls back to index 0 (fee payer) for dict format")
    else:
        print("❌ FAIL: Fallback to index 0 failed for dict format")
        return False
    
    # Test Case 6: wallet_address fallback to index 0 - string format
    print("\n--- Test 6: wallet_address fallback to index 0 (string format) ---")
    tx_6 = {
        "message": {
            "instructions": [
                {"programId": "JUP6LkbZbjS1jKKwapdHNy74zcZ3tLUZoi5QNyVTaV4"}
            ],
            "accountKeys": [
                "StringFeePayerABC",  # String format (v0 transaction)
                "OtherAccountDEF"
            ]
        }
    }
    
    result_6 = parser.parse_transaction(tx_6)
    
    print(f"Input: No signer flags, string format")
    print(f"Expected: wallet_address='StringFeePayerABC' (index 0)")
    print(f"Actual: wallet_address='{result_6.get('wallet_address')}'")
    
    if result_6.get('wallet_address') == 'StringFeePayerABC':
        print("✅ PASS: Correctly falls back to index 0 (fee payer) for string format")
    else:
        print("❌ FAIL: Fallback to index 0 failed for string format")
        return False
    
    # Test Case 7: Combined Jupiter + wallet_address
    print("\n--- Test 7: Combined Jupiter detection + wallet_address ---")
    tx_7 = {
        "message": {
            "instructions": [
                {"programId": "11111111111111111111111111111111"},
                {"programId": "JUP6LkbZbjS1jKKwapdHNy74zcZ3tLUZoi5QNyVTaV4"},
                {"programId": "ComputeBudget111111111111111111111111111111"}
            ],
            "accountKeys": [
                {"pubkey": "TargetWallet456", "signer": True},
                {"pubkey": "OtherAccount789", "signer": False}
            ]
        }
    }
    
    result_7 = parser.parse_transaction(tx_7)
    
    print(f"Input: Jupiter among multiple instructions, with signer")
    print(f"Expected: dex='jupiter', action='swap', wallet_address='TargetWallet456'")
    print(f"Actual: dex='{result_7.get('dex')}', action='{result_7.get('action')}', wallet_address='{result_7.get('wallet_address')}'")
    
    if (result_7.get('dex') == 'jupiter' and 
        result_7.get('action') == 'swap' and 
        result_7.get('wallet_address') == 'TargetWallet456'):
        print("✅ PASS: All fields correctly set for Jupiter transaction")
    else:
        print("❌ FAIL: Combined requirements not met")
        return False
    
    # Test Case 8: Ensure Jupiter takes priority over other DEX detection
    print("\n--- Test 8: Jupiter priority over other DEX ---")
    tx_8 = {
        "message": {
            "instructions": [
                {"programId": "JUP6LkbZbjS1jKKwapdHNy74zcZ3tLUZoi5QNyVTaV4"},
                {"programId": "dbcij3LWUppWqq96dh6gJWwBifmcGfLSB5D4DuSMaqN"}  # Meteora
            ],
            "accountKeys": [
                {"pubkey": "MixedWallet", "signer": True}
            ]
        }
    }
    
    result_8 = parser.parse_transaction(tx_8)
    
    print(f"Input: Both Jupiter and Meteora programIds")
    print(f"Expected: dex='jupiter' (Jupiter detected first)")
    print(f"Actual: dex='{result_8.get('dex')}'")
    
    if result_8.get('dex') == 'jupiter':
        print("✅ PASS: Jupiter correctly detected when both are present")
    else:
        print("❌ FAIL: Jupiter priority failed")
        return False
    
    print("\n" + "=" * 80)
    print("✅ ALL JUPITER DETECTION AND WALLET_ADDRESS TESTS PASSED")
    print("=" * 80)
    return True

def main():
    if test_jupiter_detection():
        print("\n🎉 SUCCESS: Jupiter detection and wallet_address fix validated!")
        return 0
    else:
        print("\n❌ FAILURE: Some tests failed")
        return 1

if __name__ == "__main__":
    sys.exit(main())
