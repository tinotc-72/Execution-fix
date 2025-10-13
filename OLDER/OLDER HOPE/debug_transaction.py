#!/usr/bin/env python3
"""
Debug script to analyze a specific transaction and understand why balance analysis might be failing
"""

import asyncio
import json
from listener import fetch_transaction, identify_dex_and_instruction

async def debug_transaction(signature: str):
    """Debug a specific transaction"""
    print(f"🔍 Debugging transaction: {signature}")
    
    # Fetch transaction data
    tx_data = await fetch_transaction(signature)
    if not tx_data:
        print("❌ Failed to fetch transaction data")
        return
    
    print(f"✅ Transaction fetched successfully")
    
    # Check DEX identification
    dex_info = identify_dex_and_instruction(tx_data)
    if dex_info:
        dex_name, instruction = dex_info
        print(f"🎯 DEX identified: {dex_name}")
    else:
        print("❌ No DEX identified")
        return
    
    # Analyze balance structure
    meta = tx_data.get('meta', {})
    print(f"\n📊 Transaction Meta Analysis:")
    print(f"   Error: {meta.get('err', 'None')}")
    print(f"   Pre-balances count: {len(meta.get('preBalances', []))}")
    print(f"   Post-balances count: {len(meta.get('postBalances', []))}")
    print(f"   Pre-token balances count: {len(meta.get('preTokenBalances', []))}")
    print(f"   Post-token balances count: {len(meta.get('postTokenBalances', []))}")
    
    # Check account keys
    account_keys = tx_data.get('transaction', {}).get('message', {}).get('accountKeys', [])
    print(f"\n🔑 Account Keys ({len(account_keys)}):")
    for i, key in enumerate(account_keys[:10]):  # Show first 10
        print(f"   {i}: {key}")
    if len(account_keys) > 10:
        print(f"   ... and {len(account_keys) - 10} more")
    
    # Check for monitored wallets
    monitored_wallets = ['suqh5sHtr8HyJ7q8scBimULPkPpA557prMG47xCHQfK', 'DfMxre4cKmvogbLrPigxmibVTTQDuzjdXojWzjCXXhzj']
    for wallet in monitored_wallets:
        if wallet in account_keys:
            wallet_index = account_keys.index(wallet)
            print(f"\n🎯 Monitored wallet {wallet[:8]}... found at index {wallet_index}")
            
            # Check balance changes
            pre_balances = meta.get('preBalances', [])
            post_balances = meta.get('postBalances', [])
            
            if wallet_index < len(pre_balances) and wallet_index < len(post_balances):
                sol_change = (post_balances[wallet_index] - pre_balances[wallet_index]) / 1_000_000_000
                print(f"   SOL balance change: {sol_change:.9f}")
            
            # Check token balance changes
            pre_token_balances = meta.get('preTokenBalances', [])
            post_token_balances = meta.get('postTokenBalances', [])
            
            print(f"   Token balances (pre):")
            for balance in pre_token_balances:
                if balance.get('owner') == wallet:
                    mint = balance.get('mint', 'Unknown')
                    amount = balance.get('uiTokenAmount', {}).get('amount', 0)
                    print(f"     {mint[:8]}...: {amount}")
            
            print(f"   Token balances (post):")
            for balance in post_token_balances:
                if balance.get('owner') == wallet:
                    mint = balance.get('mint', 'Unknown') 
                    amount = balance.get('uiTokenAmount', {}).get('amount', 0)
                    print(f"     {mint[:8]}...: {amount}")

async def main():
    # Use one of the recently detected PUMP_NEW transactions
    signature = "454e37EjpSQEjP5hBvBGLa7QDJLy9m3vFhpzxXHczQmwFvYeLmWFj13X7j3zWJQZRcBgaQJwzLXpGgRFqBWJJy3R"
    await debug_transaction(signature)

if __name__ == "__main__":
    asyncio.run(main())
