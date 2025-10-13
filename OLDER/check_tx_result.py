#!/usr/bin/env python3
"""
Fetch transaction details to debug errors
"""

import asyncio
import json
import aiohttp
from env_keys import EnvKeys

async def fetch_transaction_details(tx_sig: str):
    """Fetch transaction details from RPC"""
    keys = EnvKeys()
    rpc_url = f"https://mainnet.helius-rpc.com/v0/?api-key={keys.HELIUS_API_KEY}"
    
    payload = {
        "jsonrpc": "2.0",
        "id": 1,
        "method": "getTransaction",
        "params": [
            tx_sig,
            {
                "encoding": "json",
                "commitment": "confirmed",
                "maxSupportedTransactionVersion": 0
            }
        ]
    }
    
    async with aiohttp.ClientSession() as session:
        async with session.post(rpc_url, json=payload) as response:
            result = await response.json()
            
    if "result" in result and result["result"]:
        tx_data = result["result"]
        
        print("=== Transaction Details ===")
        print(f"Slot: {tx_data.get('slot')}")
        print(f"Block time: {tx_data.get('blockTime')}")
        
        meta = tx_data.get("meta", {})
        print(f"\n=== Transaction Meta ===")
        print(f"Error: {meta.get('err')}")
        print(f"Fee: {meta.get('fee')} lamports")
        print(f"Compute units consumed: {meta.get('computeUnitsConsumed')}")
        
        if meta.get("logMessages"):
            print(f"\n=== Program Logs ===")
            for log in meta["logMessages"]:
                print(f"  {log}")
                
        return tx_data
    else:
        print(f"Transaction not found or error: {result}")
        return None

async def main():
    tx_sig = "fEe9SnVo6Z4GCsNS7wqjcfW6kJL9As3ByJStxg7PGE5nDC8ELX79dAvDqrYXujTegCigNGjdpQXjCCWsCvpRyt5"
    await fetch_transaction_details(tx_sig)

if __name__ == "__main__":
    asyncio.run(main())
