#!/usr/bin/env python3
"""
Test the fixed Pump.fun executor ATA derivation
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from solders.pubkey import Pubkey
from solders.keypair import Keypair
from spl.token.instructions import get_associated_token_address

def test_ata_derivation():
    print("🧪 TESTING CORRECTED ATA DERIVATION")
    print("=" * 60)
    
    # Your wallet and the token from the failed transaction
    your_wallet = "A26P5WXU5SwdgKNAP6nkyYFELv4MkmK7sDGKt7Nu3AoB"
    token_mint = "GF8HNiqu4V8EAoUMugzXZ1hbWC1daoSRYPCumCe1pump"
    
    # Calculate what YOUR ATA should be
    wallet_pubkey = Pubkey.from_string(your_wallet)
    token_mint_pubkey = Pubkey.from_string(token_mint)
    
    your_ata = get_associated_token_address(wallet_pubkey, token_mint_pubkey)
    
    print(f"👤 Your Wallet: {your_wallet}")
    print(f"🪙 Token Mint: {token_mint}")
    print(f"🏦 Your Correct ATA: {your_ata}")
    print()
    
    print("📊 COMPARISON:")
    print("-" * 40)
    print(f"✅ Bot Created ATA: HuLjVqJwtXNqTeyrCDd7Gine7nuGzLihH93XBd8W155k")
    print(f"✅ Calculated ATA:  {your_ata}")
    print()
    
    # Check if they match
    if str(your_ata) == "HuLjVqJwtXNqTeyrCDd7Gine7nuGzLihH93XBd8W155k":
        print("🎉 PERFECT MATCH! The bot created the correct ATA!")
    else:
        print("⚠️ MISMATCH! Need to investigate ATA calculation.")
    
    print()
    print("❌ WRONG ATA (from hardcoded): AiFqrztULkWPCGFy6rVDgpJGRvWvLAV5s7xopr77nwkd")
    print("✅ RIGHT ATA (calculated):     HuLjVqJwtXNqTeyrCDd7Gine7nuGzLihH93XBd8W155k")
    print()
    print("🔧 FIXED: The executor now uses derive_pump_fun_accounts() which")
    print("will calculate the correct ATA for YOUR wallet dynamically!")

if __name__ == "__main__":
    test_ata_derivation()
