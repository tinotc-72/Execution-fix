#!/usr/bin/env python3
"""
Comprehensive tests for DEX detection and signer extraction requirements.

Tests verify:
1. Jupiter detection by programId (JUP6LkbZ...)
2. Jupiter detection by logs (SharedAccountsRouteV2)
3. Meteora detection by both programIds (dbcij3LW... and Eo7WjKq...)
4. Wallet address extraction from signers
5. Wallet address fallback to accountKeys[0] (fee payer)
6. merge_parsed_fields function properly merges without overwriting
"""

import sys
import os

# Mock classes to avoid dependency issues
class MockLogger:
    def __init__(self):
        self.logs = []
    
    def info(self, msg, *args, **kwargs):
        self.logs.append(('INFO', msg))
    
    def debug(self, msg, *args, **kwargs):
        self.logs.append(('DEBUG', msg))
    
    def warning(self, msg, *args, **kwargs):
        self.logs.append(('WARNING', msg))
    
    def error(self, msg, *args, **kwargs):
        self.logs.append(('ERROR', msg))

class MockRPCClient:
    pass

class MockDEXDecoder:
    def decode(self, dex_type, tx_data):
        return {
            "dex": "Unknown",
            "parsed": False,
        }


def test_jupiter_detection_by_program_id():
    """Test: Detect Jupiter by programId == JUP6LkbZbjS1jKKwapdHNy74zcZ3tLUZoi5QNyVTaV4"""
    print("\n=== TEST: Jupiter Detection by programId ===")
    
    from wallet_tx_parser import WalletTransactionParser
    
    parser = WalletTransactionParser(MockRPCClient())
    parser.logger = MockLogger()
    parser.dex_decoder = MockDEXDecoder()
    
    tx_data = {
        "message": {
            "instructions": [
                {"programId": "JUP6LkbZbjS1jKKwapdHNy74zcZ3tLUZoi5QNyVTaV4"}
            ],
            "accountKeys": [
                {"pubkey": "TestWallet123", "signer": True}
            ]
        }
    }
    
    result = parser.parse_transaction(tx_data)
    
    assert result["dex"] == "jupiter", f"Expected dex='jupiter', got '{result['dex']}'"
    assert result["action"] == "swap", f"Expected action='swap', got '{result['action']}'"
    assert result["wallet_address"] == "TestWallet123", f"Expected wallet_address='TestWallet123', got '{result['wallet_address']}'"
    
    # Verify logger was called
    assert any("Jupiter detected" in str(log) for log in parser.logger.logs), "Parser should log Jupiter detection"
    
    print("✅ PASS: Jupiter detected by programId")
    print(f"   - dex: {result['dex']}")
    print(f"   - action: {result['action']}")
    print(f"   - wallet_address: {result['wallet_address']}")
    return True


def test_jupiter_detection_by_logs():
    """Test: Detect Jupiter by logs containing SharedAccountsRouteV2"""
    print("\n=== TEST: Jupiter Detection by SharedAccountsRouteV2 in logs ===")
    
    from wallet_tx_parser import WalletTransactionParser
    
    parser = WalletTransactionParser(MockRPCClient())
    parser.logger = MockLogger()
    parser.dex_decoder = MockDEXDecoder()
    
    tx_data = {
        "message": {
            "instructions": [
                {"programId": "SomeOtherProgram"}
            ],
            "accountKeys": [
                {"pubkey": "TestWallet456", "signer": True}
            ]
        },
        "meta": {
            "logMessages": [
                "Program log: Instruction: SharedAccountsRouteV2",
                "Program log: Some other message"
            ]
        }
    }
    
    result = parser.parse_transaction(tx_data)
    
    assert result["dex"] == "jupiter", f"Expected dex='jupiter', got '{result['dex']}'"
    assert result["action"] == "swap", f"Expected action='swap', got '{result['action']}'"
    
    # Verify logger was called
    assert any("Jupiter detected" in str(log) for log in parser.logger.logs), "Parser should log Jupiter detection"
    
    print("✅ PASS: Jupiter detected by SharedAccountsRouteV2 in logs")
    print(f"   - dex: {result['dex']}")
    print(f"   - action: {result['action']}")
    return True


def test_meteora_detection_primary_pid():
    """Test: Detect Meteora by programId == dbcij3LWUppWqq96dh6gJWwBifmcGfLSB5D4DuSMaqN"""
    print("\n=== TEST: Meteora Detection by primary programId (dbcij3LW...) ===")
    
    from wallet_tx_parser import WalletTransactionParser
    
    parser = WalletTransactionParser(MockRPCClient())
    parser.logger = MockLogger()
    parser.dex_decoder = MockDEXDecoder()
    
    tx_data = {
        "message": {
            "instructions": [
                {"programId": "dbcij3LWUppWqq96dh6gJWwBifmcGfLSB5D4DuSMaqN"}
            ],
            "accountKeys": [
                {"pubkey": "MeteoraWallet1", "signer": True}
            ]
        }
    }
    
    result = parser.parse_transaction(tx_data)
    
    assert result["dex"] == "meteora", f"Expected dex='meteora', got '{result['dex']}'"
    assert result["action"] == "swap", f"Expected action='swap', got '{result['action']}'"
    assert result["wallet_address"] == "MeteoraWallet1", f"Expected wallet_address='MeteoraWallet1', got '{result['wallet_address']}'"
    
    # Verify logger was called
    assert any("Meteora detected" in str(log) for log in parser.logger.logs), "Parser should log Meteora detection"
    
    print("✅ PASS: Meteora detected by primary programId")
    print(f"   - dex: {result['dex']}")
    print(f"   - action: {result['action']}")
    print(f"   - wallet_address: {result['wallet_address']}")
    return True


def test_meteora_detection_alt_pid():
    """Test: Detect Meteora by alt programId == Eo7WjKq67rjJQSZxS6z3YkapzY3eMj6Xy8X5EQVn5UaB"""
    print("\n=== TEST: Meteora Detection by alt programId (Eo7WjKq...) ===")
    
    from wallet_tx_parser import WalletTransactionParser
    
    parser = WalletTransactionParser(MockRPCClient())
    parser.logger = MockLogger()
    parser.dex_decoder = MockDEXDecoder()
    
    tx_data = {
        "message": {
            "instructions": [
                {"programId": "Eo7WjKq67rjJQSZxS6z3YkapzY3eMj6Xy8X5EQVn5UaB"}
            ],
            "accountKeys": [
                {"pubkey": "MeteoraWallet2", "signer": True}
            ]
        }
    }
    
    result = parser.parse_transaction(tx_data)
    
    assert result["dex"] == "meteora", f"Expected dex='meteora', got '{result['dex']}'"
    assert result["action"] == "swap", f"Expected action='swap', got '{result['action']}'"
    assert result["wallet_address"] == "MeteoraWallet2", f"Expected wallet_address='MeteoraWallet2', got '{result['wallet_address']}'"
    
    # Verify logger was called
    assert any("Meteora detected" in str(log) for log in parser.logger.logs), "Parser should log Meteora detection"
    
    print("✅ PASS: Meteora detected by alt programId")
    print(f"   - dex: {result['dex']}")
    print(f"   - action: {result['action']}")
    print(f"   - wallet_address: {result['wallet_address']}")
    return True


def test_wallet_address_from_signer():
    """Test: Set wallet_address from first signer"""
    print("\n=== TEST: wallet_address from first signer ===")
    
    from wallet_tx_parser import WalletTransactionParser
    
    parser = WalletTransactionParser(MockRPCClient())
    parser.logger = MockLogger()
    parser.dex_decoder = MockDEXDecoder()
    
    tx_data = {
        "message": {
            "instructions": [],
            "accountKeys": [
                {"pubkey": "FirstSigner", "signer": True},
                {"pubkey": "SecondSigner", "signer": True},
                {"pubkey": "NonSigner", "signer": False}
            ]
        }
    }
    
    result = parser.parse_transaction(tx_data)
    
    assert result["wallet_address"] == "FirstSigner", f"Expected wallet_address='FirstSigner', got '{result['wallet_address']}'"
    
    print("✅ PASS: wallet_address set from first signer")
    print(f"   - wallet_address: {result['wallet_address']}")
    return True


def test_wallet_address_fallback_string_format():
    """Test: Set wallet_address from accountKeys[0] when signer flags missing (string format)"""
    print("\n=== TEST: wallet_address fallback (string format, fee payer) ===")
    
    from wallet_tx_parser import WalletTransactionParser
    
    parser = WalletTransactionParser(MockRPCClient())
    parser.logger = MockLogger()
    parser.dex_decoder = MockDEXDecoder()
    
    # Case: accountKeys are strings (v0 format)
    tx_data = {
        "message": {
            "instructions": [],
            "accountKeys": ["FeePayerAddress", "OtherAddress"]
        }
    }
    
    result = parser.parse_transaction(tx_data)
    
    assert result["wallet_address"] == "FeePayerAddress", f"Expected wallet_address='FeePayerAddress', got '{result['wallet_address']}'"
    
    print("✅ PASS: wallet_address set from accountKeys[0] (string format)")
    print(f"   - wallet_address: {result['wallet_address']}")
    return True


def test_wallet_address_fallback_dict_format():
    """Test: Set wallet_address from accountKeys[0] when signer flags missing (dict format)"""
    print("\n=== TEST: wallet_address fallback (dict format without signer flag) ===")
    
    from wallet_tx_parser import WalletTransactionParser
    
    parser = WalletTransactionParser(MockRPCClient())
    parser.logger = MockLogger()
    parser.dex_decoder = MockDEXDecoder()
    
    # Case: accountKeys are dicts without signer flag
    tx_data = {
        "message": {
            "instructions": [],
            "accountKeys": [
                {"pubkey": "FeePayerDict"},
                {"pubkey": "OtherDict"}
            ]
        }
    }
    
    result = parser.parse_transaction(tx_data)
    
    assert result["wallet_address"] == "FeePayerDict", f"Expected wallet_address='FeePayerDict', got '{result['wallet_address']}'"
    
    print("✅ PASS: wallet_address set from accountKeys[0] (dict format without signer)")
    print(f"   - wallet_address: {result['wallet_address']}")
    return True


def test_merge_parsed_fields_basic():
    """Test: merge_parsed_fields merges fields from parser to trade_info"""
    print("\n=== TEST: merge_parsed_fields basic functionality ===")
    
    from wallet_tx_parser import merge_parsed_fields
    
    trade_info = {
        "dex": None,
        "action": "",
        "wallet_address": "unknown",
        "signature": "PENDING_ANALYSIS"
    }
    
    parsed = {
        "dex": "jupiter",
        "action": "swap",
        "wallet_address": "RealWallet123",
        "signature": "RealSignature456"
    }
    
    merge_parsed_fields(trade_info, parsed)
    
    assert trade_info["dex"] == "jupiter", f"Expected dex='jupiter', got '{trade_info['dex']}'"
    assert trade_info["action"] == "swap", f"Expected action='swap', got '{trade_info['action']}'"
    assert trade_info["wallet_address"] == "RealWallet123", f"Expected wallet_address='RealWallet123', got '{trade_info['wallet_address']}'"
    assert trade_info["signature"] == "RealSignature456", f"Expected signature='RealSignature456', got '{trade_info['signature']}'"
    
    print("✅ PASS: merge_parsed_fields merges all fields correctly")
    print(f"   - dex: {trade_info['dex']}")
    print(f"   - action: {trade_info['action']}")
    print(f"   - wallet_address: {trade_info['wallet_address']}")
    print(f"   - signature: {trade_info['signature']}")
    return True


def test_merge_parsed_fields_no_overwrite():
    """Test: merge_parsed_fields does NOT overwrite valid existing values"""
    print("\n=== TEST: merge_parsed_fields does NOT overwrite valid values ===")
    
    from wallet_tx_parser import merge_parsed_fields
    
    trade_info = {
        "dex": "existing_dex",
        "action": "existing_action",
        "wallet_address": "ExistingWallet",
        "signature": "ExistingSignature"
    }
    
    parsed = {
        "dex": "new_dex",
        "action": "new_action",
        "wallet_address": "NewWallet",
        "signature": "NewSignature"
    }
    
    merge_parsed_fields(trade_info, parsed)
    
    # Should NOT have overwritten valid existing values
    assert trade_info["dex"] == "existing_dex", f"Should not overwrite valid dex"
    assert trade_info["action"] == "existing_action", f"Should not overwrite valid action"
    assert trade_info["wallet_address"] == "ExistingWallet", f"Should not overwrite valid wallet_address"
    assert trade_info["signature"] == "ExistingSignature", f"Should not overwrite valid signature"
    
    print("✅ PASS: merge_parsed_fields preserves valid existing values")
    print(f"   - All original values retained")
    return True


def test_merge_parsed_fields_handles_nested_parsed_tx():
    """Test: merge_parsed_fields handles nested parsed_tx structure"""
    print("\n=== TEST: merge_parsed_fields handles nested parsed_tx ===")
    
    from wallet_tx_parser import merge_parsed_fields
    
    trade_info = {
        "dex": None,
        "action": None
    }
    
    # Nested structure (some code paths store result under "parsed_tx")
    parsed = {
        "parsed_tx": {
            "dex": "meteora",
            "action": "swap"
        }
    }
    
    merge_parsed_fields(trade_info, parsed)
    
    assert trade_info["dex"] == "meteora", f"Expected dex='meteora', got '{trade_info['dex']}'"
    assert trade_info["action"] == "swap", f"Expected action='swap', got '{trade_info['action']}'"
    
    print("✅ PASS: merge_parsed_fields handles nested parsed_tx structure")
    print(f"   - dex: {trade_info['dex']}")
    print(f"   - action: {trade_info['action']}")
    return True


def test_merge_parsed_fields_mint_mapping():
    """Test: merge_parsed_fields maps 'mint' to 'token_mint'"""
    print("\n=== TEST: merge_parsed_fields maps 'mint' to 'token_mint' ===")
    
    from wallet_tx_parser import merge_parsed_fields
    
    trade_info = {
        "token_mint": None
    }
    
    # Parser returns 'mint' but trade_info uses 'token_mint'
    parsed = {
        "mint": "TokenMintAddress123"
    }
    
    merge_parsed_fields(trade_info, parsed)
    
    assert trade_info["token_mint"] == "TokenMintAddress123", f"Expected token_mint='TokenMintAddress123', got '{trade_info.get('token_mint')}'"
    
    print("✅ PASS: merge_parsed_fields maps 'mint' to 'token_mint'")
    print(f"   - token_mint: {trade_info['token_mint']}")
    return True


def test_integration_jupiter_end_to_end():
    """Test: Full end-to-end Jupiter transaction parsing and merging"""
    print("\n=== TEST: Integration - Jupiter end-to-end ===")
    
    from wallet_tx_parser import WalletTransactionParser, merge_parsed_fields
    
    parser = WalletTransactionParser(MockRPCClient())
    parser.logger = MockLogger()
    parser.dex_decoder = MockDEXDecoder()
    
    # Simulate a full Jupiter transaction
    tx_data = {
        "signature": "JupiterTxSignature123",
        "message": {
            "instructions": [
                {"programId": "JUP6LkbZbjS1jKKwapdHNy74zcZ3tLUZoi5QNyVTaV4"}
            ],
            "accountKeys": [
                {"pubkey": "JupiterUserWallet", "signer": True}
            ]
        },
        "meta": {
            "logMessages": [
                "Program JUP6LkbZbjS1jKKwapdHNy74zcZ3tLUZoi5QNyVTaV4 invoke [1]",
                "Program log: Instruction: SharedAccountsRouteV2"
            ]
        }
    }
    
    # Initial trade_info with defaults
    trade_info = {
        "dex": "unknown",
        "action": "unknown",
        "wallet_address": None,
        "signature": None
    }
    
    # Step 1: Parse transaction
    parsed = parser.parse_transaction(tx_data)
    
    # Step 2: Merge parsed fields
    merge_parsed_fields(trade_info, parsed)
    
    # Verify all fields are correctly set
    assert trade_info["dex"] == "jupiter", f"Expected dex='jupiter', got '{trade_info['dex']}'"
    assert trade_info["action"] == "swap", f"Expected action='swap', got '{trade_info['action']}'"
    assert trade_info["wallet_address"] == "JupiterUserWallet", f"Expected wallet_address='JupiterUserWallet', got '{trade_info['wallet_address']}'"
    assert trade_info["signature"] == "JupiterTxSignature123", f"Expected signature='JupiterTxSignature123', got '{trade_info['signature']}'"
    
    print("✅ PASS: Integration - Jupiter end-to-end")
    print(f"   - dex: {trade_info['dex']}")
    print(f"   - action: {trade_info['action']}")
    print(f"   - wallet_address: {trade_info['wallet_address']}")
    print(f"   - signature: {trade_info['signature']}")
    return True


def test_integration_meteora_end_to_end():
    """Test: Full end-to-end Meteora transaction parsing and merging"""
    print("\n=== TEST: Integration - Meteora end-to-end ===")
    
    from wallet_tx_parser import WalletTransactionParser, merge_parsed_fields
    
    parser = WalletTransactionParser(MockRPCClient())
    parser.logger = MockLogger()
    parser.dex_decoder = MockDEXDecoder()
    
    # Simulate a full Meteora transaction with alt PID
    tx_data = {
        "signature": "MeteoraTxSignature789",
        "message": {
            "instructions": [
                {"programId": "Eo7WjKq67rjJQSZxS6z3YkapzY3eMj6Xy8X5EQVn5UaB"}
            ],
            "accountKeys": [
                {"pubkey": "MeteoraUserWallet", "signer": True}
            ]
        }
    }
    
    # Initial trade_info with defaults/unknowns
    trade_info = {
        "dex": "",
        "action": "PENDING_ANALYSIS",
        "wallet_address": "unknown",
        "signature": ""
    }
    
    # Step 1: Parse transaction
    parsed = parser.parse_transaction(tx_data)
    
    # Step 2: Merge parsed fields
    merge_parsed_fields(trade_info, parsed)
    
    # Verify all fields are correctly set
    assert trade_info["dex"] == "meteora", f"Expected dex='meteora', got '{trade_info['dex']}'"
    assert trade_info["action"] == "swap", f"Expected action='swap', got '{trade_info['action']}'"
    assert trade_info["wallet_address"] == "MeteoraUserWallet", f"Expected wallet_address='MeteoraUserWallet', got '{trade_info['wallet_address']}'"
    assert trade_info["signature"] == "MeteoraTxSignature789", f"Expected signature='MeteoraTxSignature789', got '{trade_info['signature']}'"
    
    print("✅ PASS: Integration - Meteora end-to-end")
    print(f"   - dex: {trade_info['dex']}")
    print(f"   - action: {trade_info['action']}")
    print(f"   - wallet_address: {trade_info['wallet_address']}")
    print(f"   - signature: {trade_info['signature']}")
    return True


def main():
    """Run all tests"""
    print("=" * 80)
    print("COMPREHENSIVE DEX AND SIGNER REQUIREMENTS TESTS")
    print("=" * 80)
    print("\nTesting requirements from problem statement:")
    print("1. Jupiter detection by programId (JUP6LkbZ...)")
    print("2. Jupiter detection by logs (SharedAccountsRouteV2)")
    print("3. Meteora detection by both programIds (dbcij3LW... and Eo7WjKq...)")
    print("4. Wallet address from first signer")
    print("5. Wallet address fallback to accountKeys[0] (fee payer)")
    print("6. merge_parsed_fields properly merges fields")
    print("7. merge_parsed_fields does NOT overwrite valid values")
    print("=" * 80)
    
    tests = [
        ("Jupiter Detection by programId", test_jupiter_detection_by_program_id),
        ("Jupiter Detection by logs", test_jupiter_detection_by_logs),
        ("Meteora Detection by primary PID", test_meteora_detection_primary_pid),
        ("Meteora Detection by alt PID", test_meteora_detection_alt_pid),
        ("wallet_address from signer", test_wallet_address_from_signer),
        ("wallet_address fallback (string)", test_wallet_address_fallback_string_format),
        ("wallet_address fallback (dict)", test_wallet_address_fallback_dict_format),
        ("merge_parsed_fields basic", test_merge_parsed_fields_basic),
        ("merge_parsed_fields no overwrite", test_merge_parsed_fields_no_overwrite),
        ("merge_parsed_fields nested", test_merge_parsed_fields_handles_nested_parsed_tx),
        ("merge_parsed_fields mint mapping", test_merge_parsed_fields_mint_mapping),
        ("Integration - Jupiter E2E", test_integration_jupiter_end_to_end),
        ("Integration - Meteora E2E", test_integration_meteora_end_to_end),
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
        except AssertionError as e:
            failed += 1
            print(f"❌ FAIL: {test_name} - {e}")
        except Exception as e:
            failed += 1
            print(f"❌ FAIL: {test_name} - {e}")
            import traceback
            traceback.print_exc()
    
    print("\n" + "=" * 80)
    print(f"RESULTS: {passed} passed, {failed} failed")
    print("=" * 80)
    
    if failed == 0:
        print("\n✅ ALL REQUIREMENTS VERIFIED!")
        print("\nImplementation Summary:")
        print("  ✅ Jupiter detected by programId (JUP6LkbZbjS1jKKwapdHNy74zcZ3tLUZoi5QNyVTaV4)")
        print("  ✅ Jupiter detected by logs (SharedAccountsRouteV2)")
        print("  ✅ Meteora detected by primary PID (dbcij3LWUppWqq96dh6gJWwBifmcGfLSB5D4DuSMaqN)")
        print("  ✅ Meteora detected by alt PID (Eo7WjKq67rjJQSZxS6z3YkapzY3eMj6Xy8X5EQVn5UaB)")
        print("  ✅ Wallet address extracted from first signer")
        print("  ✅ Wallet address fallback to accountKeys[0] (fee payer)")
        print("  ✅ merge_parsed_fields merges parser fields into trade_info")
        print("  ✅ merge_parsed_fields preserves valid existing values")
        print("  ✅ merge_parsed_fields handles all field mappings correctly")
        print("\nThe parser consistently sets dex/signer, and merge prevents defaults from")
        print("overwriting valid values. Routing sees correct DEX and real signer.")
    else:
        print("\n❌ SOME TESTS FAILED - Review implementation")
    
    return 0 if failed == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
