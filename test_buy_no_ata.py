#!/usr/bin/env python3

import asyncio
import sys
sys.path.append('/Users/tinotchinyoka/Desktop/Algo Trading/Axiom Sniper 13.03.25/Attempt/Hope')

from complete_mev_bot import CompleteMEVBot
from config import get_wallet_config
import logging

logging.basicConfig(level=logging.INFO)

async def test_buy_without_ata_bundle():
    """Test buy without ATA bundling to match successful transaction structure"""
    
    print("🔧 Testing buy without ATA bundling...")
    
    # Get configuration
    config = get_wallet_config()
    
    # Initialize bot
    bot = CompleteMEVBot(config)
    
    # Create ATA instruction manually
    from solders.pubkey import Pubkey
    from solders.instruction import Instruction, AccountMeta
    
    mint = Pubkey.from_string("8MRAEdcfeVgqgGyTjjiMy6e99muFwzRkDsK4nR4Hpump")
    user_token_account = bot.get_associated_token_address(mint, bot.keypair.pubkey())
    
    # Check if ATA exists
    import httpx
    resp = httpx.post(
        bot.env.HELIUS_RPC_URL,
        json={
            "jsonrpc": "2.0",
            "id": 1,
            "method": "getAccountInfo",
            "params": [str(user_token_account), {"encoding": "base64"}]
        }
    )
    data = resp.json()
    ata_exists = data.get("result", {}).get("value") is not None
    
    print(f"🏦 ATA exists: {ata_exists}")
    
    if not ata_exists:
        print("❌ ATA must be created first. Cannot proceed with non-bundled approach.")
        return
    
    # Try buy without bundling (this should match successful transaction structure)
    # Note: This would require modifying the bot to skip ATA creation
    print("✅ ATA exists, can proceed with direct buy")

if __name__ == "__main__":
    asyncio.run(test_buy_without_ata_bundle())