#!/usr/bin/env python3
"""
Integration test for the updated build_and_sign function.
Tests the function with mock data to verify it builds a valid transaction.
"""

import sys
import json
import base64

def create_mock_trade_info():
    """Create a mock trade_info with a Meteora transaction"""
    return {
        "token_mint": "EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v",  # USDC for testing
        "wallet_address": "suqh5sHtr8HyJ7q8scBimULPkPpA557prMG47xCHQfK",
        "transaction": {
            "message": {
                "accountKeys": [
                    {"pubkey": "suqh5sHtr8HyJ7q8scBimULPkPpA557prMG47xCHQfK", "signer": True, "writable": True},
                    {"pubkey": "So11111111111111111111111111111111111111112", "signer": False, "writable": False},
                    {"pubkey": "EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v", "signer": False, "writable": False},
                    {"pubkey": "Eo7WjKq67rjJQSZxS6z3YkapzY3eMj6Xy8X5EQVn5UaB", "signer": False, "writable": False},
                ],
                "instructions": [
                    {
                        "programIdIndex": 3,
                        "accounts": [0, 1, 2],
                        "data": base64.b64encode(bytes([248, 198, 158, 145, 225, 117, 135, 200]) + 
                                                 int(1000000).to_bytes(8, 'little') + 
                                                 int(1).to_bytes(8, 'little')).decode()
                    }
                ],
                "addressTableLookups": []
            }
        }
    }

def test_build_and_sign_basic():
    """Test basic build_and_sign functionality"""
    print("=" * 80)
    print("TEST: Basic build_and_sign Functionality")
    print("=" * 80)
    
    try:
        # Import required modules
        from mev_meteora_executor import build_and_sign, SimpleRPC, RPCConfig
        from solders.keypair import Keypair
        
        # Create mock RPC (won't actually call RPC in this test)
        class MockRPC:
            def _post(self, method, params):
                if method == "getAccountInfo":
                    # Return None to trigger ATA creation
                    return {"value": None}
                return {}
            
            def get_latest_blockhash(self):
                from solders.hash import Hash
                return (Hash.from_string("11111111111111111111111111111111111111111111"), "123456")
        
        rpc = MockRPC()
        keypair = Keypair()  # Generate a random keypair for testing
        trade_info = create_mock_trade_info()
        
        print("\n📋 Test inputs:")
        print(f"   Token mint: {trade_info['token_mint']}")
        print(f"   Wallet: {trade_info['wallet_address']}")
        print(f"   Force requote: False")
        print(f"   Slippage BPS: 300")
        
        # Test without force_requote
        print("\n🔧 Building transaction without force_requote...")
        tx = build_and_sign(
            trade_info=trade_info,
            rpc=rpc,
            keypair=keypair,
            force_requote=False,
            slippage_bps=300
        )
        
        print("✅ PASS: Transaction built successfully")
        print(f"   Transaction type: {type(tx).__name__}")
        
        # Verify transaction has instructions
        if hasattr(tx, 'message'):
            num_ixs = len(tx.message.instructions)
            print(f"   Number of instructions: {num_ixs}")
            if num_ixs > 0:
                print("✅ PASS: Transaction has instructions")
            else:
                print("❌ FAIL: Transaction has no instructions")
                return False
        
        return True
        
    except Exception as e:
        print(f"❌ FAIL: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_build_and_sign_force_requote():
    """Test build_and_sign with force_requote=True"""
    print("\n" + "=" * 80)
    print("TEST: build_and_sign with force_requote")
    print("=" * 80)
    
    try:
        from mev_meteora_executor import build_and_sign
        from solders.keypair import Keypair
        
        class MockRPC:
            def _post(self, method, params):
                if method == "getAccountInfo":
                    return {"value": None}
                return {}
            
            def get_latest_blockhash(self):
                from solders.hash import Hash
                return (Hash.from_string("11111111111111111111111111111111111111111111"), "123456")
        
        rpc = MockRPC()
        keypair = Keypair()
        trade_info = create_mock_trade_info()
        
        print("\n📋 Test inputs:")
        print(f"   Force requote: True")
        print(f"   Slippage BPS: 500")
        
        # Test with force_requote
        print("\n🔧 Building transaction with force_requote...")
        tx = build_and_sign(
            trade_info=trade_info,
            rpc=rpc,
            keypair=keypair,
            force_requote=True,
            slippage_bps=500
        )
        
        print("✅ PASS: Transaction built successfully with force_requote")
        return True
        
    except Exception as e:
        print(f"❌ FAIL: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_parameter_validation():
    """Test that parameters are correctly passed to the function"""
    print("\n" + "=" * 80)
    print("TEST: Parameter Validation")
    print("=" * 80)
    
    try:
        from mev_meteora_executor import build_and_sign
        from solders.keypair import Keypair
        
        class MockRPC:
            def _post(self, method, params):
                if method == "getAccountInfo":
                    return {"value": None}
                return {}
            
            def get_latest_blockhash(self):
                from solders.hash import Hash
                return (Hash.from_string("11111111111111111111111111111111111111111111"), "123456")
        
        rpc = MockRPC()
        keypair = Keypair()
        trade_info = create_mock_trade_info()
        
        # Test with different slippage values
        test_cases = [
            (False, 100),
            (False, 300),
            (True, 300),
            (True, 500),
        ]
        
        for force_requote, slippage_bps in test_cases:
            print(f"\n   Testing: force_requote={force_requote}, slippage_bps={slippage_bps}")
            tx = build_and_sign(
                trade_info=trade_info,
                rpc=rpc,
                keypair=keypair,
                force_requote=force_requote,
                slippage_bps=slippage_bps
            )
            print(f"   ✅ Success with force_requote={force_requote}, slippage_bps={slippage_bps}")
        
        print("\n✅ PASS: All parameter combinations work correctly")
        return True
        
    except Exception as e:
        print(f"❌ FAIL: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Run all integration tests"""
    print("\n" + "=" * 80)
    print("INTEGRATION TESTS FOR build_and_sign")
    print("=" * 80 + "\n")
    
    tests = [
        test_build_and_sign_basic,
        test_build_and_sign_force_requote,
        test_parameter_validation,
    ]
    
    results = []
    for test in tests:
        try:
            result = test()
            results.append(result)
        except Exception as e:
            print(f"❌ ERROR: {e}")
            results.append(False)
    
    print("\n" + "=" * 80)
    print("INTEGRATION TEST SUMMARY")
    print("=" * 80)
    
    passed = sum(results)
    total = len(results)
    
    print(f"\n{passed}/{total} integration tests passed")
    
    if passed == total:
        print("\n✅ ALL INTEGRATION TESTS PASSED!")
        return 0
    else:
        print(f"\n⚠️  {total - passed} integration test(s) failed")
        return 1

if __name__ == "__main__":
    sys.exit(main())
