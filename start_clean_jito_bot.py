#!/usr/bin/env python3
"""
Start Clean Jito-First Copy Trading Bot
Simple launcher with Jito-first execution and immediate RPC fallback
"""

import asyncio
import logging
from main import CopyTradingBot, CopyTradeConfig

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

async def start_clean_jito_bot():
    """Start the clean Jito-first copy trading bot"""
    
    logger.info("🚀 Starting Clean Jito-First Copy Trading Bot")
    logger.info("=" * 50)
    
    # Configure your target wallets here
    target_wallets = [
        # Add your target wallet addresses here
        # "WALLET_ADDRESS_1",
        # "WALLET_ADDRESS_2",
    ]
    
    if not target_wallets or not target_wallets[0]:
        logger.error("❌ Please add target wallet addresses to the target_wallets list")
        return
    
    # Clean Jito-first configuration
    config = CopyTradeConfig(
        target_wallets=target_wallets,
        investment_amount_sol=0.01,      # Adjust your investment amount
        use_jito=True,                   # Jito-first execution
        jito_timeout=10.0,               # 10 second Jito timeout
        slippage_tolerance=0.15,         # 15% slippage
        max_trades_per_hour=30,          # Rate limiting
        log_level="INFO"
    )
    
    logger.info("⚙️ Bot Configuration:")
    logger.info(f"   Target wallets: {len(config.target_wallets)}")
    logger.info(f"   Investment per trade: {config.investment_amount_sol} SOL")
    logger.info(f"   Execution: Jito-first → RPC fallback")
    logger.info(f"   Jito timeout: {config.jito_timeout}s")
    logger.info(f"   Max trades/hour: {config.max_trades_per_hour}")
    
    # Create and start bot
    bot = CopyTradingBot(config)
    
    logger.info("\n🎯 Execution Strategy:")
    logger.info("1️⃣ Monitor target wallets for transactions")
    logger.info("2️⃣ When trade detected → Try Jito first (MEV protection)")
    logger.info("3️⃣ If Jito fails → IMMEDIATE RPC fallback")
    logger.info("4️⃣ Execute trade as fast as possible")
    
    try:
        logger.info("\n🏃 Starting copy trading...")
        logger.info("Press Ctrl+C to stop")
        
        # Start the bot
        await bot.start()
        
    except KeyboardInterrupt:
        logger.info("\n🛑 Stopping bot...")
        await bot.stop()
        logger.info("✅ Bot stopped successfully")
    except Exception as e:
        logger.error(f"❌ Bot error: {e}")
        import traceback
        logger.error(traceback.format_exc())

async def main():
    """Main function"""
    try:
        await start_clean_jito_bot()
    except Exception as e:
        logger.error(f"❌ Startup error: {e}")

if __name__ == "__main__":
    asyncio.run(main())
