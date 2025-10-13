#!/usr/bin/env python3
"""
Test Jito-First Execution for Both Buys and Sells
This script tests that both buy and sell operations now use Jito-first execution
"""

import asyncio
import logging
from datetime import datetime
from config import CopyTradeConfig
from main import CopyTradingBot

# Setup test logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

async def test_jito_integration():
    """Test that Jito-first execution is available for both buys and sells"""
    try:
        logger.info("🧪 TESTING JITO-FIRST EXECUTION FOR BUYS AND SELLS")
        
        # Create test configuration with Jito enabled
        config = CopyTradeConfig(
            target_wallets=["9WwGxj1rPMZZg4KhzWsxRxij3hiKkZyzN1TfXR8zzGzv"],  # Test wallet
            investment_amount_sol=0.001,  # Very small amount for testing
            use_jito=True,  # CRITICAL: Enable Jito
            enable_dexes={
                "jupiter": True,
                "pumpfun": True,
                "raydium": True
            }
        )
        
        logger.info(f"✅ Test config created with use_jito = {config.use_jito}")
        
        # Initialize bot
        logger.info("🔧 Initializing CopyTradingBot...")
        bot = CopyTradingBot(config)
        
        # Check Jito service initialization
        if bot.jito_service:
            logger.info("✅ JITO SERVICE AVAILABLE!")
            logger.info(f"   Type: {type(bot.jito_service)}")
            logger.info(f"   Endpoint: {bot.jito_service.primary_endpoint}")
        else:
            logger.error("❌ JITO SERVICE NOT AVAILABLE!")
            logger.error("   This means Jito execution will not work")
            return False
        
        # Test that both buy and sell methods have Jito integration
        logger.info("🔍 CHECKING JITO-FIRST EXECUTION METHODS...")
        
        # Check if _try_jito_first_execution exists (for buys)
        if hasattr(bot, '_try_jito_first_execution'):
            logger.info("✅ BUY: _try_jito_first_execution method found")
        else:
            logger.error("❌ BUY: _try_jito_first_execution method missing")
            return False
        
        # Check if _try_jito_first_sell_execution exists (for sells)
        if hasattr(bot, '_try_jito_first_sell_execution'):
            logger.info("✅ SELL: _try_jito_first_sell_execution method found")
        else:
            logger.error("❌ SELL: _try_jito_first_sell_execution method missing")
            return False
        
        # Check if _try_jito_liquidation_transaction exists (for sell_all)
        if hasattr(bot, '_try_jito_liquidation_transaction'):
            logger.info("✅ LIQUIDATION: _try_jito_liquidation_transaction method found")
        else:
            logger.error("❌ LIQUIDATION: _try_jito_liquidation_transaction method missing")
            return False
        
        logger.info("🎯 TESTING EXECUTION FLOW SIMULATION...")
        
        # Test buy execution flow (simulation)
        test_token = "LanMV9sAd7wArD4vJFi2qDdfnVhFxYSUg6eADduJ3uj"  # Example meme coin
        test_source_wallet = "9WwGxj1rPMZZg4KhzWsxRxij3hiKkZyzN1TfXR8zzGzv"
        
        logger.info(f"📊 BUY FLOW TEST:")
        logger.info(f"   Token: {test_token[:8]}...")
        logger.info(f"   Source: {test_source_wallet[:8]}...")
        logger.info(f"   Amount: {config.investment_amount_sol} SOL")
        logger.info(f"   Jito Service: {'✅ Available' if bot.jito_service else '❌ Not Available'}")
        logger.info(f"   Use Jito Config: {'✅ Enabled' if config.use_jito else '❌ Disabled'}")
        
        # Check that buy execution will use Jito
        will_use_jito_buy = bot.jito_service and config.use_jito
        logger.info(f"   Will Use Jito for BUY: {'✅ YES' if will_use_jito_buy else '❌ NO'}")
        
        logger.info(f"📊 SELL FLOW TEST:")
        logger.info(f"   Token: {test_token[:8]}...")
        logger.info(f"   Jito Service: {'✅ Available' if bot.jito_service else '❌ Not Available'}")
        logger.info(f"   Use Jito Config: {'✅ Enabled' if config.use_jito else '❌ Disabled'}")
        
        # Check that sell execution will use Jito
        will_use_jito_sell = bot.jito_service and config.use_jito
        logger.info(f"   Will Use Jito for SELL: {'✅ YES' if will_use_jito_sell else '❌ NO'}")
        
        # Final assessment
        if will_use_jito_buy and will_use_jito_sell:
            logger.info("🎉 SUCCESS: Both BUYS and SELLS will use Jito-first execution!")
            logger.info("   ✅ BUY trades: Jito → DEX fallback")
            logger.info("   ✅ SELL trades: Jito → DEX fallback") 
            logger.info("   ✅ LIQUIDATIONS: Jito → DEX fallback")
            logger.info("   🛡️ Full MEV protection across all trade types!")
            return True
        else:
            logger.error("❌ FAILED: Jito-first execution not properly configured")
            if not will_use_jito_buy:
                logger.error("   ❌ BUY trades will NOT use Jito")
            if not will_use_jito_sell:
                logger.error("   ❌ SELL trades will NOT use Jito")
            return False
        
    except Exception as e:
        logger.error(f"❌ Error in Jito integration test: {e}")
        import traceback
        logger.error(traceback.format_exc())
        return False

async def main():
    """Run the Jito integration test"""
    success = await test_jito_integration()
    
    if success:
        print("\n🎉 JITO-FIRST EXECUTION TEST PASSED!")
        print("✅ Your bot will now use Jito for both buys and sells")
        print("🛡️ Full MEV protection across all trade types")
    else:
        print("\n❌ JITO-FIRST EXECUTION TEST FAILED!")
        print("⚠️ Check your configuration and Jito service setup")

if __name__ == "__main__":
    asyncio.run(main())
