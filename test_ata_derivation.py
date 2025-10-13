#!/usr/bin/env python3
"""
Test ATA Creation with correct derivation
"""

import asyncio
from solders.pubkey import Pubkey
from spl.token.instructions import get_associated_token_address
from config import WALLET

async def test_ata_derivation():
    """Test if ATA derivation is working correctly"""
    
    print(f"🔧 TESTING ATA DERIVATION")
    print(f"Your wallet: {WALLET.pubkey()}")
    print("=" * 80)
    
    # Test with the token from the failed transaction
    # We need to find what token was being traded
    
    # Common meme coin for testing
    test_token = "DAjnBrfGGYtC2QFypWMZivxTETKF9Abu8ZK17VZ5pump"  # From earlier successful trades
    
    try:
        wallet_pubkey = WALLET.pubkey()
        token_mint_pubkey = Pubkey.from_string(test_token)
        
        print(f"🪙 Token: {test_token}")
        print(f"📱 Wallet: {wallet_pubkey}")
        
        # Calculate ATA address
        ata_address = get_associated_token_address(
            owner=wallet_pubkey,
            mint=token_mint_pubkey
        )
        
        print(f"🎯 Calculated ATA: {ata_address}")
        print(f"✅ ATA derivation successful!")
        
        # Test the derivation parameters
        print(f"\n🔍 DERIVATION PARAMETERS:")
        print(f"   Owner: {wallet_pubkey} (type: {type(wallet_pubkey)})")
        print(f"   Mint: {token_mint_pubkey} (type: {type(token_mint_pubkey)})")
        print(f"   ATA: {ata_address} (type: {type(ata_address)})")
        
        return True
        
    except Exception as e:
        print(f"❌ ATA derivation failed: {e}")
        import traceback
        print(f"❌ Traceback: {traceback.format_exc()}")
        return False

if __name__ == "__main__":
    success = asyncio.run(test_ata_derivation())
    if success:
        print(f"\n✅ ATA derivation is working correctly")
        print(f"🔍 The issue must be elsewhere in the execution chain")
    else:
        print(f"\n❌ ATA derivation has issues that need fixing")
