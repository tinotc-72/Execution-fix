#!/usr/bin/env python3
"""
Quick MEV Test Setup
Uses the token from your analyzed transactions for safe testing
"""

import asyncio
from mev_real_trade_test import MEVRealTradeTest

async def quick_mev_test():
    """Quick test using the token from your transaction analysis"""
    
    # This is the token from the successful MEV transactions we analyzed
    test_mint = "Ew4teeKoEKn5EQeNtgfYS5y1gJriBcMXet7kCiTJpump"
    
    print("🎯 QUICK MEV TEST")
    print("=" * 50)
    print(f"Using token from analyzed MEV transactions:")
    print(f"Mint: {test_mint}")
    print(f"This token had successful MEV trades worth 1.5+ SOL")
    print("=" * 50)
    
    # Create tester
    tester = MEVRealTradeTest()
    
    # Check current balance
    sol_balance = await tester.executor.get_sol_balance()
    print(f"\n💰 Current SOL Balance: {sol_balance:.6f}")
    
    if sol_balance < 0.01:
        print(f"❌ Need at least 0.01 SOL for testing")
        return
        
    # Check if we already have tokens
    token_balance = await tester.executor.get_token_balance(test_mint)
    print(f"💰 Current Token Balance: {token_balance:,}")
    
    print(f"\n🎯 TEST OPTIONS:")
    print(f"1. MEV Buy Test (0.005 SOL)")
    print(f"2. MEV Sell Test (if you have tokens)")
    print(f"3. Full Buy-Sell Cycle")
    
    # Get user choice
    print(f"\nSelect test to run:")
    print(f"Enter 1, 2, or 3 (or 'q' to quit): ", end="")
    
    # For safety, let's just show what would happen
    print(f"\n⚠️  SAFETY MODE - Showing what would happen:")
    
    if token_balance > 0:
        print(f"\n🎯 You have {token_balance:,} tokens to test selling")
        print(f"MEV Sell would use:")
        print(f"   • Priority: 750,000 μ-lamports")
        print(f"   • Compute: 200,000 units")
        print(f"   • MEV Router: Advanced routing")
    else:
        print(f"\n🎯 You could test buying with:")
        print(f"   • Amount: 0.005 SOL (~$1)")
        print(f"   • Priority: 500,000 μ-lamports")
        print(f"   • Compute: 149,700 units")
        print(f"   • Direct Pump.fun calls")
        
    print(f"\n💡 TO RUN ACTUAL TEST:")
    print(f"1. Edit this file")
    print(f"2. Uncomment the test functions below")
    print(f"3. Run again")
    
    # Uncomment these lines to run actual tests:
    
    # Option 1: Buy test
    # print(f"\n🚀 Running MEV buy test...")
    # buy_signature = await tester.test_meme_coin_buy(test_mint, 0.005)
    
    # Option 2: Sell test (if you have tokens)
    # if token_balance > 0:
    #     print(f"\n🚀 Running MEV sell test...")
    #     sell_signature = await tester.test_meme_coin_sell(test_mint)
    
    # Option 3: Full cycle
    # print(f"\n🚀 Running full MEV cycle test...")
    # result = await tester.full_cycle_test(test_mint, 0.005)
    
    print(f"\n✅ Test setup complete!")

if __name__ == "__main__":
    asyncio.run(quick_mev_test())
