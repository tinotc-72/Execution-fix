#!/usr/bin/env python3
"""
Check what the expected creator_vault address actually is on-chain
"""

import asyncio
import httpx
from solders.pubkey import Pubkey

async def check_address_info():
    """Check the account info for the expected creator_vault"""
    
    expected_vault = "J6tqVTD9Fswag94sNU7cKatw5BDpq8MWUubktSFFS7uQ"
    rpc_url = "https://mainnet.helius-rpc.com/v0?api-key=7277139c-ff2c-4257-ad06-2db6aa16c315"
    
    print(f"🔍 Checking account info for: {expected_vault}")
    
    async with httpx.AsyncClient() as client:
        # Get account info
        response = await client.post(rpc_url, json={
            "jsonrpc": "2.0",
            "id": 1,
            "method": "getAccountInfo",
            "params": [expected_vault, {"encoding": "base64"}]
        })
        
        if response.status_code == 200:
            result = response.json().get("result", {})
            if result.get("value"):
                account_info = result["value"]
                owner = account_info.get("owner")
                lamports = account_info.get("lamports", 0)
                data_len = len(account_info.get("data", [""])[0]) if account_info.get("data") else 0
                
                print(f"✅ Account exists:")
                print(f"   Owner: {owner}")
                print(f"   Lamports: {lamports}")
                print(f"   Data length: {data_len}")
                
                # Check if it's owned by Pump.fun program
                pump_program = "6EF8rrecthR5Dkzon8Nwu78hRvfCKubJ14M5uBEwF6P"
                if owner == pump_program:
                    print(f"✅ Owned by Pump.fun program!")
                else:
                    print(f"❌ Not owned by Pump.fun program")
                    
            else:
                print("❌ Account does not exist")
        else:
            print(f"❌ Error: {response.status_code}")
            
    # Also check a recent successful Pump.fun transaction to see what creator_vault it uses
    print("\n🔍 Looking for recent successful Pump.fun transactions...")
    
    # Let's check the token mint account to get more info
    token_mint = "8MRAEdcfeVgqgGyTjjiMy6e99muFwzRkDsK4nR4Hpump"
    async with httpx.AsyncClient() as client:
        response = await client.post(rpc_url, json={
            "jsonrpc": "2.0",
            "id": 1,
            "method": "getAccountInfo",
            "params": [token_mint, {"encoding": "jsonParsed"}]
        })
        
        if response.status_code == 200:
            result = response.json().get("result", {})
            if result.get("value"):
                print(f"✅ Token mint {token_mint} exists")
                parsed = result["value"].get("data", {}).get("parsed", {})
                if parsed:
                    info = parsed.get("info", {})
                    print(f"   Decimals: {info.get('decimals')}")
                    print(f"   Supply: {info.get('supply')}")
                    print(f"   Mint authority: {info.get('mintAuthority')}")
                    print(f"   Freeze authority: {info.get('freezeAuthority')}")
            else:
                print(f"❌ Token mint {token_mint} does not exist")

if __name__ == "__main__":
    asyncio.run(check_address_info())