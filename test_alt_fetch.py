#!/usr/bin/env python3
"""
Test for synchronous ALT fetch helpers in utils/alt_fetch.py
"""
import logging
from unittest.mock import patch, MagicMock
from utils.alt_fetch import rpc_call, fetch_lookup_table, build_alts_from_tables
from solders.pubkey import Pubkey
from solders.address_lookup_table_account import AddressLookupTableAccount

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def test_rpc_call():
    """Test the generic RPC call function"""
    print("\n" + "="*60)
    print("TEST: rpc_call()")
    print("="*60 + "\n")
    
    # Mock the requests.post call
    with patch('utils.alt_fetch.requests.post') as mock_post:
        # Setup mock response
        mock_response = MagicMock()
        mock_response.json.return_value = {
            "jsonrpc": "2.0",
            "id": 1,
            "result": {"test": "data"}
        }
        mock_post.return_value = mock_response
        
        # Call the function
        result = rpc_call("http://test-rpc", "testMethod", ["param1"])
        
        # Verify
        assert result == {"jsonrpc": "2.0", "id": 1, "result": {"test": "data"}}
        mock_post.assert_called_once()
        call_kwargs = mock_post.call_args
        assert call_kwargs.kwargs['json']['method'] == 'testMethod'
        assert call_kwargs.kwargs['json']['params'] == ['param1']
        
        print("   ✅ RPC call with correct payload")
        print("   ✅ Response parsed correctly")
    
    print()


def test_fetch_lookup_table():
    """Test fetching ALT addresses"""
    print("\n" + "="*60)
    print("TEST: fetch_lookup_table()")
    print("="*60 + "\n")
    
    # Test successful fetch
    with patch('utils.alt_fetch.rpc_call') as mock_rpc:
        mock_rpc.return_value = {
            "result": {
                "value": {
                    "addresses": [
                        "TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA",
                        "11111111111111111111111111111111"
                    ]
                }
            }
        }
        
        result = fetch_lookup_table("http://test-rpc", "AddressLookupTab1e1111111111111111111111111")
        
        assert len(result) == 2
        assert result[0] == "TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA"
        assert result[1] == "11111111111111111111111111111111"
        
        print("   ✅ Successfully fetched addresses from ALT")
        print(f"   ✅ Returned {len(result)} addresses")
    
    # Test failed fetch (no value)
    with patch('utils.alt_fetch.rpc_call') as mock_rpc:
        mock_rpc.return_value = {"result": None}
        
        result = fetch_lookup_table("http://test-rpc", "InvalidALT")
        
        assert result == []
        print("   ✅ Returns empty list for missing ALT")
    
    # Test error handling
    with patch('utils.alt_fetch.rpc_call') as mock_rpc:
        mock_rpc.side_effect = Exception("RPC error")
        
        result = fetch_lookup_table("http://test-rpc", "ErrorALT")
        
        assert result == []
        print("   ✅ Returns empty list on error")
    
    print()


def test_build_alts_from_tables():
    """Test building AddressLookupTableAccount objects"""
    print("\n" + "="*60)
    print("TEST: build_alts_from_tables()")
    print("="*60 + "\n")
    
    # Test successful build
    with patch('utils.alt_fetch.fetch_lookup_table') as mock_fetch:
        mock_fetch.side_effect = [
            [
                "TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA",
                "11111111111111111111111111111111"
            ],
            [
                "So11111111111111111111111111111111111111112"
            ]
        ]
        
        table_pubkeys = [
            "AddressLookupTab1e1111111111111111111111111",
            "AddressLookupTab1e2222222222222222222222222"
        ]
        
        result = build_alts_from_tables("http://test-rpc", table_pubkeys)
        
        assert len(result) == 2
        assert isinstance(result[0], AddressLookupTableAccount)
        assert isinstance(result[1], AddressLookupTableAccount)
        assert len(result[0].addresses) == 2
        assert len(result[1].addresses) == 1
        
        print(f"   ✅ Successfully built {len(result)} ALT accounts")
        print(f"   ✅ First ALT has {len(result[0].addresses)} addresses")
        print(f"   ✅ Second ALT has {len(result[1].addresses)} addresses")
    
    # Test with empty ALT (should skip)
    with patch('utils.alt_fetch.fetch_lookup_table') as mock_fetch:
        mock_fetch.side_effect = [
            ["TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA"],
            [],  # Empty ALT
            ["11111111111111111111111111111111"]
        ]
        
        table_pubkeys = [
            "AddressLookupTab1e1111111111111111111111111",
            "AddressLookupTab1e2222222222222222222222222",
            "AddressLookupTab1e3333333333333333333333333"
        ]
        
        result = build_alts_from_tables("http://test-rpc", table_pubkeys)
        
        assert len(result) == 2  # Empty ALT should be skipped
        print("   ✅ Correctly skips empty ALTs")
    
    # Test with invalid pubkey (should skip)
    with patch('utils.alt_fetch.fetch_lookup_table') as mock_fetch:
        mock_fetch.return_value = ["invalid_address"]
        
        table_pubkeys = ["AddressLookupTab1e1111111111111111111111111"]
        
        result = build_alts_from_tables("http://test-rpc", table_pubkeys)
        
        assert len(result) == 0  # Invalid pubkey should be skipped
        print("   ✅ Correctly handles invalid addresses")
    
    print()


def test_integration_with_message_v0():
    """Test that ALT accounts can be used with MessageV0"""
    print("\n" + "="*60)
    print("TEST: Integration with MessageV0")
    print("="*60 + "\n")
    
    # This test verifies that the ALT accounts we build are compatible with MessageV0
    from solders.message import MessageV0
    from solders.instruction import Instruction
    from solders.hash import Hash
    from solders.keypair import Keypair
    
    with patch('utils.alt_fetch.fetch_lookup_table') as mock_fetch:
        mock_fetch.return_value = [
            "TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA"
        ]
        
        table_pubkeys = ["AddressLookupTab1e1111111111111111111111111"]
        alts = build_alts_from_tables("http://test-rpc", table_pubkeys)
        
        assert len(alts) == 1
        
        # Try to use it with MessageV0.try_compile
        payer = Keypair()
        instruction = Instruction(
            program_id=Pubkey.from_string("TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA"),
            accounts=[],
            data=bytes([])
        )
        blockhash = Hash.default()
        
        try:
            message = MessageV0.try_compile(
                payer.pubkey(),
                [instruction],
                alts,
                blockhash
            )
            print("   ✅ ALT accounts compatible with MessageV0.try_compile")
            print(f"   ✅ MessageV0 created successfully")
        except Exception as e:
            print(f"   ❌ Failed to create MessageV0: {e}")
            raise
    
    print()


def main():
    """Run all tests"""
    print("\n" + "🚀"*30)
    print("SYNCHRONOUS ALT FETCH HELPERS TEST SUITE")
    print("🚀"*30)
    
    try:
        test_rpc_call()
        test_fetch_lookup_table()
        test_build_alts_from_tables()
        test_integration_with_message_v0()
        
        print("\n" + "="*60)
        print("TEST SUMMARY")
        print("="*60 + "\n")
        print("✅ ALL TESTS PASSED")
        print("\nValidated:")
        print("   ✅ rpc_call() makes correct RPC requests")
        print("   ✅ fetch_lookup_table() fetches ALT addresses")
        print("   ✅ build_alts_from_tables() builds AddressLookupTableAccount objects")
        print("   ✅ ALT accounts are compatible with MessageV0")
        print("   ✅ Error handling works correctly")
        print("\n🎉 Synchronous ALT fetch helpers are working correctly!")
        return True
        
    except Exception as e:
        print("\n" + "="*60)
        print("TEST SUMMARY")
        print("="*60 + "\n")
        print(f"❌ TESTS FAILED: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)
