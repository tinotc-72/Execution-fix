#!/usr/bin/env python3
"""
Copy Trading Launcher
Simple script to start the copy trading bot with the proven pump.fun trading system
"""

import asyncio
import sys
from advanced_copy_trading_bot import PumpCopyTradingBot

def print_banner():
    """Print startup banner"""
    print("""
╔═══════════════════════════════════════════════════════════════╗
║                    🚀 PUMP.FUN COPY TRADING BOT 🚀            ║
║                                                               ║
║  🎯 Monitors target wallets for pump.fun trades              ║
║  ⚡ Uses proven direct trading system                         ║
║  💰 Automatically copies buy/sell trades                     ║
║  📊 Real-time performance tracking                           ║
║                                                               ║
╚═══════════════════════════════════════════════════════════════╝
""")

async def run_copy_trading():
    """Main copy trading function"""
    
    print_banner()
    
    # Trading configuration - adjust these based on your risk tolerance
    copy_config = {
        'copy_percentage': 0.1,     # Copy 10% of target trade size
        'min_copy_amount': 0.002,   # Minimum 0.002 SOL per trade
        'max_copy_amount': 0.05,    # Maximum 0.05 SOL per trade
        'delay_seconds': 0,         # No delay - execute immediately
        'enable_sells': True,       # Copy sell trades
        'enable_buys': True         # Copy buy trades
    }
    
    print("⚙️  Configuration:")
    print(f"   • Copy Percentage: {copy_config['copy_percentage']*100}%")
    print(f"   • Min Trade: {copy_config['min_copy_amount']} SOL")
    print(f"   • Max Trade: {copy_config['max_copy_amount']} SOL")
    print(f"   • Delay: {copy_config['delay_seconds']} seconds")
    print(f"   • Buy Copying: {'✅' if copy_config['enable_buys'] else '❌'}")
    print(f"   • Sell Copying: {'✅' if copy_config['enable_sells'] else '❌'}")
    print()
    
    # Initialize copy trading bot
    bot = PumpCopyTradingBot(copy_config)
    
    try:
        print("🚀 Starting copy trading system...")
        print("🎯 Monitoring target wallets for pump.fun trades...")
        print("💡 Press Ctrl+C to stop\n")
        
        # Start the copy trading bot
        await bot.start_monitoring()
        
    except KeyboardInterrupt:
        print("\n👋 Shutting down copy trading bot...")
    except Exception as e:
        print(f"\n❌ Error: {e}")
        return 1
    finally:
        await bot.close()
        print("✅ Copy trading bot stopped")
    
    return 0

if __name__ == "__main__":
    try:
        exit_code = asyncio.run(run_copy_trading())
        sys.exit(exit_code)
    except KeyboardInterrupt:
        print("\n👋 Goodbye!")
        sys.exit(0)
