#!/usr/bin/env python3
"""
Test requirements from problem statement for wallet_tx_parser.py
"""

# Mock classes to avoid dependency issues
class MockLogger:
    def info(self, *args, **kwargs):
        pass
    def debug(self, *args, **kwargs):
        pass
    def warning(self, *args, **kwargs):
        pass
    def error(self, *args, **kwargs):
        pass

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
    
    # Create a minimal parser without dependencies
    import sys
    import os
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    
    # Import after mocking
    import logging
    logging.basicConfig(level=logging.INFO)
    
    from wallet_tx_parser import WalletTransactionParser
    
    # Mock the decoder
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
    print("✅ PASS: Jupiter detected by programId")
    return True

def test_jupiter_detection_by_logs():
    """Test: Detect Jupiter by logs containing SharedAccountsRouteV2"""
    print("\n=== TEST: Jupiter Detection by SharedAccountsRouteV2 in logs ===")
    
    import sys
    import os
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    
    from wallet_tx_parser import WalletTransactionParser
    
    parser = WalletTransactionParser(MockRPCClient())
    parser.logger = MockLogger()
    parser.dex_decoder = MockDEXDecoder()
    
    tx_data = {
        "message": {
            "instructions": [
                {"programId": "SomeOtherProgram"}
            ],
            "accountKeys": []
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
    print("✅ PASS: Jupiter detected by SharedAccountsRouteV2 in logs")
    return True

def test_meteora_detection():
    """Test: Detect Meteora by programId == dbcij3LWUppWqq96dh6gJWwBifmcGfLSB5D4DuSMaqN"""
    print("\n=== TEST: Meteora Detection by programId ===")
    
    import sys
    import os
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    
    from wallet_tx_parser import WalletTransactionParser
    
    parser = WalletTransactionParser(MockRPCClient())
    parser.logger = MockLogger()
    parser.dex_decoder = MockDEXDecoder()
    
    tx_data = {
        "message": {
            "instructions": [
                {"programId": "dbcij3LWUppWqq96dh6gJWwBifmcGfLSB5D4DuSMaqN"}
            ],
            "accountKeys": []
        }
    }
    
    result = parser.parse_transaction(tx_data)
    
    assert result["dex"] == "meteora", f"Expected dex='meteora', got '{result['dex']}'"
    assert result["action"] == "swap", f"Expected action='swap', got '{result['action']}'"
    print("✅ PASS: Meteora detected by programId")
    return True

def test_wallet_address_from_signer():
    """Test: Set wallet_address from first signer"""
    print("\n=== TEST: wallet_address from first signer ===")
    
    import sys
    import os
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    
    from wallet_tx_parser import WalletTransactionParser
    
    parser = WalletTransactionParser(MockRPCClient())
    parser.logger = MockLogger()
    parser.dex_decoder = MockDEXDecoder()
    
    tx_data = {
        "message": {
            "instructions": [],
            "accountKeys": [
                {"pubkey": "FirstSigner", "signer": True},
                {"pubkey": "SecondSigner", "signer": True}
            ]
        }
    }
    
    result = parser.parse_transaction(tx_data)
    
    assert result["wallet_address"] == "FirstSigner", f"Expected wallet_address='FirstSigner', got '{result['wallet_address']}'"
    print("✅ PASS: wallet_address set from first signer")
    return True

def test_wallet_address_fallback():
    """Test: Set wallet_address from accountKeys[0] when signer flags missing"""
    print("\n=== TEST: wallet_address fallback when signer flags missing ===")
    
    import sys
    import os
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    
    from wallet_tx_parser import WalletTransactionParser
    
    parser = WalletTransactionParser(MockRPCClient())
    parser.logger = MockLogger()
    parser.dex_decoder = MockDEXDecoder()
    
    # Case 1: accountKeys are strings (v0 format)
    tx_data = {
        "message": {
            "instructions": [],
            "accountKeys": ["FeePayerAddress", "OtherAddress"]
        }
    }
    
    result = parser.parse_transaction(tx_data)
    
    assert result["wallet_address"] == "FeePayerAddress", f"Expected wallet_address='FeePayerAddress', got '{result['wallet_address']}'"
    print("✅ PASS: wallet_address set from accountKeys[0] (string format)")
    
    # Case 2: accountKeys are dicts without signer flag
    tx_data2 = {
        "message": {
            "instructions": [],
            "accountKeys": [
                {"pubkey": "FeePayerDict"},
                {"pubkey": "OtherDict"}
            ]
        }
    }
    
    result2 = parser.parse_transaction(tx_data2)
    
    assert result2["wallet_address"] == "FeePayerDict", f"Expected wallet_address='FeePayerDict', got '{result2['wallet_address']}'"
    print("✅ PASS: wallet_address set from accountKeys[0] (dict format without signer)")
    return True

def main():
    """Run all tests"""
    print("=" * 70)
    print("TESTING: wallet_tx_parser.py Requirements")
    print("=" * 70)
    
    tests = [
        ("Jupiter Detection by programId", test_jupiter_detection_by_program_id),
        ("Jupiter Detection by logs", test_jupiter_detection_by_logs),
        ("Meteora Detection", test_meteora_detection),
        ("wallet_address from signer", test_wallet_address_from_signer),
        ("wallet_address fallback", test_wallet_address_fallback),
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
    
    print("\n" + "=" * 70)
    print(f"RESULTS: {passed} passed, {failed} failed")
    print("=" * 70)
    
    return 0 if failed == 0 else 1

if __name__ == "__main__":
    import sys
    sys.exit(main())
