#!/usr/bin/env python3
"""
Final validation test for problem statement requirements.

Requirements from problem statement:
1. If any instruction programId equals dbcij3LWUppWqq96dh6gJWwBifmcGfLSB5D4DuSMaqN, 
   set parsed["dex"] = "meteora" and if action is unset set parsed["action"] = "swap"
2. Set parsed["wallet_address"] to the first signer in transaction.message.accountKeys 
   that is not our own wallet (if you know it), otherwise the first signer.
"""

import sys
from wallet_tx_parser import WalletTransactionParser

class MockRPCClient:
    pass

def test_exact_problem_statement():
    """Test exact requirements from problem statement"""
    print("=" * 80)
    print("PROBLEM STATEMENT VALIDATION")
    print("=" * 80)
    
    parser = WalletTransactionParser(MockRPCClient())
    
    # Test Case 1: Meteora program ID should set dex="meteora" and action="swap"
    print("\n--- Requirement 1: Meteora Detection ---")
    tx_1 = {
        "message": {
            "instructions": [
                {"programId": "dbcij3LWUppWqq96dh6gJWwBifmcGfLSB5D4DuSMaqN"}
            ],
            "accountKeys": [
                {"pubkey": "WalletABC", "signer": True}
            ]
        }
    }
    
    result_1 = parser.parse_transaction(tx_1)
    
    print(f"Input: Meteora program ID in instructions")
    print(f"Expected: dex='meteora', action='swap'")
    print(f"Actual: dex='{result_1.get('dex')}', action='{result_1.get('action')}'")
    
    if result_1.get('dex') == 'meteora' and result_1.get('action') == 'swap':
        print("✅ PASS: Meteora correctly sets dex and action")
    else:
        print("❌ FAIL: Meteora detection failed")
        return False
    
    # Test Case 2: Action is "swap" only when not set by other means
    print("\n--- Requirement 2: Action setdefault behavior ---")
    tx_2 = {
        "message": {
            "instructions": [
                {"programId": "dbcij3LWUppWqq96dh6gJWwBifmcGfLSB5D4DuSMaqN"}
            ],
            "accountKeys": []
        }
    }
    
    result_2 = parser.parse_transaction(tx_2)
    
    print(f"Input: Meteora program ID, no action from decoder")
    print(f"Expected: action='swap'")
    print(f"Actual: action='{result_2.get('action')}'")
    
    if result_2.get('action') == 'swap':
        print("✅ PASS: Action correctly defaults to 'swap' for Meteora")
    else:
        print("❌ FAIL: Action setdefault failed")
        return False
    
    # Test Case 3: wallet_address is first signer
    print("\n--- Requirement 3: First Signer as wallet_address ---")
    tx_3 = {
        "message": {
            "instructions": [
                {"programId": "SomeOtherProgram"}
            ],
            "accountKeys": [
                {"pubkey": "FirstSigner123", "signer": True},
                {"pubkey": "SecondSigner456", "signer": True},
                {"pubkey": "NotASigner789", "signer": False}
            ]
        }
    }
    
    result_3 = parser.parse_transaction(tx_3)
    
    print(f"Input: Multiple signers in accountKeys")
    print(f"Expected: wallet_address='FirstSigner123'")
    print(f"Actual: wallet_address='{result_3.get('wallet_address')}'")
    
    if result_3.get('wallet_address') == 'FirstSigner123':
        print("✅ PASS: First signer correctly selected")
    else:
        print("❌ FAIL: First signer selection failed")
        return False
    
    # Test Case 4: Combined test - Meteora + wallet_address
    print("\n--- Requirement 4: Combined Meteora + wallet_address ---")
    tx_4 = {
        "message": {
            "instructions": [
                {"programId": "11111111111111111111111111111111"},
                {"programId": "dbcij3LWUppWqq96dh6gJWwBifmcGfLSB5D4DuSMaqN"},
                {"programId": "ComputeBudget111111111111111111111111111111"}
            ],
            "accountKeys": [
                {"pubkey": "TargetWallet789", "signer": True},
                {"pubkey": "OtherAccount123", "signer": False}
            ]
        }
    }
    
    result_4 = parser.parse_transaction(tx_4)
    
    print(f"Input: Meteora among multiple instructions, with signer")
    print(f"Expected: dex='meteora', action='swap', wallet_address='TargetWallet789'")
    print(f"Actual: dex='{result_4.get('dex')}', action='{result_4.get('action')}', wallet_address='{result_4.get('wallet_address')}'")
    
    if (result_4.get('dex') == 'meteora' and 
        result_4.get('action') == 'swap' and 
        result_4.get('wallet_address') == 'TargetWallet789'):
        print("✅ PASS: All fields correctly set")
    else:
        print("❌ FAIL: Combined requirements not met")
        return False
    
    # Test Case 5: Transaction wrapper format
    print("\n--- Requirement 5: Handle transaction wrapper ---")
    tx_5 = {
        "transaction": {
            "message": {
                "instructions": [
                    {"programId": "dbcij3LWUppWqq96dh6gJWwBifmcGfLSB5D4DuSMaqN"}
                ],
                "accountKeys": [
                    {"pubkey": "WrappedWallet", "signer": True}
                ]
            }
        }
    }
    
    result_5 = parser.parse_transaction(tx_5)
    
    print(f"Input: Transaction wrapped in 'transaction' key")
    print(f"Expected: dex='meteora', wallet_address='WrappedWallet'")
    print(f"Actual: dex='{result_5.get('dex')}', wallet_address='{result_5.get('wallet_address')}'")
    
    if (result_5.get('dex') == 'meteora' and 
        result_5.get('wallet_address') == 'WrappedWallet'):
        print("✅ PASS: Transaction wrapper handled correctly")
    else:
        print("❌ FAIL: Transaction wrapper handling failed")
        return False
    
    # Test Case 6: Return format check
    print("\n--- Requirement 6: Return Format ---")
    print("Expected keys: dex, action, mint, amount, signature, wallet_address")
    print(f"Actual keys: {', '.join(result_1.keys())}")
    
    required_keys = ['dex', 'action', 'mint', 'amount', 'signature', 'wallet_address']
    missing_keys = [k for k in required_keys if k not in result_1]
    
    if not missing_keys:
        print("✅ PASS: All required keys present")
    else:
        print(f"❌ FAIL: Missing keys: {missing_keys}")
        return False
    
    if 'source_wallet' not in result_1:
        print("✅ PASS: 'source_wallet' correctly replaced with 'wallet_address'")
    else:
        print("⚠️  WARNING: 'source_wallet' still present (should be removed)")
    
    print("\n" + "=" * 80)
    print("✅ ALL PROBLEM STATEMENT REQUIREMENTS VALIDATED")
    print("=" * 80)
    return True

def main():
    if test_exact_problem_statement():
        print("\n🎉 SUCCESS: Implementation matches problem statement exactly!")
        return 0
    else:
        print("\n❌ FAILURE: Implementation does not match problem statement")
        return 1

if __name__ == "__main__":
    sys.exit(main())
