#!/usr/bin/env python3
"""
Simple instruction data analyzer for pump.fun transactions
"""

import asyncio
import json
import aiohttp
import base58
from env_keys import EnvKeys

async def simple_analyze(tx_sig: str):
    """Simple analysis of instruction data"""
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
        message = tx_data["transaction"]["message"]
        accounts = message.get("accountKeys", [])
        
        print(f"=== Transaction: {tx_sig} ===")
        
        for i, ix in enumerate(message.get("instructions", [])):
            program_idx = ix.get("programIdIndex", 0)
            program_id = accounts[program_idx] if program_idx < len(accounts) else "Unknown"
            
            if program_id == "6EF8rrecthR5Dkzon8Nwu78hRvfCKubJ14M5uBEwF6P":
                print(f"\n🎯 Pump.fun Instruction {i}:")
                
                data = ix.get("data", "")
                if data:
                    try:
                        raw_data = base58.b58decode(data)
                        print(f"Data (hex): {raw_data.hex()}")
                        
                        if len(raw_data) >= 8:
                            discriminator = raw_data[:8]
                            print(f"Discriminator: {discriminator.hex()}")
                            
                            if len(raw_data) > 8:
                                rest = raw_data[8:]
                                print(f"Additional data: {rest.hex()} ({len(rest)} bytes)")
                                
                    except Exception as e:
                        print(f"Error decoding: {e}")
                
                # Account structure 
                account_indices = ix.get("accounts", [])
                print(f"Accounts ({len(account_indices)}):")
                for j, acc_idx in enumerate(account_indices):
                    if acc_idx < len(accounts):
                        acc = accounts[acc_idx]
                        print(f"  {j}: {acc}")

async def main():
    # Successful sell transaction
    await simple_analyze("VfqeM43anBaxsR7fezsKVMY1P4DGp9LBKsxAoCbL2BQNt5LUZhec5bHqPb1DzUVYQNFqaYCHz65zirGvnfabPcX")
    
    print("\n" + "="*80 + "\n")
    
    # Let's also find a BUY transaction - this was a sell
    # Look at one of the other recent transactions  
    await simple_analyze("64txy9SD2LPaC8KjEUQd8K957ui5iohk7vG7mG2ypRoEvSiLdSzpSmCCJsVEgVr5cY3zHfRTgGJaswT8cqaewche")

if __name__ == "__main__":
    asyncio.run(main())
