#!/usr/bin/env python3

import asyncio
import httpx
from solders.pubkey import Pubkey

async def check_ata_status():
    """Check if our ATA already exists"""
    user_pubkey = Pubkey.from_string("A26P5WXU5SwdgKNAP6nkyYFELv4MkmK7sDGKt7Nu3AoB")
    mint = Pubkey.from_string("8MRAEdcfeVgqgGyTjjiMy6e99muFwzRkDsK4nR4Hpump")
    TOKEN_PROGRAM_ID = Pubkey.from_string("TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA")
    ASSOCIATED_TOKEN_PROGRAM_ID = Pubkey.from_string("ATokenGPvbdGVxr1b2hvZbsiqW5xWH25efTNsLJA8knL")
    
    # Derive ATA address
    user_token_account, _ = Pubkey.find_program_address(
        [
            bytes(user_pubkey),
            bytes(TOKEN_PROGRAM_ID),
            bytes(mint)
        ],
        ASSOCIATED_TOKEN_PROGRAM_ID
    )
    
    print(f"👤 User: {user_pubkey}")
    print(f"🪙 Mint: {mint}")
    print(f"🏦 Expected ATA: {user_token_account}")
    
    # Check if ATA exists
    helius_url = "https://mainnet.helius-rpc.com/v0?api-key=7277139c-ff2c-4257-ad06-2db6aa16c315"
    resp = httpx.post(helius_url, json={
        "jsonrpc": "2.0",
        "id": 1,
        "method": "getAccountInfo",
        "params": [str(user_token_account), {"encoding": "base64"}]
    })
    
    data = resp.json()
    ata_exists = data.get("result", {}).get("value") is not None
    
    if ata_exists:
        print(f"✅ ATA already exists - no need to create")
        account_data = data.get("result", {}).get("value", {})
        print(f"📊 Account data: {account_data}")
    else:
        print(f"❌ ATA does not exist - needs creation")
    
    return ata_exists

if __name__ == "__main__":
    asyncio.run(check_ata_status())