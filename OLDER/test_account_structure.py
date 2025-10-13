#!/usr/bin/env python3
"""
Test the generalized bot with the known working token to ensure account structure compatibility
"""

import asyncio
import logging
from generalized_pump_trading_bot import GeneralizedPumpTradingBot, TradeConfig

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def test_known_working_token():
    """Test with the token we know works to verify account structure"""
    
    # Known working token
    working_token = "6nTfw8wkRRqJviT9JZvRyeR2WV682ETZEf7LudQzpump"
    
    print("🔧 TESTING GENERALIZED BOT WITH KNOWN WORKING TOKEN")
    print("="*80)
    print(f"Token: {working_token}")
    print("This should work since we've successfully traded this token before")
    
    config = TradeConfig(sol_amount=0.001, max_retries=2)
    bot = GeneralizedPumpTradingBot(config)
    
    try:
        print(f"\n🔍 Getting token information...")
        token_info = await bot.get_token_info(working_token)
        
        print(f"✅ Token valid: {token_info.is_valid}")
        print(f"   Bonding Curve: {token_info.bonding_curve}")
        print(f"   Bonding Curve ATA: {token_info.bonding_curve_ata}")
        
        # Check that derived addresses match the hardcoded working ones
        expected_bonding_curve = "9y2pMaFYhLasS5guL1YyfBSfXzqybMyxcCn5XcawRjfb"
        expected_bonding_curve_ata = "HfQEZpR8wnKk3qTiUg1EjhAtzGcHdLKzGsavJUQLEFcz"
        
        print(f"\n🔍 Verifying derived addresses match working hardcoded ones:")
        print(f"   Expected BC: {expected_bonding_curve}")
        print(f"   Derived BC:  {token_info.bonding_curve}")
        print(f"   Match: {str(token_info.bonding_curve) == expected_bonding_curve}")
        
        print(f"   Expected ATA: {expected_bonding_curve_ata}")
        print(f"   Derived ATA:  {token_info.bonding_curve_ata}")
        print(f"   Match: {str(token_info.bonding_curve_ata) == expected_bonding_curve_ata}")
        
        if (str(token_info.bonding_curve) == expected_bonding_curve and 
            str(token_info.bonding_curve_ata) == expected_bonding_curve_ata):
            print(f"✅ Perfect! Generalized derivation matches working addresses!")
            
            # Test a small buy
            print(f"\n🛒 Testing small buy trade...")
            buy_result = await bot.buy_token(working_token, sol_amount=0.001)
            
            print(f"Buy result: {buy_result.result.value}")
            if buy_result.signature:
                print(f"Transaction: https://solscan.io/tx/{buy_result.signature}")
                if buy_result.result.value == 'success':
                    print(f"Tokens received: {buy_result.tokens_amount:,}")
                    print(f"✅ Generalized bot successfully executed buy!")
                else:
                    print(f"❌ Buy failed: {buy_result.error_message}")
            else:
                print(f"❌ Buy failed: {buy_result.error_message}")
        else:
            print(f"❌ Address derivation mismatch - need to fix derivation logic")
        
    except Exception as e:
        logger.error(f"Test error: {e}")
        
    finally:
        await bot.close()

async def debug_account_structure():
    """Debug the account structure being used"""
    
    print(f"\n🔍 DEBUGGING ACCOUNT STRUCTURE")
    print("="*50)
    
    from production_pump_trading_bot import PumpFunTradingBot
    from solders.pubkey import Pubkey
    
    # Create both bots
    prod_config = TradeConfig(sol_amount=0.001)
    prod_bot = PumpFunTradingBot(prod_config)
    gen_bot = GeneralizedPumpTradingBot(prod_config)
    
    try:
        # Test token
        token_mint = Pubkey.from_string("6nTfw8wkRRqJviT9JZvRyeR2WV682ETZEf7LudQzpump")
        bonding_curve = Pubkey.from_string("9y2pMaFYhLasS5guL1YyfBSfXzqybMyxcCn5XcawRjfb")
        bonding_curve_ata = Pubkey.from_string("HfQEZpR8wnKk3qTiUg1EjhAtzGcHdLKzGsavJUQLEFcz")
        
        # Get account structures from both
        prod_accounts = prod_bot._build_trade_accounts(token_mint, bonding_curve, bonding_curve_ata)
        gen_accounts = gen_bot._build_trade_accounts(token_mint, bonding_curve, bonding_curve_ata)
        
        print(f"Production bot accounts ({len(prod_accounts)}):")
        for i, acc in enumerate(prod_accounts):
            print(f"  [{i}] {acc.pubkey} (signer: {acc.is_signer}, writable: {acc.is_writable})")
        
        print(f"\nGeneralized bot accounts ({len(gen_accounts)}):")
        for i, acc in enumerate(gen_accounts):
            print(f"  [{i}] {acc.pubkey} (signer: {acc.is_signer}, writable: {acc.is_writable})")
        
        # Check if they match
        accounts_match = len(prod_accounts) == len(gen_accounts)
        if accounts_match:
            for i, (prod_acc, gen_acc) in enumerate(zip(prod_accounts, gen_accounts)):
                if (prod_acc.pubkey != gen_acc.pubkey or 
                    prod_acc.is_signer != gen_acc.is_signer or 
                    prod_acc.is_writable != gen_acc.is_writable):
                    accounts_match = False
                    print(f"❌ Mismatch at position {i}:")
                    print(f"   Prod: {prod_acc.pubkey} (s:{prod_acc.is_signer}, w:{prod_acc.is_writable})")
                    print(f"   Gen:  {gen_acc.pubkey} (s:{gen_acc.is_signer}, w:{gen_acc.is_writable})")
                    break
        
        if accounts_match:
            print(f"✅ Account structures match perfectly!")
        else:
            print(f"❌ Account structures differ")
        
    except Exception as e:
        logger.error(f"Debug error: {e}")
        
    finally:
        await prod_bot.close()
        await gen_bot.close()

if __name__ == "__main__":
    asyncio.run(test_known_working_token())
    asyncio.run(debug_account_structure())
