#!/usr/bin/env python3

import httpx
import json
import asyncio

async def test_transaction_fetch():
    """Test if we can fetch the transaction signature properly"""
    tx_sig = "2zwXd6Ddv4xkDTBUmT3H9xd46ufwwx6Q1gMoqisYhV42UPzdE1JXv4Kp9GhcL6Vn8k6qT6LWVtKoXNSVK1pcqgGG"
    rpc_url = "https://api.mainnet-beta.solana.com"
    
    print(f"🔍 Fetching transaction: {tx_sig}")
    print(f"🌐 RPC URL: {rpc_url}")
    
    resp = httpx.post(rpc_url, json={
        "jsonrpc": "2.0",
        "id": 1,
        "method": "getTransaction",
        "params": [tx_sig, {"encoding": "jsonParsed", "maxSupportedTransactionVersion": 0}]
    })
    
    print(f"📡 Response status: {resp.status_code}")
    
    if resp.status_code == 200:
        result = resp.json()
        print(f"✅ Response received")
        print(f"📋 Full response: {json.dumps(result, indent=2)}")
        
        if "result" in result and result["result"]:
            tx = result["result"]
            message = tx.get("transaction", {}).get("message", {})
            account_keys = message.get("accountKeys", [])
            instructions = message.get("instructions", [])
            
            print(f"🔑 Account keys count: {len(account_keys)}")
            print(f"📋 Instructions count: {len(instructions)}")
            
            if account_keys:
                print("🔑 First 5 account keys:")
                for i, key in enumerate(account_keys[:5]):
                    if isinstance(key, dict):
                        print(f"  {i}: {key.get('pubkey', 'unknown')}")
                    else:
                        print(f"  {i}: {key}")
            
            if instructions:
                print("📋 Instructions:")
                for i, inst in enumerate(instructions):
                    print(f"  {i}: {inst}")
        else:
            print("❌ No transaction result found")
    else:
        print(f"❌ Failed to fetch transaction: {resp.text}")

if __name__ == "__main__":
    asyncio.run(test_transaction_fetch())