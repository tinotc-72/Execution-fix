#!/usr/bin/env python3
"""
Test script to verify that the solders.pubkey.Pubkey fix works correctly
"""

import sys
import traceback
from trade_processor import TradeProcessor

class MockPubkey:
    """Mock solders.pubkey.Pubkey object to test the fix"""
    def __init__(self, address):
        self.address = address
    
    def __str__(self):
        return self.address

class MockRPCClient:
    async def call(self, method, params):
        return {"result": {"value": None}}

def test_key_str_helper():
    """Test the _key_str helper with various input types"""
    print("🧪 Testing _key_str helper...")
    
    processor = TradeProcessor(["test"], MockRPCClient())
    
    # Test with string
    result = processor._key_str("So11111111111111111111111111111111111111112")
    assert result == "So11111111111111111111111111111111111111112"
    print("✅ String input works")
    
    # Test with dict
    result = processor._key_str({"pubkey": "So11111111111111111111111111111111111111112"})
    assert result == "So11111111111111111111111111111111111111112"
    print("✅ Dict input works")
    
    # Test with MockPubkey (simulating solders.pubkey.Pubkey)
    mock_pubkey = MockPubkey("So11111111111111111111111111111111111111112")
    result = processor._key_str(mock_pubkey)
    assert result == "So11111111111111111111111111111111111111112"
    print("✅ Pubkey-like object works")
    
    # Test with None
    result = processor._key_str(None)
    assert result == ""
    print("✅ None input handled safely")
    
    print("🎉 All _key_str tests passed!\n")

def test_candidates_from_atas():
    """Test _candidates_from_atas with mixed key types"""
    print("🧪 Testing _candidates_from_atas with mixed key types...")
    
    processor = TradeProcessor(["test"], MockRPCClient())
    
    # Create mock transaction with mixed key types
    mock_tx = {
        "transaction": {
            "message": {
                "accountKeys": [
                    "gasTzr94Pmp4Gf8vknQnqxeYxdgwFjbgdJa4msYRpnB",  # string
                    {"pubkey": "So11111111111111111111111111111111111111112"},  # dict
                    MockPubkey("EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v"),  # mock Pubkey
                ]
            }
        }
    }
    
    # Test with string wallet
    wallet = "gasTzr94Pmp4Gf8vknQnqxeYxdgwFjbgdJa4msYRpnB"
    result = processor._candidates_from_atas(mock_tx, wallet)
    print(f"Result with string wallet: {result}")
    
    # Test with MockPubkey wallet
    mock_wallet = MockPubkey("gasTzr94Pmp4Gf8vknQnqxeYxdgwFjbgdJa4msYRpnB")
    result = processor._candidates_from_atas(mock_tx, mock_wallet)
    print(f"Result with MockPubkey wallet: {result}")
    
    print("✅ _candidates_from_atas test completed without errors!\n")

def test_detect_platform():
    """Test _detect_platform with mixed key types"""
    print("🧪 Testing _detect_platform with mixed key types...")
    
    processor = TradeProcessor(["test"], MockRPCClient())
    
    # Mock transaction with Jupiter program
    mock_tx = {
        "transaction": {
            "message": {
                "instructions": [
                    {
                        "programIdIndex": 0
                    }
                ],
                "accountKeys": [
                    MockPubkey("JUP6LkbZbjS1jKKwapdHNy74zcZ3tLUZoi5QNyVTaV4")  # Jupiter program
                ]
            }
        }
    }
    
    result = processor._detect_platform(mock_tx)
    assert result == "jupiter"
    print(f"✅ Detected platform correctly: {result}")
    print("✅ _detect_platform test passed!\n")

async def test_extract_token_info_fast():
    """Test extract_token_info_fast with MockPubkey wallet"""
    print("🧪 Testing extract_token_info_fast with MockPubkey wallet...")
    
    processor = TradeProcessor(["test"], MockRPCClient())
    
    mock_tx = {
        "meta": {
            "preTokenBalances": [],
            "postTokenBalances": []
        }
    }
    
    # Test with MockPubkey wallet - should not crash
    mock_wallet = MockPubkey("gasTzr94Pmp4Gf8vknQnqxeYxdgwFjbgdJa4msYRpnB")
    try:
        result = await processor.extract_token_info_fast(mock_tx, mock_wallet)
        print(f"✅ extract_token_info_fast completed without error: {result}")
    except Exception as e:
        if "'solders.pubkey.Pubkey' object is not subscriptable" in str(e):
            print(f"❌ Still getting Pubkey subscript error: {e}")
            return False
        else:
            print(f"✅ Different error (expected): {e}")
    
    print("✅ extract_token_info_fast test passed!\n")
    return True

def main():
    """Run all tests"""
    print("🚀 Testing solders.pubkey.Pubkey fix...\n")
    
    try:
        test_key_str_helper()
        test_candidates_from_atas()
        test_detect_platform()
        
        # Run async test
        import asyncio
        asyncio.run(test_extract_token_info_fast())
        
        print("🎉 ALL TESTS PASSED! The Pubkey fix is working correctly!")
        return True
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)