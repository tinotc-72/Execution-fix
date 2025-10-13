#!/usr/bin/env python3
"""
Find a recent pump.fun token that's currently active
"""

import asyncio
import json
import aiohttp
from env_keys import EnvKeys

async def get_recent_pump_transactions():
    """Get recent transactions on pump.fun trade program"""
    keys = EnvKeys()
    rpc_url = f"https://mainnet.helius-rpc.com/v0/?api-key={keys.HELIUS_API_KEY}"
    
    # Pump.fun trade program ID
    program_id = "6EF8rrecthR5Dkzon8Nwu78hRvfCKubJ14M5uBEwF6P"
    
    payload = {
        "jsonrpc": "2.0",
        "id": 1,
        "method": "getSignaturesForAddress",
        "params": [
            program_id,
            {
                "limit": 10,
                "commitment": "confirmed"
            }
        ]
    }
    
    async with aiohttp.ClientSession() as session:
        async with session.post(rpc_url, json=payload) as response:
            result = await response.json()
    
    if "result" in result:
        print("=== Recent Pump.fun Transactions ===")
        for i, tx in enumerate(result["result"][:5]):  # Show first 5
            sig = tx["signature"]
            print(f"\n{i+1}. {sig}")
            print(f"   Slot: {tx.get('slot')}")
            print(f"   Error: {tx.get('err')}")
            
            # Get transaction details to find token mint
            await get_tx_details(sig)

async def get_tx_details(tx_sig: str):
    """Get transaction details to extract token mint"""
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
    
    try:
        async with aiohttp.ClientSession() as session:
            async with session.post(rpc_url, json=payload) as response:
                result = await response.json()
        
        if "result" in result and result["result"]:
            tx_data = result["result"]
            meta = tx_data.get("meta", {})
            
            # Look for token mints in account keys
            if "transaction" in tx_data:
                message = tx_data["transaction"]["message"]
                if "accountKeys" in message:
                    accounts = message["accountKeys"]
                    
                    # Look for potential token mints (32-char base58 addresses)
                    token_candidates = []
                    for acc in accounts:
                        acc_str = acc if isinstance(acc, str) else str(acc)
                        # Skip known system accounts
                        if (len(acc_str) == 44 and  # Standard Solana address length
                            not acc_str.startswith("11111111111111111111111111111111") and
                            not acc_str.startswith("TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA") and
                            not acc_str.startswith("ComputeBudget111111111111111111111111111111") and
                            acc_str.endswith("pump")):  # Many pump.fun tokens end with "pump"
                            token_candidates.append(acc_str)
                    
                    if token_candidates:
                        print(f"   Token candidates: {token_candidates}")
                        return token_candidates[0]  # Return first candidate
                        
            # Check for errors
            if meta.get("err"):
                print(f"   Transaction failed: {meta['err']}")
            else:
                print(f"   Transaction successful")
                
    except Exception as e:
        print(f"   Error fetching details: {e}")
    
    return None

async def main():
    tokens = await get_recent_pump_transactions()
    
if __name__ == "__main__":
    asyncio.run(main())
