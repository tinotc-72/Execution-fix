#!/usr/bin/env python3
"""
Check if we can use the exact same accounts from the successful transaction
"""

import asyncio
from solders.pubkey import Pubkey
from minimal_tx_builder import create_buy_instruction, get_associated_token_address
from debug_buy_only import *

async def test_with_exact_accounts():
    """Test using the exact token and trying to derive the same accounts as successful transaction"""
    
    # Use the same token from the successful transaction
    token_mint = Pubkey.from_string("6nTfw8wkRRqJviT9JZvRyeR2WV682ETZEf7LudQzpump")
    wallet = WALLET
    token_ata = get_associated_token_address(wallet.pubkey(), token_mint)
    
    print(f"Token mint: {token_mint}")
    print(f"Our wallet: {wallet.pubkey()}")
    print(f"Our token ATA: {token_ata}")
    
    # From the successful transaction, the accounts were:
    successful_accounts = [
        "4wTV1YmiEkRvAtNtsSGPtUrqRYQMe5SKy2uB4Jjaxnjf",  # 0: Config/global
        "G5UZAVbAf46s7cKWoyKu8kYTip9DGTpbLZ2qa9Aq69dP",  # 1: Some other PDA
        "6nTfw8wkRRqJviT9JZvRyeR2WV682ETZEf7LudQzpump", # 2: Token mint
        "9y2pMaFYhLasS5guL1YyfBSfXzqybMyxcCn5XcawRjfb", # 3: Token vault
        "HfQEZpR8wnKk3qTiUg1EjhAtzGcHdLKzGsavJUQLEFcz", # 4: Route state
        "7sFAH9hpWLMr6UvLTN1goYY9MJ3M8usqvPgqoQhWW31s", # 5: Token account
        "2NDxhZMdJbEgHEHVDfdGu6xv7NCLgMqSVUjiuZG88ZNz", # 6: User wallet
        "11111111111111111111111111111111",              # 7: System program
        "TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA",     # 8: Token program
        "Cia7DN8dU9nbwozAQ94xegdBuQuY92q4ythwBWiypSFD",     # 9: Some account
        "Ce6TQqeHC9p8KetsN6JsjHK7UTZk7nasjjnr7XxXp9F1",     # 10: Event authority
        "6EF8rrecthR5Dkzon8Nwu78hRvfCKubJ14M5uBEwF6P",      # 11: Program ID
    ]
    
    print(f"\n=== Successful Transaction Account Analysis ===")
    print(f"Config/Global: {successful_accounts[0]}")
    print(f"Some PDA: {successful_accounts[1]}")
    print(f"Token Mint: {successful_accounts[2]} ✓ (matches)")
    print(f"Token Vault: {successful_accounts[3]}")
    print(f"Route State: {successful_accounts[4]}")
    print(f"Token Account: {successful_accounts[5]}")
    print(f"User Wallet: {successful_accounts[6]}")
    
    # Let's see what PDAs we derive for this same token
    from minimal_tx_builder import (
        derive_config_pda,
        derive_route_params_pda, 
        derive_route_state_pda,
        derive_token_vault_pda
    )
    
    print(f"\n=== Our PDA Derivations ===")
    our_config = derive_config_pda()
    our_route_params = derive_route_params_pda(token_mint)
    our_route_state = derive_route_state_pda(token_mint)
    our_token_vault = derive_token_vault_pda(token_mint)
    
    print(f"Our config PDA: {our_config}")
    print(f"Our route params: {our_route_params}")
    print(f"Our route state: {our_route_state}")
    print(f"Our token vault: {our_token_vault}")
    
    print(f"\n=== Comparison ===")
    print(f"Config match: {str(our_config) == successful_accounts[0]} ({our_config} vs {successful_accounts[0]})")
    print(f"Route params match: {str(our_route_params) == successful_accounts[1]} ({our_route_params} vs {successful_accounts[1]})")
    print(f"Route state match: {str(our_route_state) == successful_accounts[4]} ({our_route_state} vs {successful_accounts[4]})")
    print(f"Token vault match: {str(our_token_vault) == successful_accounts[3]} ({our_token_vault} vs {successful_accounts[3]})")

if __name__ == "__main__":
    asyncio.run(test_with_exact_accounts())
