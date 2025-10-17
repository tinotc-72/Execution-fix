#!/usr/bin/env python3
"""
Integration test for wallet_tx_parser.py meeting all problem statement requirements:
1. Detect DEX and action for Jupiter and Meteora
2. Set wallet_address from first signer or fallback to fee payer
3. Merge parsed fields into trade_info before defaults/validation
"""

from wallet_tx_parser import WalletTransactionParser, merge_parsed_fields

def test_jupiter_detection_and_merge():
    """Test Jupiter detection with proper DEX, action, and wallet_address"""
    print("\n" + "=" * 80)
    print("TEST 1: Jupiter Detection and Merge")
    print("=" * 80)
    
    # Simulate Jupiter transaction
    tx_data = {
        'message': {
            'instructions': [
                {'programId': 'JUP6LkbZbjS1jKKwapdHNy74zcZ3tLUZoi5QNyVTaV4'}
            ],
            'accountKeys': [
                {'pubkey': 'JupiterWallet123', 'signer': True}
            ]
        }
    }
    
    parser = WalletTransactionParser(None)
    parsed = parser.parse_transaction(tx_data)
    
    print(f"Parser output:")
    print(f"  dex: {parsed.get('dex')}")
    print(f"  action: {parsed.get('action')}")
    print(f"  wallet_address: {parsed.get('wallet_address')}")
    
    # Simulate trade_info before merge (with defaults)
    trade_info = {
        'dex': 'unknown',
        'action': None,
        'wallet_address': ''
    }
    
    # Merge parsed fields
    merge_parsed_fields(trade_info, parsed)
    
    print(f"\nAfter merge:")
    print(f"  dex: {trade_info.get('dex')}")
    print(f"  action: {trade_info.get('action')}")
    print(f"  wallet_address: {trade_info.get('wallet_address')}")
    
    # Verify
    assert trade_info['dex'] == 'jupiter', f"Expected jupiter, got {trade_info['dex']}"
    assert trade_info['action'] == 'swap', f"Expected swap, got {trade_info['action']}"
    assert trade_info['wallet_address'] == 'JupiterWallet123'
    
    print("\n✅ PASS: Jupiter correctly detected and merged")
    return True


def test_jupiter_logs_detection():
    """Test Jupiter detection from logs containing SharedAccountsRouteV2"""
    print("\n" + "=" * 80)
    print("TEST 2: Jupiter Detection from Logs")
    print("=" * 80)
    
    tx_data = {
        'message': {
            'instructions': [
                {'programId': 'SomeOtherProgram'}
            ],
            'accountKeys': []
        },
        'meta': {
            'logMessages': [
                'Program log: Instruction: SharedAccountsRouteV2',
                'Program JUP6LkbZ... invoke'
            ]
        }
    }
    
    parser = WalletTransactionParser(None)
    parsed = parser.parse_transaction(tx_data)
    
    print(f"Parser output:")
    print(f"  dex: {parsed.get('dex')}")
    print(f"  action: {parsed.get('action')}")
    
    assert parsed['dex'] == 'jupiter', f"Expected jupiter, got {parsed['dex']}"
    assert parsed['action'] == 'swap', f"Expected swap, got {parsed['action']}"
    
    print("\n✅ PASS: Jupiter detected from logs")
    return True


def test_meteora_detection_and_merge():
    """Test Meteora detection with proper DEX and action"""
    print("\n" + "=" * 80)
    print("TEST 3: Meteora Detection and Merge")
    print("=" * 80)
    
    tx_data = {
        'message': {
            'instructions': [
                {'programId': 'dbcij3LWUppWqq96dh6gJWwBifmcGfLSB5D4DuSMaqN'}
            ],
            'accountKeys': [
                {'pubkey': 'MeteoraWallet456', 'signer': True}
            ]
        }
    }
    
    parser = WalletTransactionParser(None)
    parsed = parser.parse_transaction(tx_data)
    
    print(f"Parser output:")
    print(f"  dex: {parsed.get('dex')}")
    print(f"  action: {parsed.get('action')}")
    print(f"  wallet_address: {parsed.get('wallet_address')}")
    
    # Merge
    trade_info = {'dex': 'unknown', 'action': None, 'wallet_address': ''}
    merge_parsed_fields(trade_info, parsed)
    
    print(f"\nAfter merge:")
    print(f"  dex: {trade_info.get('dex')}")
    print(f"  action: {trade_info.get('action')}")
    print(f"  wallet_address: {trade_info.get('wallet_address')}")
    
    assert trade_info['dex'] == 'meteora'
    assert trade_info['action'] == 'swap'
    assert trade_info['wallet_address'] == 'MeteoraWallet456'
    
    print("\n✅ PASS: Meteora correctly detected and merged")
    return True


def test_wallet_address_fallback():
    """Test wallet_address fallback to fee payer when no signer flag"""
    print("\n" + "=" * 80)
    print("TEST 4: Wallet Address Fallback")
    print("=" * 80)
    
    # Test with string accountKeys (v0 transaction format)
    tx_data = {
        'message': {
            'instructions': [
                {'programId': 'JUP6LkbZbjS1jKKwapdHNy74zcZ3tLUZoi5QNyVTaV4'}
            ],
            'accountKeys': ['FeePayerAddress', 'OtherAddress']
        }
    }
    
    parser = WalletTransactionParser(None)
    parsed = parser.parse_transaction(tx_data)
    
    print(f"Parser output (string format):")
    print(f"  wallet_address: {parsed.get('wallet_address')}")
    
    assert parsed['wallet_address'] == 'FeePayerAddress'
    print("✅ Correctly uses fee payer (accountKeys[0]) as fallback")
    
    # Test with dict accountKeys without signer flag
    tx_data2 = {
        'message': {
            'instructions': [
                {'programId': 'JUP6LkbZbjS1jKKwapdHNy74zcZ3tLUZoi5QNyVTaV4'}
            ],
            'accountKeys': [
                {'pubkey': 'FeePayerDict'},
                {'pubkey': 'OtherDict'}
            ]
        }
    }
    
    parsed2 = parser.parse_transaction(tx_data2)
    
    print(f"\nParser output (dict format):")
    print(f"  wallet_address: {parsed2.get('wallet_address')}")
    
    assert parsed2['wallet_address'] == 'FeePayerDict'
    print("✅ Correctly uses fee payer from dict format")
    
    print("\n✅ PASS: Wallet address fallback works correctly")
    return True


def test_merge_preserves_existing_values():
    """Test that merge does not overwrite existing non-empty values"""
    print("\n" + "=" * 80)
    print("TEST 5: Merge Preserves Existing Values")
    print("=" * 80)
    
    # Trade info already has valid values
    trade_info = {
        'dex': 'meteora',
        'action': 'buy',
        'wallet_address': 'ExistingWallet'
    }
    
    # Parser returns different values
    parsed = {
        'dex': 'jupiter',
        'action': 'swap',
        'wallet_address': 'NewWallet'
    }
    
    merge_parsed_fields(trade_info, parsed)
    
    print(f"After merge:")
    print(f"  dex: {trade_info.get('dex')} (should remain 'meteora')")
    print(f"  action: {trade_info.get('action')} (should remain 'buy')")
    print(f"  wallet_address: {trade_info.get('wallet_address')} (should remain 'ExistingWallet')")
    
    assert trade_info['dex'] == 'meteora', "Should not overwrite existing dex"
    assert trade_info['action'] == 'buy', "Should not overwrite existing action"
    assert trade_info['wallet_address'] == 'ExistingWallet', "Should not overwrite existing wallet"
    
    print("\n✅ PASS: Existing values preserved correctly")
    return True


def test_merge_replaces_unknown_and_pending():
    """Test that merge replaces 'unknown' and 'PENDING_ANALYSIS' values"""
    print("\n" + "=" * 80)
    print("TEST 6: Merge Replaces Unknown/Pending Values")
    print("=" * 80)
    
    trade_info = {
        'dex': 'unknown',
        'action': 'PENDING_ANALYSIS',
        'wallet_address': '',
        'token_mint': None
    }
    
    parsed = {
        'dex': 'jupiter',
        'action': 'swap',
        'wallet_address': 'DetectedWallet',
        'mint': 'TokenMintAddress'
    }
    
    merge_parsed_fields(trade_info, parsed)
    
    print(f"After merge:")
    print(f"  dex: {trade_info.get('dex')} (should be 'jupiter')")
    print(f"  action: {trade_info.get('action')} (should be 'swap')")
    print(f"  wallet_address: {trade_info.get('wallet_address')} (should be 'DetectedWallet')")
    print(f"  token_mint: {trade_info.get('token_mint')} (should be 'TokenMintAddress')")
    
    assert trade_info['dex'] == 'jupiter'
    assert trade_info['action'] == 'swap'
    assert trade_info['wallet_address'] == 'DetectedWallet'
    assert trade_info['token_mint'] == 'TokenMintAddress'
    
    print("\n✅ PASS: Unknown/pending values replaced correctly")
    return True


def main():
    """Run all integration tests"""
    print("\n" + "=" * 80)
    print("PARSER INTEGRATION TESTS - Problem Statement Requirements")
    print("=" * 80)
    
    tests = [
        ("Jupiter Detection and Merge", test_jupiter_detection_and_merge),
        ("Jupiter Detection from Logs", test_jupiter_logs_detection),
        ("Meteora Detection and Merge", test_meteora_detection_and_merge),
        ("Wallet Address Fallback", test_wallet_address_fallback),
        ("Merge Preserves Existing Values", test_merge_preserves_existing_values),
        ("Merge Replaces Unknown/Pending", test_merge_replaces_unknown_and_pending),
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
            print(f"❌ FAIL: {test_name} - {e}")
            import traceback
            traceback.print_exc()
    
    print("\n" + "=" * 80)
    print(f"FINAL RESULTS: {passed} passed, {failed} failed")
    print("=" * 80)
    
    if failed == 0:
        print("\n✅ ALL INTEGRATION TESTS PASSED")
        print("\nProblem Statement Requirements Met:")
        print("  1. ✅ Jupiter DEX detected by programId or logs (SharedAccountsRouteV2)")
        print("  2. ✅ Meteora DEX detected by programId")
        print("  3. ✅ Action set to 'swap' for both Jupiter and Meteora")
        print("  4. ✅ wallet_address extracted from first signer")
        print("  5. ✅ wallet_address falls back to accountKeys[0] (fee payer)")
        print("  6. ✅ merge_parsed_fields merges parser results into trade_info")
        print("  7. ✅ Merge only updates empty/unknown/PENDING_ANALYSIS fields")
        print("  8. ✅ Merge preserves existing valid values")
        return 0
    else:
        print("\n❌ SOME TESTS FAILED")
        return 1


if __name__ == "__main__":
    import sys
    sys.exit(main())
