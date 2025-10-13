#!/usr/bin/env python3

import asyncio
import logging
from env_keys import EnvKeys, load_wallet_from_private_key

# Configure logging
logging.basicConfig(level=logging.INFO)

async def check_token_balances():
    """Check what tokens we currently hold"""
    
    # Setup environment and wallet
    env_keys = EnvKeys()
    private_key = env_keys.PHANTOM_PRIVATE_KEY
    wallet = load_wallet_from_private_key(private_key)
    
    print(f"🔑 Checking balances for wallet: {wallet.pubkey()}")
    
    # Check our recent successful transaction token
    recent_token = "mvqgb1pa4pyTcqDnKjhFV2Zi97qTb9kn16obh4T6RYd"
    
    # Import the MEV executor to check balance
    try:
        from mev_pumpfun_executor import get_mev_executor
        
        executor = get_mev_executor(private_key)
        
        # Check SOL balance
        sol_balance = await executor.get_sol_balance()
        print(f"💰 SOL Balance: {sol_balance:.6f} SOL")
        
        # Check token balance for our recent transaction
        try:
            token_balance = await executor.get_token_balance(recent_token)
            print(f"🪙 Token Balance ({recent_token[:8]}): {token_balance:,} tokens")
            
            if token_balance > 0:
                print(f"✅ We have {token_balance:,} tokens to test selling!")
                return recent_token, token_balance
            else:
                print(f"❌ No tokens found for {recent_token[:8]}")
                
        except Exception as e:
            print(f"❌ Error checking token balance: {e}")
            
    except Exception as e:
        print(f"❌ Error with MEV executor: {e}")
        
    return None, 0

if __name__ == "__main__":
    asyncio.run(check_token_balances())