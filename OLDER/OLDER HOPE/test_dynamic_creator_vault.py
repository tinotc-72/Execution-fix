#!/usr/bin/env python3
"""
Test dynamic creator vault derivation for router-based tokens
"""

import asyncio
import logging
from solders.pubkey import Pubkey

from production_pump_trading_bot import PumpFunTradingBot, TradeConfig

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

async def test_creator_vault_derivation():
    """Test creator vault derivation for different tokens"""
    
    print("🧪 TESTING DYNAMIC CREATOR VAULT DERIVATION")
    print("="*60)
    
    # Initialize bot
    config = TradeConfig()
    bot = PumpFunTradingBot(config)
    
    # Test tokens
    test_tokens = [
        {
            "name": "Standard Token (Working)",
            "mint": "6nTfw8wkRRqJviT9JZvRyeR2WV682ETZEf7LudQzpump",
            "expected_vault": "Cia7DN8dU9nbwozAQ94xegdBuQuY92q4ythwBWiypSFD"
        },
        {
            "name": "Router Token (Problematic)", 
            "mint": "766cu48DWcanNfre5p4Hs9e13UaBjSQxSFy8mzJcpump",
            "expected_vault": "HZte1mnbgg288wDnLndop6kibW3DqDHBY4C933LjMorL"
        }
    ]
    
    for token_info in test_tokens:
        print(f"\n📍 Testing: {token_info['name']}")
        print(f"   Mint: {token_info['mint']}")
        print(f"   Expected Vault: {token_info['expected_vault']}")
        
        token_mint = Pubkey.from_string(token_info['mint'])
        
        # Test dynamic derivation
        try:
            derived_vault = await bot.get_optimal_creator_vault(token_mint)
            print(f"   ✅ Derived Vault: {derived_vault}")
            
            # Check if it matches expected
            if str(derived_vault) == token_info['expected_vault']:
                print(f"   ✅ MATCH! Derivation successful")
            else:
                print(f"   ❌ MISMATCH! Got {derived_vault}, expected {token_info['expected_vault']}")
                
            # Test validation
            is_valid = await bot.validate_creator_vault(derived_vault)
            print(f"   📊 Vault Valid: {is_valid}")
            
        except Exception as e:
            print(f"   ❌ Error: {e}")
    
    # Test fallback derivation patterns
    print(f"\n🔍 Testing PDA Derivation Patterns")
    router_token = Pubkey.from_string("766cu48DWcanNfre5p4Hs9e13UaBjSQxSFy8mzJcpump")
    
    patterns = [
        [b"creator", bytes(router_token)],
        [b"creator_vault", bytes(router_token)], 
        [bytes(router_token), b"creator"],
        [bytes(router_token), b"creator_vault"],
        [b"vault", bytes(router_token)]
    ]
    
    for i, seeds in enumerate(patterns):
        try:
            creator_vault, bump = Pubkey.find_program_address(seeds, bot.PUMP_PROGRAM)
            print(f"   Pattern {i+1}: {creator_vault} (bump: {bump})")
            
            # Check if this matches the expected router vault
            if str(creator_vault) == "HZte1mnbgg288wDnLndop6kibW3DqDHBY4C933LjMorL":
                print(f"   ✅ FOUND MATCH! Pattern {i+1} produces correct vault")
                
        except Exception as e:
            print(f"   Pattern {i+1}: Error - {e}")
    
    await bot.client.close()
    print("\n✅ Test completed")

if __name__ == "__main__":
    asyncio.run(test_creator_vault_derivation())
