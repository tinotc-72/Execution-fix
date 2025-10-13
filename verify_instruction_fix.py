#!/usr/bin/env python3

import asyncio
from complete_mev_bot import CompleteMEVBot
from env_keys import EnvKeys

async def verify_fix():
    """Final verification that our instruction data fix works"""
    
    print("🔥 FINAL VERIFICATION - LIVE INSTRUCTION DATA FIX")
    print("=" * 60)
    
    env = EnvKeys()
    bot = CompleteMEVBot(env.PHANTOM_PRIVATE_KEY)
    
    print("📊 BEFORE vs AFTER:")
    print("   ❌ OLD: 000b9a530600000000ef0e483a8f000000 (17 bytes) - Failed with Custom 101")
    print("   ✅ NEW: 66063d1201daebea3d8bba6e0500000020d6130000000000 (24 bytes) - From live blockchain")
    
    print(f"\n🎯 TESTING WITH WORKING PATTERN...")
    
    try:
        # Test with a known token from our recent detections
        test_mint = 'HQ7zcHCsBwquAk7aBuF9CeFqQJX9rrCZaKigufDtRjM6'
        buy_amount = 0.001
        
        print(f"   Token: {test_mint}")
        print(f"   Amount: {buy_amount} SOL")
        
        # Execute the buy
        signature = await bot.execute_buy(test_mint, buy_amount)
        
        if signature:
            print(f"\n✅ SUCCESS! CUSTOM 101 ERRORS FIXED!")
            print(f"   Signature: {signature}")
            print(f"   🎉 Transaction executed successfully with live blockchain instruction data")
            
            return True
        else:
            print(f"\n❌ Transaction failed - more investigation needed")
            return False
            
    except Exception as e:
        print(f"\n❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = asyncio.run(verify_fix())
    
    if success:
        print(f"\n🚀 SOLUTION SUMMARY:")
        print(f"=" * 50)
        print(f"✅ Problem: Custom 101 errors from incorrect instruction data")
        print(f"✅ Root Cause: Using 17-byte patterns instead of 24-byte patterns")  
        print(f"✅ Solution: Analyzed live blockchain transactions to get working patterns")
        print(f"✅ Fix: Updated instruction data to 66063d1201daebea3d8bba6e0500000020d6130000000000")
        print(f"✅ Result: Transactions now execute successfully!")
        print(f"\n🎯 NEXT: Deploy corrected bot for live trading")
    else:
        print(f"\n🔍 Further analysis needed...")
