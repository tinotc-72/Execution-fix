#!/usr/bin/env python3
"""
Test script to verify Raydium executor minimal scaffold and Keypair enforcement.

This test validates:
1. mev_raydium_executor imports cleanly
2. MEVRaydiumExecutor can be instantiated
3. try_raydium_buy and try_raydium_sell_all return None as expected
4. ExecutionCoordinator._require_keypair() properly validates Keypairs
"""

import sys
import asyncio


def test_raydium_imports():
    """Test that mev_raydium_executor imports cleanly."""
    print("=" * 60)
    print("TEST 1: Raydium Executor Imports")
    print("=" * 60)
    
    try:
        from mev_raydium_executor import MEVRaydiumExecutor, try_raydium_buy, try_raydium_sell_all
        print("✅ All imports successful")
        print(f"  - MEVRaydiumExecutor: {MEVRaydiumExecutor}")
        print(f"  - try_raydium_buy: {try_raydium_buy}")
        print(f"  - try_raydium_sell_all: {try_raydium_sell_all}")
        return True
    except Exception as e:
        print(f"❌ Import failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_raydium_executor_instantiation():
    """Test that MEVRaydiumExecutor can be instantiated."""
    print("\n" + "=" * 60)
    print("TEST 2: Raydium Executor Instantiation")
    print("=" * 60)
    
    try:
        from mev_raydium_executor import MEVRaydiumExecutor
        
        # Test with minimal parameters
        executor = MEVRaydiumExecutor(
            rpc_url="https://api.mainnet-beta.solana.com",
            keypair=None,
            jito_service=None
        )
        
        print("✅ MEVRaydiumExecutor instantiated successfully")
        print(f"  - Type: {type(executor)}")
        print(f"  - RPC URL: {executor.rpc_url}")
        print(f"  - Keypair: {executor.keypair}")
        print(f"  - Jito Service: {executor.jito_service}")
        return True
    except Exception as e:
        print(f"❌ Instantiation failed: {e}")
        import traceback
        traceback.print_exc()
        return False


async def test_raydium_stubs():
    """Test that try_raydium_buy and try_raydium_sell_all return None."""
    print("\n" + "=" * 60)
    print("TEST 3: Raydium Executor Stub Functions")
    print("=" * 60)
    
    try:
        from mev_raydium_executor import try_raydium_buy, try_raydium_sell_all
        
        # Test try_raydium_buy
        trade_info = {"signature": "test_sig", "token_mint": "test_mint"}
        result_buy = await try_raydium_buy(trade_info, keypair=None)
        
        if result_buy is None:
            print("✅ try_raydium_buy returns None as expected")
        else:
            print(f"❌ try_raydium_buy returned unexpected value: {result_buy}")
            return False
        
        # Test try_raydium_sell_all
        result_sell = await try_raydium_sell_all(trade_info, keypair=None)
        
        if result_sell is None:
            print("✅ try_raydium_sell_all returns None as expected")
        else:
            print(f"❌ try_raydium_sell_all returned unexpected value: {result_sell}")
            return False
        
        return True
    except Exception as e:
        print(f"❌ Stub test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_require_keypair_validation():
    """Test that _require_keypair properly validates Keypairs."""
    print("\n" + "=" * 60)
    print("TEST 4: ExecutionCoordinator._require_keypair() Validation")
    print("=" * 60)
    
    try:
        # Check if we can import the necessary modules
        try:
            from solders.keypair import Keypair
            solders_available = True
        except ImportError:
            print("⚠️ solders not available - skipping Keypair validation test")
            print("   (This is expected in environments without solders installed)")
            return True
        
        from execution_coordinator import ExecutionCoordinator
        
        # Test 1: Valid Keypair
        print("\nTest 4a: Valid Keypair")
        valid_keypair = Keypair()
        coordinator = ExecutionCoordinator(wallet=valid_keypair, rpc_client=None, jito_service=None, config=None)
        
        try:
            result = coordinator._require_keypair()
            if isinstance(result, Keypair):
                print("✅ _require_keypair returns valid Keypair when wallet is Keypair")
            else:
                print(f"❌ _require_keypair returned wrong type: {type(result)}")
                return False
        except Exception as e:
            print(f"❌ _require_keypair raised unexpected error: {e}")
            return False
        
        # Test 2: Invalid wallet (not a Keypair)
        print("\nTest 4b: Invalid Wallet (should raise TypeError)")
        invalid_wallet = "not_a_keypair"
        coordinator_invalid = ExecutionCoordinator(wallet=invalid_wallet, rpc_client=None, jito_service=None, config=None)
        
        try:
            coordinator_invalid._require_keypair()
            print("❌ _require_keypair should have raised TypeError for invalid wallet")
            return False
        except TypeError as e:
            print(f"✅ _require_keypair properly raised TypeError: {e}")
        except Exception as e:
            print(f"❌ _require_keypair raised wrong exception type: {type(e).__name__}: {e}")
            return False
        
        # Test 3: None wallet (should raise TypeError)
        print("\nTest 4c: None Wallet (should raise TypeError)")
        coordinator_none = ExecutionCoordinator(wallet=None, rpc_client=None, jito_service=None, config=None)
        
        try:
            coordinator_none._require_keypair()
            print("❌ _require_keypair should have raised TypeError for None wallet")
            return False
        except TypeError as e:
            print(f"✅ _require_keypair properly raised TypeError: {e}")
        except Exception as e:
            print(f"❌ _require_keypair raised wrong exception type: {type(e).__name__}: {e}")
            return False
        
        return True
    except Exception as e:
        print(f"❌ Keypair validation test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


async def main():
    """Run all tests."""
    print("\n" + "=" * 60)
    print("RAYDIUM EXECUTOR AND KEYPAIR ENFORCEMENT TESTS")
    print("=" * 60)
    
    results = []
    
    # Test 1: Imports
    results.append(("Raydium Imports", test_raydium_imports()))
    
    # Test 2: Instantiation
    results.append(("Raydium Instantiation", test_raydium_executor_instantiation()))
    
    # Test 3: Stub functions
    results.append(("Raydium Stubs", await test_raydium_stubs()))
    
    # Test 4: Keypair validation
    results.append(("Keypair Validation", test_require_keypair_validation()))
    
    # Summary
    print("\n" + "=" * 60)
    print("TEST SUMMARY")
    print("=" * 60)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        status = "✅ PASSED" if result else "❌ FAILED"
        print(f"{status}: {test_name}")
    
    print(f"\nTotal: {passed}/{total} tests passed")
    
    if passed == total:
        print("\n🎉 All tests passed!")
        return 0
    else:
        print(f"\n❌ {total - passed} test(s) failed")
        return 1


if __name__ == "__main__":
    sys.exit(asyncio.run(main()))
