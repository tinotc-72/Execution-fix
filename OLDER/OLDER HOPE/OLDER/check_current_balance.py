#!/usr/bin/env python3
"""
Check current token balance to understand what's happening
"""

import asyncio
from solders.pubkey import Pubkey
from minimal_tx_builder import get_associated_token_address
from config import WALLET
from utils import get_token_account_balance

TOKEN_MINT = "6nTfw8wkRRqJviT9JZvRyeR2WV682ETZEf7LudQzpump"

async def main():
    wallet = WALLET
    token_mint = Pubkey.from_string(TOKEN_MINT)
    token_ata = get_associated_token_address(wallet.pubkey(), token_mint)
    
    print(f"Wallet: {wallet.pubkey()}")
    print(f"Token mint: {token_mint}")
    print(f"Token ATA: {token_ata}")
    
    balance = await get_token_account_balance(token_ata)
    print(f"Current token balance: {balance:,} tokens" if balance else "No tokens found")

if __name__ == "__main__":
    asyncio.run(main())
