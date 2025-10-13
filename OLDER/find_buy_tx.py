#!/usr/bin/env python3
"""
Find recent buy transactions on pump.fun
"""

import asyncio
import aiohttp
from env_keys import EnvKeys

async def find_buy_transactions():
    """Find recent buy transactions by looking for 'Buy' in logs"""
    keys = EnvKeys()
    rpc_url = f"https://mainnet.helius-rpc.com/v0/?api-key={keys.HELIUS_API_KEY}"
    
    # Get recent transactions from pump.fun trade program
    payload = {
        "jsonrpc": "2.0",
        "id": 1,
        "method": "getSignaturesForAddress",
        "params": [
            "6EF8rrecthR5Dkzon8Nwu78hRvfCKubJ14M5uBEwF6P",
            {
                "limit": 20,
                "commitment": "confirmed"
            }
        ]
    }
    
    async with aiohttp.ClientSession() as session:
        async with session.post(rpc_url, json=payload) as response:
            result = await response.json()
    
    if "result" in result:
        print("Looking for buy transactions...")
        
        for i, tx in enumerate(result["result"][:15]):  # Check first 15
            sig = tx["signature"]
            
            # Get transaction details
            tx_payload = {
                "jsonrpc": "2.0", 
                "id": 1,
                "method": "getTransaction",
                "params": [
                    sig,
                    {
                        "encoding": "json",
                        "commitment": "confirmed",
                        "maxSupportedTransactionVersion": 0
                    }
                ]
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.post(rpc_url, json=tx_payload) as response:
                    tx_result = await response.json()
            
            if "result" in tx_result and tx_result["result"]:
                tx_data = tx_result["result"]
                meta = tx_data.get("meta", {})
                
                # Check logs for "Buy" instruction
                logs = meta.get("logMessages", [])
                for log in logs:
                    if "Instruction: Buy" in log:
                        print(f"\n🎯 FOUND BUY TRANSACTION: {sig}")
                        print(f"   Slot: {tx_data.get('slot')}")
                        print(f"   Error: {meta.get('err')}")
                        return sig
                        
                # Also check for successful transactions without specific logs
                if not meta.get("err"):
                    message = tx_data["transaction"]["message"]
                    accounts = message.get("accountKeys", [])
                    
                    # Look for pump instructions
                    for ix in message.get("instructions", []):
                        program_idx = ix.get("programIdIndex", 0)
                        program_id = accounts[program_idx] if program_idx < len(accounts) else ""
                        
                        if program_id == "6EF8rrecthR5Dkzon8Nwu78hRvfCKubJ14M5uBEwF6P":
                            print(f"\n📝 Pump instruction in: {sig}")
                            print(f"   Success: {meta.get('err') is None}")
                            
                            # Check if this might be a buy (no "Sell" in logs)
                            is_sell = any("Instruction: Sell" in log for log in logs)
                            if not is_sell:
                                print(f"   ^ Potential BUY transaction!")
                                return sig
    
    return None

async def main():
    buy_tx = await find_buy_transactions()
    if buy_tx:
        print(f"\nFound potential buy transaction: {buy_tx}")
        
        # Analyze it
        from simple_analyze import simple_analyze
        print("\n" + "="*50 + "\n")
        await simple_analyze(buy_tx)
    else:
        print("No buy transactions found in recent history")

if __name__ == "__main__":
    asyncio.run(main())
