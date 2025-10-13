#!/usr/bin/env python3
"""
Find recent sell transactions on pump.fun to analyze account structure
"""

import asyncio
import aiohttp
import json
from env_keys import EnvKeys

PUMP_PROGRAM = "6EF8rrecthR5Dkzon8Nwu78hRvfCKubJ14M5uBEwF6P"
SELL_DISCRIMINATOR = "33e685a4017f83ad"

async def fetch_recent_transactions():
    """Fetch recent transactions for pump.fun program"""
    keys = EnvKeys()
    rpc_url = f"https://mainnet.helius-rpc.com/v0/?api-key={keys.HELIUS_API_KEY}"
    
    payload = {
        "jsonrpc": "2.0",
        "id": 1,
        "method": "getSignaturesForAddress",
        "params": [
            PUMP_PROGRAM,
            {
                "limit": 50
            }
        ]
    }
    
    async with aiohttp.ClientSession() as session:
        async with session.post(rpc_url, json=payload) as response:
            result = await response.json()
            
            if 'result' in result:
                print(f"Found {len(result['result'])} recent transactions")
                return [tx['signature'] for tx in result['result']]
            else:
                print(f"Error fetching signatures: {result}")
                return []

async def analyze_transaction(sig: str):
    """Analyze a specific transaction"""
    keys = EnvKeys()
    rpc_url = f"https://mainnet.helius-rpc.com/v0/?api-key={keys.HELIUS_API_KEY}"
    
    payload = {
        "jsonrpc": "2.0",
        "id": 1,
        "method": "getTransaction",
        "params": [
            sig,
            {
                "encoding": "json",
                "maxSupportedTransactionVersion": 0
            }
        ]
    }
    
    async with aiohttp.ClientSession() as session:
        async with session.post(rpc_url, json=payload) as response:
            result = await response.json()
            
            if 'result' in result and result['result']:
                tx = result['result']
                
                # Check if this is a sell transaction
                for instruction in tx['transaction']['message']['instructions']:
                    if instruction.get('programId') == PUMP_PROGRAM:
                        data = instruction.get('data', '')
                        if data.startswith(SELL_DISCRIMINATOR):
                            print(f"\n=== SELL TRANSACTION: {sig} ===")
                            print(f"Data: {data}")
                            
                            # Print account structure
                            accounts = instruction.get('accounts', [])
                            all_accounts = tx['transaction']['message']['accountKeys']
                            
                            print("Account structure:")
                            for i, account_idx in enumerate(accounts):
                                account_pubkey = all_accounts[account_idx]
                                print(f"  {i}: {account_pubkey}")
                            
                            return True
            return False

async def main():
    print("🔍 Searching for recent sell transactions...")
    
    signatures = await fetch_recent_transactions()
    
    sell_count = 0
    for sig in signatures:
        if await analyze_transaction(sig):
            sell_count += 1
            if sell_count >= 3:  # Get 3 examples
                break
    
    print(f"\nFound {sell_count} sell transactions")

if __name__ == "__main__":
    asyncio.run(main())
