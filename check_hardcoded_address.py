#!/usr/bin/env python3
"""
Check what the hardcoded associated_user address is
"""

import asyncio
from env_keys import EnvKeys
from solders.pubkey import Pubkey
import httpx

async def check_hardcoded_address():
    """Check the hardcoded associated_user address"""
    
    # From working executor
    hardcoded_address = "HapyT99AvwPNMcJQWH33hiyBPKhsi5dfETQuJ1EbejTT"
    
    env = EnvKeys()
    
    print(f"🔍 Checking hardcoded address: {hardcoded_address}")
    
    async with httpx.AsyncClient(timeout=10.0) as client:
        response = await client.post(
            env.HELIUS_RPC_URL,
            json={
                "jsonrpc": "2.0",
                "id": 1,
                "method": "getAccountInfo",
                "params": [hardcoded_address, {"encoding": "jsonParsed"}]
            }
        )
        
        data = response.json()
        result = data.get("result", {}).get("value")
        
        if result:
            print(f"✅ Account exists!")
            print(f"   Owner: {result.get('owner')}")
            print(f"   Lamports: {result.get('lamports')}")
            print(f"   Data: {result.get('data', {}).get('parsed') or 'Not parsed'}")
        else:
            print(f"❌ Account does not exist")
            
    # Also check if it's a known system account
    try:
        pubkey = Pubkey.from_string(hardcoded_address)
        print(f"   Valid pubkey: {pubkey}")
    except Exception as e:
        print(f"   Invalid pubkey: {e}")

if __name__ == "__main__":
    asyncio.run(check_hardcoded_address())
