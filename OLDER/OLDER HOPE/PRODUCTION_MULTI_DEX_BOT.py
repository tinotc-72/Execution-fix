#!/usr/bin/env python3
"""
PRODUCTION MULTI-DEX COPY TRADING BOT
Live production version with support for ALL DEXes
"""

import asyncio
import logging
from datetime import datetime
from advanced_copy_trading_bot import PumpCopyTradingBot

# Setup logging for production
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('multi_dex_copy_trading.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

async def run_production_multi_dex_bot():
    """Run the production multi-DEX copy trading bot"""
    
    logger.info("🚀 STARTING PRODUCTION MULTI-DEX COPY TRADING BOT")
    logger.info("="*80)
    
    try:
        # Initialize the multi-DEX copy trading bot
        bot = PumpCopyTradingBot()
        
        logger.info("📊 PRODUCTION BOT STATUS:")
        logger.info(f"   💰 Copy Amount: {bot.copy_config['fixed_buy_amount']} SOL per trade")
        logger.info(f"   📡 Monitored Wallets: {len(bot.target_wallets)}")
        logger.info(f"   🔥 Multi-DEX Support: {'✅ ENABLED' if hasattr(bot, 'multi_dex_trader') and bot.multi_dex_trader else '❌ DISABLED'}")
        
        logger.info("\n🎯 SUPPORTED DEX PLATFORMS:")
        supported_dexes = ["PUMP.FUN", "JUPITER", "RAYDIUM", "ORCA", "PHOENIX", "OPENBOOK"]
        for dex in supported_dexes:
            logger.info(f"   ✅ {dex}")
        
        logger.info("\n📡 MONITORED WALLETS:")
        for i, wallet in enumerate(bot.target_wallets, 1):
            wallet_type = "Original" if i <= 2 else "Active Trader"
            logger.info(f"   {i}. {wallet[:8]}... ({wallet_type})")
        
        logger.info("\n⚡ STARTING LIVE MONITORING...")
        logger.info("🎯 The bot will now copy ANY trade from ANY monitored wallet on ANY supported DEX")
        logger.info("="*80)
        
        # Start the production monitoring
        await bot.start_monitoring()
        
    except KeyboardInterrupt:
        logger.info("\n⏹️  Production bot stopped by user")
        if 'bot' in locals():
            bot.print_stats()
            await bot.close()
    except Exception as e:
        logger.error(f"❌ Production bot error: {e}", exc_info=True)
        if 'bot' in locals():
            await bot.close()
        raise

if __name__ == "__main__":
    try:
        asyncio.run(run_production_multi_dex_bot())
    except KeyboardInterrupt:
        print("\n👋 Production multi-DEX bot shutdown complete")
    except Exception as e:
        print(f"\n❌ Production bot failed: {e}")
