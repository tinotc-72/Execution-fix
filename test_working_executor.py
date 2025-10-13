#!/usr/bin/env python3
"""
Test using working old executor functions
"""

import asyncio
import sys
import os
sys.path.append(os.getcwd())

# Import from the old working executor
from pumpfun_CC_copy_executor_OLD_BACKUP import try_pumpfun_buy, try_pumpfun_sell_all
from env_keys import EnvKeys, load_wallet_from_private_key

async def test_working_executor():
    """Test with the old working executor functions"""
    
    # Your chosen meme coin
    mint_address = "4SXJJw2GKVTeoxqjrcrFNb3S59632wXjVRSJN8kFpump"
    sol_amount = 0.001
    
    print("🎯 TESTING WITH OLD WORKING EXECUTOR")
    print("=" * 50)
    print(f"Mint: {mint_address}")
    print(f"Amount: {sol_amount} SOL")
    print("=" * 50)
    
    # Load wallet
    env = EnvKeys()
    wallet_keypair = load_wallet_from_private_key(env.PHANTOM_PRIVATE_KEY)
    
    print(f"Wallet: {wallet_keypair.pubkey()}")
    
    # Test buy
    print(f"\n🚀 TESTING BUY...")
    buy_result = await try_pumpfun_buy(
        wallet_keypair=wallet_keypair,
        token_mint=mint_address,
        amount_sol=sol_amount,
        max_retries=1
    )
    
    print(f"Buy Result: {buy_result}")
    
    if buy_result.get('success'):
        print(f"✅ BUY SUCCESSFUL!")
        print(f"Signature: {buy_result.get('signature')}")
        print(f"Explorer: https://solscan.io/tx/{buy_result.get('signature')}")
        
        # Wait a bit then try sell
        print(f"\n⏳ Waiting 5 seconds before sell...")
        await asyncio.sleep(5)
        
        print(f"\n🚀 TESTING SELL...")
        sell_result = await try_pumpfun_sell_all(
            wallet_keypair=wallet_keypair,
            token_mint=mint_address,
            max_retries=1
        )
        
        print(f"Sell Result: {sell_result}")
        
        if sell_result.get('success'):
            print(f"✅ SELL SUCCESSFUL!")
            print(f"Signature: {sell_result.get('signature')}")
            print(f"Explorer: https://solscan.io/tx/{sell_result.get('signature')}")
        else:
            print(f"❌ Sell failed: {sell_result}")
            
    else:
        print(f"❌ Buy failed: {buy_result}")

if __name__ == "__main__":
    asyncio.run(test_working_executor())
