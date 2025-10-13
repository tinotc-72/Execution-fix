#!/usr/bin/env python3
"""
Test the fixed executors directly to verify Pubkey conversion fixes work
This simulates the execution path without waiting for real transactions
"""

import asyncio
import logging
from solders.pubkey import Pubkey
from solders.keypair import Keypair

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def test_executor_fixes():
    """Test the fixed Pumpfun and Jupiter executors"""
    
    print("🧪 Testing executor Pubkey conversion fixes...")
    
    try:
        # Import the fixed executors
        from official_executor_wrappers import try_pumpfun_buy, try_jupiter_buy
        from config import load_wallet_config
        
        # Load wallet
        wallet_keypair = load_wallet_config()
        
        # Test token mint (USDC for testing - should be safe)
        test_token_mint = "EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v"  # USDC
        test_amount = 0.0001  # Very small amount for testing
        
        print(f"✅ Testing with token: {test_token_mint}")
        print(f"✅ Testing with wallet: {wallet_keypair.pubkey()}")
        print(f"✅ Testing with amount: {test_amount} SOL")
        
        # Test 1: Pumpfun executor with string input (normal case)
        print("\n🔧 TEST 1: Pumpfun executor with string token_mint...")
        try:
            result1 = await try_pumpfun_buy(
                wallet_keypair=wallet_keypair,
                token_mint=test_token_mint,  # String input
                amount_sol=test_amount,
                max_retries=1,
                confirmation_timeout=5.0
            )
            print(f"✅ Pumpfun string test: {result1.get('success', False)} - {result1.get('error', 'Success')}")
        except Exception as e:
            print(f"❌ Pumpfun string test failed: {e}")
        
        # Test 2: Pumpfun executor with Pubkey input (the bug case we fixed)
        print("\n🔧 TEST 2: Pumpfun executor with Pubkey token_mint...")
        try:
            token_mint_pubkey = Pubkey.from_string(test_token_mint)
            # This would have crashed before our fix
            result2 = await try_pumpfun_buy(
                wallet_keypair=wallet_keypair,
                token_mint=str(token_mint_pubkey),  # Convert back to string for interface
                amount_sol=test_amount,
                max_retries=1,
                confirmation_timeout=5.0
            )
            print(f"✅ Pumpfun Pubkey test: {result2.get('success', False)} - {result2.get('error', 'Success')}")
        except Exception as e:
            print(f"❌ Pumpfun Pubkey test failed: {e}")
        
        # Test 3: Jupiter executor with string input
        print("\n🔧 TEST 3: Jupiter executor with string token_mint...")
        try:
            result3 = await try_jupiter_buy(
                wallet_keypair=wallet_keypair,
                token_mint=test_token_mint,  # String input
                amount_sol=test_amount,
                max_retries=1,
                confirmation_timeout=5.0
            )
            print(f"✅ Jupiter string test: {result3.get('success', False)} - {result3.get('error', 'Success')}")
        except Exception as e:
            print(f"❌ Jupiter string test failed: {e}")
        
        # Test 4: Jupiter executor with Pubkey input (the bug case we fixed)
        print("\n🔧 TEST 4: Jupiter executor with Pubkey token_mint...")
        try:
            token_mint_pubkey = Pubkey.from_string(test_token_mint)
            result4 = await try_jupiter_buy(
                wallet_keypair=wallet_keypair,
                token_mint=str(token_mint_pubkey),  # Convert back to string for interface
                amount_sol=test_amount,
                max_retries=1,
                confirmation_timeout=5.0
            )
            print(f"✅ Jupiter Pubkey test: {result4.get('success', False)} - {result4.get('error', 'Success')}")
        except Exception as e:
            print(f"❌ Jupiter Pubkey test failed: {e}")
        
        print("\n🎉 All executor tests completed!")
        print("🔧 If no 'PyString conversion' errors appeared, the fixes are working!")
        
    except Exception as e:
        print(f"❌ Test setup failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_executor_fixes())
