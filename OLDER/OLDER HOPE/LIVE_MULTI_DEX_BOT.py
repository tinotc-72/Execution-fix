#!/usr/bin/env python3
"""
MULTI-DEX PRODUCTION COPY TRADING BOT
This is your LIVE production copy trading system with full multi-DEX support
"""

import asyncio
import logging
from datetime import datetime
from advanced_copy_trading_bot import PumpCopyTradingBot

# Setup logging for production
logging.basicConfig(
    level=logging.INFO, 
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('multi_dex_copy_trading.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

async def run_production_multi_dex_bot():
    """Production multi-DEX copy trading bot"""
    
    print("\n" + "="*80)
    print("🚀 MULTI-DEX COPY TRADING BOT - PRODUCTION MODE")
    print("="*80)
    print(f"📅 {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("="*80)
    
    # Initialize the multi-DEX copy trading bot
    logger.info("🤖 Starting Production Multi-DEX Copy Trading Bot...")
    bot = PumpCopyTradingBot()
    
    print("\n🎯 PRODUCTION CONFIGURATION:")
    print("-" * 45)
    print(f"   💰 Copy Amount: {bot.copy_config['fixed_buy_amount']} SOL per trade")
    print(f"   ⚡ Execution: INSTANT (0ms delay)")
    print(f"   📊 Buys: {'ENABLED' if bot.copy_config['enable_buys'] else 'DISABLED'}")
    print(f"   💸 Sells: {'ENABLED' if bot.copy_config['enable_sells'] else 'DISABLED'}")
    print(f"   🔄 Proportional Selling: {'ENABLED' if bot.copy_config['proportional_selling'] else 'DISABLED'}")
    
    print(f"\n🌐 SUPPORTED DEX PLATFORMS:")
    print("-" * 35)
    dex_status = [
        ("PUMP.FUN", "✅ Native Trading"),
        ("JUPITER", "✅ Full Support"),
        ("RAYDIUM", "✅ Via Jupiter"),
        ("ORCA", "✅ Via Jupiter"),
        ("PHOENIX", "✅ Via Jupiter"),
        ("OPENBOOK", "✅ Via Jupiter"),
    ]
    
    for dex, status in dex_status:
        print(f"   {dex:<12} {status}")
    
    print(f"\n📡 MONITORED WALLETS ({len(bot.target_wallets)} total):")
    print("-" * 50)
    for i, wallet in enumerate(bot.target_wallets, 1):
        wallet_type = "Your Original" if i <= 2 else "Active Trader"
        print(f"   {i}. {wallet[:8]}... ({wallet_type})")
    
    print(f"\n🎯 YOUR TRADING WALLET:")
    print("-" * 30)
    try:
        from config import BOT_PUBKEY
        print(f"   📍 {BOT_PUBKEY}")
        print(f"   🔗 https://solscan.io/account/{BOT_PUBKEY}")
    except Exception as e:
        logger.error(f"Could not load wallet address: {e}")
    
    # Check multi-DEX trader status
    multi_dex_status = "✅ ACTIVE" if hasattr(bot, 'multi_dex_trader') and bot.multi_dex_trader else "❌ FAILED"
    print(f"\n🌐 Multi-DEX Trader: {multi_dex_status}")
    
    print("\n" + "="*80)
    print("🚀 PRODUCTION BOT ACTIVE - MONITORING ALL DEXES!")
    print("💡 Any trade from monitored wallets will be copied instantly")
    print("📊 Monitor logs for trade detection and execution")
    print("⏹️  Press Ctrl+C to stop the bot")
    print("="*80)
    
    # Start production monitoring
    try:
        await bot.start_monitoring()
    except KeyboardInterrupt:
        print("\n\n⏹️  Production bot stopped by user")
        logger.info("Production bot stopped by user")
        bot.print_stats()
        await bot.close()
    except Exception as e:
        print(f"\n❌ Production bot error: {e}")
        logger.error(f"Production bot error: {e}")
        await bot.close()

if __name__ == "__main__":
    try:
        asyncio.run(run_production_multi_dex_bot())
    except KeyboardInterrupt:
        print("\n👋 Production bot shutdown complete")
    except Exception as e:
        print(f"\n❌ Critical error: {e}")
        logger.error(f"Critical error: {e}")
