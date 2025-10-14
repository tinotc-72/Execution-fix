#!/usr/bin/env python3
"""
Test to verify both Meteora program IDs are detected correctly.
Tests the updated METEORA_PROGRAM_IDS set implementation.
"""

import sys
import os

# Add the current directory to the path to import wallet_tx_parser
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_meteora_program_ids_constant():
    """Test that METEORA_PROGRAM_IDS constant is defined with both IDs"""
    print("=" * 80)
    print("TEST: METEORA_PROGRAM_IDS Constant Definition")
    print("=" * 80)
    
    from wallet_tx_parser import METEORA_PROGRAM_IDS
    
    expected_ids = {
        "Eo7WjKq67rjJQSZxS6z3YkapzY3eMj6Xy8X5EQVn5UaB",  # Meteora AMM
        "dbcij3LWUppWqq96dh6gJWwBifmcGfLSB5D4DuSMaqN",  # Meteora alternate ID
    }
    
    print(f"\nExpected IDs: {expected_ids}")
    print(f"Actual IDs:   {METEORA_PROGRAM_IDS}")
    
    if METEORA_PROGRAM_IDS == expected_ids:
        print("✅ PASS: METEORA_PROGRAM_IDS contains both expected program IDs")
        return True
    else:
        print("❌ FAIL: METEORA_PROGRAM_IDS does not match expected set")
        missing = expected_ids - METEORA_PROGRAM_IDS
        extra = METEORA_PROGRAM_IDS - expected_ids
        if missing:
            print(f"  Missing: {missing}")
        if extra:
            print(f"  Extra: {extra}")
        return False

def test_meteora_detection_both_ids():
    """Test that both Meteora program IDs are detected"""
    print("\n" + "=" * 80)
    print("TEST: Detection of Both Meteora Program IDs")
    print("=" * 80)
    
    from wallet_tx_parser import WalletTransactionParser
    
    class MockRPCClient:
        pass
    
    parser = WalletTransactionParser(MockRPCClient())
    
    # Test case 1: First Meteora ID (original)
    test_cases = [
        {
            "name": "Meteora AMM (Eo7W...)",
            "program_id": "Eo7WjKq67rjJQSZxS6z3YkapzY3eMj6Xy8X5EQVn5UaB",
            "tx_data": {
                "signature": "test_sig_eo7w",
                "message": {
                    "instructions": [
                        {"programId": "Eo7WjKq67rjJQSZxS6z3YkapzY3eMj6Xy8X5EQVn5UaB"}
                    ],
                    "accountKeys": [
                        {"pubkey": "WalletEo7W", "signer": True}
                    ]
                }
            }
        },
        {
            "name": "Meteora Alternate (dbci...)",
            "program_id": "dbcij3LWUppWqq96dh6gJWwBifmcGfLSB5D4DuSMaqN",
            "tx_data": {
                "signature": "test_sig_dbci",
                "message": {
                    "instructions": [
                        {"programId": "dbcij3LWUppWqq96dh6gJWwBifmcGfLSB5D4DuSMaqN"}
                    ],
                    "accountKeys": [
                        {"pubkey": "WalletDbci", "signer": True}
                    ]
                }
            }
        },
        {
            "name": "Non-Meteora Program",
            "program_id": "11111111111111111111111111111111",
            "tx_data": {
                "signature": "test_sig_other",
                "message": {
                    "instructions": [
                        {"programId": "11111111111111111111111111111111"}
                    ],
                    "accountKeys": [
                        {"pubkey": "WalletOther", "signer": True}
                    ]
                }
            }
        }
    ]
    
    all_passed = True
    
    for test_case in test_cases:
        print(f"\nTest Case: {test_case['name']}")
        print(f"  Program ID: {test_case['program_id']}")
        
        result = parser.parse_transaction(test_case['tx_data'])
        
        print(f"  Result DEX: {result.get('dex')}")
        print(f"  Result Action: {result.get('action')}")
        print(f"  Result Wallet: {result.get('wallet_address')}")
        
        # Check expectations
        if test_case['program_id'] in ["Eo7WjKq67rjJQSZxS6z3YkapzY3eMj6Xy8X5EQVn5UaB", "dbcij3LWUppWqq96dh6gJWwBifmcGfLSB5D4DuSMaqN"]:
            # Should detect as Meteora
            if result.get('dex') == 'meteora':
                print("  ✅ PASS: DEX correctly detected as 'meteora'")
            else:
                print(f"  ❌ FAIL: Expected dex='meteora', got '{result.get('dex')}'")
                all_passed = False
            
            if result.get('action') == 'swap':
                print("  ✅ PASS: Action correctly set to 'swap'")
            else:
                print(f"  ❌ FAIL: Expected action='swap', got '{result.get('action')}'")
                all_passed = False
        else:
            # Should NOT detect as Meteora (will be unknown or other DEX)
            if result.get('dex') != 'meteora':
                print(f"  ✅ PASS: DEX correctly NOT detected as Meteora (got '{result.get('dex')}')")
            else:
                print("  ❌ FAIL: Should not detect as Meteora")
                all_passed = False
    
    return all_passed

def test_wallet_address_extraction():
    """Test that wallet_address is correctly extracted from signers"""
    print("\n" + "=" * 80)
    print("TEST: Wallet Address Extraction")
    print("=" * 80)
    
    from wallet_tx_parser import WalletTransactionParser
    
    class MockRPCClient:
        pass
    
    parser = WalletTransactionParser(MockRPCClient())
    
    tx_data = {
        "signature": "test_sig",
        "message": {
            "instructions": [
                {"programId": "Eo7WjKq67rjJQSZxS6z3YkapzY3eMj6Xy8X5EQVn5UaB"}
            ],
            "accountKeys": [
                {"pubkey": "FirstSigner123", "signer": True},
                {"pubkey": "SecondSigner456", "signer": True},
                {"pubkey": "NotASigner789", "signer": False}
            ]
        }
    }
    
    result = parser.parse_transaction(tx_data)
    
    print(f"\nWallet address extracted: {result.get('wallet_address')}")
    
    if result.get('wallet_address') == 'FirstSigner123':
        print("✅ PASS: First signer correctly extracted as wallet_address")
        return True
    else:
        print(f"❌ FAIL: Expected 'FirstSigner123', got '{result.get('wallet_address')}'")
        return False

def main():
    """Run all tests"""
    print("\n🧪 Testing Meteora Program IDs Detection\n")
    
    test_results = []
    
    # Test 1: Constant definition
    test_results.append(("METEORA_PROGRAM_IDS constant", test_meteora_program_ids_constant()))
    
    # Test 2: Detection of both IDs
    test_results.append(("Detection of both program IDs", test_meteora_detection_both_ids()))
    
    # Test 3: Wallet address extraction
    test_results.append(("Wallet address extraction", test_wallet_address_extraction()))
    
    # Summary
    print("\n" + "=" * 80)
    print("TEST SUMMARY")
    print("=" * 80)
    
    all_passed = True
    for test_name, passed in test_results:
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"  {status}: {test_name}")
        if not passed:
            all_passed = False
    
    if all_passed:
        print("\n🎉 ALL TESTS PASSED!")
        return 0
    else:
        print("\n❌ SOME TESTS FAILED")
        return 1

if __name__ == "__main__":
    sys.exit(main())
