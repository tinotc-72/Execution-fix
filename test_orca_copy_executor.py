#!/usr/bin/env python3
"""
Test Orca Copy Executor
Tests the copy bot compatible Orca executor functions
"""

import asyncio
import logging
from config import WALLET
from orca_copy_executor import OrcaCopyExecutor, orca_copy_buy, orca_copy_sell_all

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("test_orca_copy")

# Test tokens
USDC_MINT = "EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v"
SOL_MINT = "So11111111111111111111111111111111111111112"

async def test_orca_copy_executor_class():
    """Test the OrcaCopyExecutor class directly"""
    print("\n🧪 TEST 1: OrcaCopyExecutor Class")
    print("=" * 50)
    
    executor = OrcaCopyExecutor(WALLET)
    
    try:
        # Get initial balances
        sol_balance = await executor.get_token_balance(SOL_MINT)
        usdc_balance = await executor.get_token_balance(USDC_MINT)
        
        print(f"💰 Initial Balances:")
        print(f"   SOL: {sol_balance:.6f}")
        print(f"   USDC: {usdc_balance:.6f}")
        
        if sol_balance < 0.001:
            print(f"❌ Insufficient SOL balance for test")
            return False
        
        # Test buy
        print(f"\n🛒 Testing Orca BUY: 0.001 SOL → USDC")
        buy_result = await executor.try_orca_buy(USDC_MINT, 0.001)
        
        print(f"📊 Buy Result: {buy_result}")
        
        if not buy_result["success"]:
            print(f"❌ Buy test failed")
            return False
        
        print(f"✅ Buy successful: {buy_result['signature']}")
        
        # Wait a moment
        print(f"\n⏳ Waiting 5 seconds...")
        await asyncio.sleep(5)
        
        # Check balances after buy
        sol_balance_post = await executor.get_token_balance(SOL_MINT)
        usdc_balance_post = await executor.get_token_balance(USDC_MINT)
        
        print(f"💰 Post-Buy Balances:")
        print(f"   SOL: {sol_balance_post:.6f}")
        print(f"   USDC: {usdc_balance_post:.6f}")
        
        # Test sell
        print(f"\n💸 Testing Orca SELL ALL: USDC → SOL")
        sell_result = await executor.try_orca_sell_all(USDC_MINT)
        
        print(f"📊 Sell Result: {sell_result}")
        
        if not sell_result["success"]:
            print(f"❌ Sell test failed")
            return False
        
        print(f"✅ Sell successful: {sell_result['signature']}")
        
        # Final balances
        sol_balance_final = await executor.get_token_balance(SOL_MINT)
        usdc_balance_final = await executor.get_token_balance(USDC_MINT)
        
        print(f"\n💰 Final Balances:")
        print(f"   SOL: {sol_balance_final:.6f}")
        print(f"   USDC: {usdc_balance_final:.6f}")
        
        # Calculate P&L
        sol_change = sol_balance_final - sol_balance
        print(f"\n📈 P&L: {sol_change:+.6f} SOL")
        
        print(f"\n🎉 OrcaCopyExecutor class test completed successfully!")
        return True
        
    except Exception as e:
        print(f"❌ Class test error: {e}")
        return False
    
    finally:
        await executor.close()

async def test_orca_convenience_functions():
    """Test the convenience functions for copy bot integration"""
    print("\n🧪 TEST 2: Convenience Functions")
    print("=" * 50)
    
    try:
        # Test convenience buy function
        print(f"🛒 Testing orca_copy_buy() convenience function")
        buy_result = await orca_copy_buy(WALLET, USDC_MINT, 0.001)
        
        print(f"📊 Buy Result: {buy_result}")
        
        if not buy_result["success"]:
            print(f"❌ Convenience buy test failed")
            return False
        
        print(f"✅ Convenience buy successful: {buy_result['signature']}")
        
        # Wait a moment
        print(f"\n⏳ Waiting 5 seconds...")
        await asyncio.sleep(5)
        
        # Test convenience sell function
        print(f"\n💸 Testing orca_copy_sell_all() convenience function")
        sell_result = await orca_copy_sell_all(WALLET, USDC_MINT)
        
        print(f"📊 Sell Result: {sell_result}")
        
        if not sell_result["success"]:
            print(f"❌ Convenience sell test failed")
            return False
        
        print(f"✅ Convenience sell successful: {sell_result['signature']}")
        
        print(f"\n🎉 Convenience functions test completed successfully!")
        return True
        
    except Exception as e:
        print(f"❌ Convenience functions test error: {e}")
        return False

async def test_error_handling():
    """Test error handling scenarios"""
    print("\n🧪 TEST 3: Error Handling")
    print("=" * 50)
    
    executor = OrcaCopyExecutor(WALLET)
    
    try:
        # Test sell with no balance
        print(f"🧪 Testing sell with no token balance...")
        fake_mint = "11111111111111111111111111111111111111111112"  # System program (invalid token)
        
        sell_result = await executor.try_orca_sell_all(fake_mint)
        print(f"📊 No-balance sell result: {sell_result}")
        
        if sell_result["success"]:
            print(f"❌ Expected failure but got success")
            return False
        
        print(f"✅ Correctly handled no-balance scenario")
        
        # Test buy with insufficient SOL (if wallet has less than 1 SOL)
        sol_balance = await executor.get_token_balance(SOL_MINT)
        if sol_balance < 1.0:
            print(f"🧪 Testing buy with large amount (should work with slippage)...")
            large_buy_result = await executor.try_orca_buy(USDC_MINT, 0.01)  # Small but larger amount
            print(f"📊 Large buy result: {large_buy_result}")
        
        print(f"\n🎉 Error handling test completed!")
        return True
        
    except Exception as e:
        print(f"❌ Error handling test error: {e}")
        return False
    
    finally:
        await executor.close()

async def main():
    """Run all tests"""
    print("🐋 ORCA COPY EXECUTOR TESTS")
    print("=" * 60)
    print("Testing copy bot compatible Orca executor")
    print("=" * 60)
    
    tests = [
        ("OrcaCopyExecutor Class", test_orca_copy_executor_class),
        ("Convenience Functions", test_orca_convenience_functions),
        ("Error Handling", test_error_handling)
    ]
    
    results = []
    
    for test_name, test_func in tests:
        try:
            print(f"\n{'='*60}")
            print(f"Running: {test_name}")
            print(f"{'='*60}")
            
            result = await test_func()
            results.append((test_name, result))
            
            if result:
                print(f"✅ {test_name}: PASSED")
            else:
                print(f"❌ {test_name}: FAILED")
                
        except Exception as e:
            print(f"❌ {test_name}: ERROR - {e}")
            results.append((test_name, False))
        
        # Wait between tests
        if test_func != tests[-1][1]:  # Don't wait after last test
            print(f"\n⏳ Waiting 10 seconds before next test...")
            await asyncio.sleep(10)
    
    # Final summary
    print(f"\n{'='*60}")
    print("🎯 TEST SUMMARY")
    print(f"{'='*60}")
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        status = "✅ PASSED" if result else "❌ FAILED"
        print(f"{test_name}: {status}")
    
    print(f"\nOverall: {passed}/{total} tests passed")
    
    if passed == total:
        print(f"\n🎉 ALL TESTS PASSED! Orca Copy Executor is ready for copy bot integration!")
    else:
        print(f"\n⚠️  Some tests failed. Review the output above.")

if __name__ == "__main__":
    asyncio.run(main())
