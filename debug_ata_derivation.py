#!/usr/bin/env python3
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from solders.pubkey import Pubkey
from spl.token.constants import ASSOCIATED_TOKEN_PROGRAM_ID, TOKEN_PROGRAM_ID

def derive_ata(owner_pubkey, mint_pubkey):
    """Derive Associated Token Account address"""
    owner_pk = Pubkey.from_string(owner_pubkey) if isinstance(owner_pubkey, str) else owner_pubkey
    mint_pk = Pubkey.from_string(mint_pubkey) if isinstance(mint_pubkey, str) else mint_pubkey
    
    ata_address, bump = Pubkey.find_program_address(
        [bytes(owner_pk), bytes(TOKEN_PROGRAM_ID), bytes(mint_pk)],
        ASSOCIATED_TOKEN_PROGRAM_ID
    )
    return ata_address, bump

# Our wallet and the token from the real transaction
our_wallet = "A26P5WXU5SwdgKNAP6nkyYFELv4MkmK7sDGKt7Nu3AoB"
token_mint = "mvqgb1pa4pyTcqDnKjhFV2Zi97qTb9kn16obh4T6RYd"

print("=== ATA Derivation Debug ===")
print(f"Our Wallet: {our_wallet}")
print(f"Token Mint: {token_mint}")

# Derive our ATA
our_ata, bump = derive_ata(our_wallet, token_mint)
print(f"Our Derived ATA: {our_ata}")
print(f"Bump: {bump}")

# Original wallet from the transaction
orig_wallet = "3Z19SwGej4xwKh9eiHyx3eVWHjBDEgGHeqrKtmhNcxsv"
orig_ata, orig_bump = derive_ata(orig_wallet, token_mint)
print(f"\nOriginal Wallet: {orig_wallet}")
print(f"Original ATA: {orig_ata}")
print(f"Original Bump: {orig_bump}")