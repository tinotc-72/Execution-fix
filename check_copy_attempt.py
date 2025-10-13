#!/usr/bin/env python3
"""
Check if this failed transaction was your bot's copy attempt
"""

import asyncio
import aiohttp
from env_keys import EnvKeys
from datetime import datetime

async def check_copy_attempt():
    """Check if this was your bot attempting a copy trade"""
    
    failed_signature = "BGAXxeYWJroSxbk8dEXj8cmaeaHGbGc2y88o5R5gL6jTgC1mUAxBxvKjdsjf6R9Bvj8f8csAgnyLcsSqGTamQJ2"
    your_wallet = "A26P5WXU5SwdgKNAP6nkyYFELv4MkmK7sDGKt7Nu3AoB"  # Your bot's wallet
    
    print(f"🔍 CHECKING IF FAILED TX WAS YOUR BOT'S COPY ATTEMPT")
    print(f"Failed TX: {failed_signature[:12]}...")
    print(f"Your Wallet: {your_wallet[:8]}...")
    print("=" * 80)
    
    env_keys = EnvKeys()
    
    payload = {
        "jsonrpc": "2.0",
        "id": 1,
        "method": "getTransaction",
        "params": [
            failed_signature,
            {
                "encoding": "json",
                "commitment": "confirmed",
                "maxSupportedTransactionVersion": 0
            }
        ]
    }
    
    async with aiohttp.ClientSession() as session:
        async with session.post(env_keys.HELIUS_RPC_URL, json=payload) as response:
            data = await response.json()
            
            if 'error' in data:
                print(f"❌ ERROR: {data['error']}")
                return
            
            result = data.get('result')
            if not result:
                print(f"❌ NO RESULT")
                return
            
            # Check if your wallet is involved
            transaction = result.get('transaction', {})
            message = transaction.get('message', {})
            account_keys = message.get('accountKeys', [])
            
            if your_wallet in account_keys:
                wallet_index = account_keys.index(your_wallet)
                print(f"✅ CONFIRMED: This was YOUR BOT'S transaction!")
                print(f"   Your wallet at index: {wallet_index}")
                print(f"   This proves detection is working - bot attempted copy trade")
                
                # Get transaction timing
                slot = result.get('slot')
                print(f"   📅 Slot: {slot}")
                
                # Look for the token being traded
                meta = result.get('meta', {})
                pre_token_balances = meta.get('preTokenBalances', [])
                post_token_balances = meta.get('postTokenBalances', [])
                
                print(f"   🪙 Token balances before: {len(pre_token_balances)}")
                print(f"   🪙 Token balances after: {len(post_token_balances)}")
                
                # Find what token was being created ATA for
                logs = meta.get('logMessages', [])
                for log in logs:
                    if "Create" in log and "ATokenGPvbdGVxr1b2hvZbsiqW5xWH25efTNsLJA8knL" in log:
                        print(f"   🎯 ATA Creation attempted: {log}")
                
                # Now let's find what target wallet trade triggered this
                await find_triggering_trade(slot, env_keys)
                
            else:
                print(f"❌ This was NOT your bot's transaction")
                print(f"   Account keys: {len(account_keys)}")
                for i, key in enumerate(account_keys):
                    print(f"      [{i}] {key}")

async def find_triggering_trade(failed_slot, env_keys):
    """Find the target wallet trade that triggered this copy attempt"""
    print(f"\n🔍 SEARCHING FOR TRIGGERING TRADE AROUND SLOT {failed_slot}")
    
    target_wallets = [
        "suqh5sHtr8HyJ7q8scBimULPkPpA557prMG47xCHQfK",
        "DfMxre4cKmvogbLrPigxmibVTTQDuzjdXojWzjCXXhzj"
    ]
    
    for wallet in target_wallets:
        print(f"   🎯 Checking {wallet[:8]}... for recent trades")
        
        # Get recent transactions for this wallet
        payload = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "getSignaturesForAddress",
            "params": [
                wallet,
                {
                    "limit": 20,
                    "commitment": "confirmed"
                }
            ]
        }
        
        async with aiohttp.ClientSession() as session:
            async with session.post(env_keys.HELIUS_RPC_URL, json=payload) as response:
                data = await response.json()
                
                if 'error' in data:
                    continue
                
                result = data.get('result', [])
                
                for tx_info in result:
                    tx_slot = tx_info.get('slot')
                    signature = tx_info.get('signature')
                    
                    # Look for transactions around the same time (within 100 slots)
                    if abs(tx_slot - failed_slot) <= 100:
                        print(f"      📅 Found nearby transaction: {signature[:12]}... (slot {tx_slot})")
                        print(f"         ⏱️ Slot difference: {tx_slot - failed_slot}")
                        
                        if tx_slot < failed_slot:
                            print(f"         🎯 POTENTIAL TRIGGER: This happened BEFORE your failed copy")

if __name__ == "__main__":
    asyncio.run(check_copy_attempt())
