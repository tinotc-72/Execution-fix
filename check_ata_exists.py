#!/usr/bin/env python3
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

import asyncio
from solders.pubkey import Pubkey
from solana.rpc.async_api import AsyncClient
from env_keys import EnvKeys

async def check_ata_exists():
    env = EnvKeys()
    async with AsyncClient(env.HELIUS_RPC_URL) as client:
        # Our wallet and token
        our_wallet = "A26P5WXU5SwdgKNAP6nkyYFELv4MkmK7sDGKt7Nu3AoB"
        token_mint = "mvqgb1pa4pyTcqDnKjhFV2Zi97qTb9kn16obh4T6RYd"
        our_ata = "BfuNmxQzgdF6DXeahuAMK3xKR6BD2RJat8Pqa16nkwST"
        
        print(f"Checking ATA: {our_ata}")
        print(f"For wallet: {our_wallet}")
        print(f"Token mint: {token_mint}")
        
        # Check if ATA exists
        try:
            ata_info = await client.get_account_info(Pubkey.from_string(our_ata))
            if ata_info.value is None:
                print("❌ ATA does NOT exist - needs to be created")
            else:
                print("✅ ATA exists")
                print(f"   Owner: {ata_info.value.owner}")
                print(f"   Lamports: {ata_info.value.lamports}")
                print(f"   Data length: {len(ata_info.value.data) if ata_info.value.data else 0}")
        except Exception as e:
            print(f"❌ Error checking ATA: {e}")
            
        # Also check original wallet's ATA
        orig_ata = "2xgwRdihJw7LeESyVTGqfDwVkeB2KFDTZVU9ZCc8Y9Xk"
        print(f"\nChecking original ATA: {orig_ata}")
        try:
            orig_info = await client.get_account_info(Pubkey.from_string(orig_ata))
            if orig_info.value is None:
                print("❌ Original ATA does NOT exist")
            else:
                print("✅ Original ATA exists")
                print(f"   Owner: {orig_info.value.owner}")
                print(f"   Lamports: {orig_info.value.lamports}")
        except Exception as e:
            print(f"❌ Error checking original ATA: {e}")

if __name__ == "__main__":
    asyncio.run(check_ata_exists())