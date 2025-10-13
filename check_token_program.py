#!/usr/bin/env python3

import asyncio
import json
from solders.pubkey import Pubkey
from solana.rpc.async_api import AsyncClient

async def check_token_program():
    """Check which program owns the bonding curve for a specific token"""
    
    # Token from the failed transaction
    token_mint = "FRP9rmngPuVJb4Ghm9UkYLJmVgJB7rUjbV44TA9AWB4n"
    
    # Old and new Pump.fun program IDs
    OLD_PUMP_PROGRAM = "6EF8rrecthR5Dkzon8Nwu78hRvfCKubJ14M5uBEwF6P"
    NEW_PUMP_PROGRAM = "pAMMBay6oceH9fJKBRHGP5D4bD4sWpmSwMn52FMfXEA"
    
    mint_pubkey = Pubkey.from_string(token_mint)
    
    # Derive bonding curve for both old and new programs
    old_bonding_curve = Pubkey.find_program_address(
        [b"bonding-curve", bytes(mint_pubkey)],
        Pubkey.from_string(OLD_PUMP_PROGRAM)
    )[0]
    
    new_bonding_curve = Pubkey.find_program_address(
        [b"bonding-curve", bytes(mint_pubkey)],
        Pubkey.from_string(NEW_PUMP_PROGRAM)
    )[0]
    
    print(f"Token: {token_mint}")
    print(f"Old Program Bonding Curve: {old_bonding_curve}")
    print(f"New Program Bonding Curve: {new_bonding_curve}")
    
    # Check which ones actually exist on-chain
    client = AsyncClient("https://mainnet.helius-rpc.com/v0?api-key=7277139c-ff2c-4257-ad06-2db6aa16c315")
    
    try:
        # Check old bonding curve
        old_account = await client.get_account_info(old_bonding_curve)
        if old_account.value:
            print(f"✅ OLD bonding curve EXISTS - Owner: {old_account.value.owner}")
        else:
            print("❌ OLD bonding curve does NOT exist")
            
        # Check new bonding curve  
        new_account = await client.get_account_info(new_bonding_curve)
        if new_account.value:
            print(f"✅ NEW bonding curve EXISTS - Owner: {new_account.value.owner}")
        else:
            print("❌ NEW bonding curve does NOT exist")
            
    except Exception as e:
        print(f"Error checking accounts: {e}")
    finally:
        await client.close()

if __name__ == "__main__":
    asyncio.run(check_token_program())
