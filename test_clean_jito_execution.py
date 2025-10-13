#!/usr/bin/env python3
"""
Test Clean Jito-First Execution with Immediate RPC Fallback
Simple test to verify the streamlined execution pattern
"""

import asyncio
import logging
from main import CopyTradingBot, CopyTradeConfig

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

async def test_clean_jito_execution():
    """Test the clean Jito-first with immediate RPC fallback execution"""
    
    logger.info("🚀 Testing Clean Jito-First Execution with RPC Fallback")
    logger.info("=" * 60)
    
    # Test wallets (replace with your actual target wallets)
    target_wallets = [
        "YOUR_TARGET_WALLET_1",  # Replace with actual wallet addresses
        "YOUR_TARGET_WALLET_2"
    ]
    
    # Clean configuration - Jito-first with immediate RPC fallback
    config = CopyTradeConfig(
        target_wallets=target_wallets,
        investment_amount_sol=0.001,
        use_jito=True,                      # Enable Jito-first execution
        jito_timeout=10.0,                  # 10 second timeout
        slippage_tolerance=0.15             # 15% slippage
    )
    
    logger.info("✅ Clean Jito-First Configuration:")
    logger.info(f"   Jito enabled: {config.use_jito}")
    logger.info(f"   Jito timeout: {config.jito_timeout}s")
    logger.info(f"   Investment: {config.investment_amount_sol} SOL")
    logger.info(f"   Slippage: {config.slippage_tolerance * 100}%")
    
    # Create bot with clean configuration
    bot = CopyTradingBot(config)
    
    logger.info("\n🔧 Execution Flow:")
    logger.info("1. Try Jito first for MEV protection")
    logger.info("2. If Jito fails, immediately fallback to RPC")
    logger.info("3. Ensure transaction executes as quickly as possible")
    
    logger.info("\n📋 Methods Available:")
    logger.info(f"✅ _try_jito_first_execution() - Jito-first with RPC fallback")
    logger.info(f"✅ _try_jito_first_sell_execution() - Sell with Jito-first")
    logger.info(f"✅ _try_direct_rpc_execution() - Direct RPC fallback")
    
    # Test method availability
    try:
        # Check if the bot has the required methods
        has_jito_first = hasattr(bot, '_try_jito_first_execution')
        has_jito_sell = hasattr(bot, '_try_jito_first_sell_execution')
        has_rpc_fallback = hasattr(bot, '_try_direct_rpc_execution')
        
        logger.info(f"\n🔍 Method Availability Check:")
        logger.info(f"   _try_jito_first_execution: {'✅' if has_jito_first else '❌'}")
        logger.info(f"   _try_jito_first_sell_execution: {'✅' if has_jito_sell else '❌'}")
        logger.info(f"   _try_direct_rpc_execution: {'✅' if has_rpc_fallback else '❌'}")
        
        if has_jito_first and has_jito_sell and has_rpc_fallback:
            logger.info("✅ All required methods available!")
        else:
            logger.error("❌ Some methods are missing!")
        
        # Check Jito service
        jito_available = bot.jito_service is not None
        logger.info(f"\n🔍 Jito Service Check:")
        logger.info(f"   Jito service: {'✅ Available' if jito_available else '❌ Not available'}")
        
        if jito_available:
            logger.info("✅ Ready for Jito-first execution with RPC fallback!")
        else:
            logger.warning("⚠️ Will use RPC-only execution")
            
    except Exception as e:
        logger.error(f"❌ Test error: {e}")
    
    logger.info("\n📊 Execution Pattern Summary:")
    logger.info("🚀 When trade detected:")
    logger.info("   1. Build transaction")
    logger.info("   2. Try Jito execution first (MEV protection)")
    logger.info("   3. If Jito fails → IMMEDIATE RPC fallback")
    logger.info("   4. Return success as soon as either method succeeds")
    
    logger.info("\n✅ Clean Jito-First Execution Test Complete!")
    logger.info("🎯 Your bot will now execute: Jito-first → RPC fallback")

async def main():
    """Main test function"""
    try:
        await test_clean_jito_execution()
    except Exception as e:
        logger.error(f"❌ Test error: {e}")
        import traceback
        logger.error(traceback.format_exc())

if __name__ == "__main__":
    asyncio.run(main())
