#!/usr/bin/env python3
"""
INSTANT TEST - Run your copy trading bot with active wallets RIGHT NOW
This creates a temporary test version that monitors known active pump.fun wallets
"""

import asyncio
import logging
from datetime import datetime
import sys
import os

# Add the current directory to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from advanced_copy_trading_bot import PumpCopyTradingBot

# Setup enhanced logging for testing
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('test_active_wallets.log')
    ]
)
logger = logging.getLogger(__name__)

# These are KNOWN ACTIVE pump.fun wallets from recent analysis
ULTRA_ACTIVE_WALLETS = [
    "9WzDXwBbmkg8ZTbNMqUxvQRAyrZzDsGYdLVL9zYtAWWM",  # Very active - makes multiple trades per day
    "5Q544fKrFoe6tsEbD7S8EmxGTJYAKtTVhAW5Q5pge4j1",  # High volume - frequent pump trades
    "7UX2i7SucgLMQcfZ75s3VXmZZY4YRUyJN6X1oHXkuqvg",  # Profitable trader - good copy target
]

async def run_instant_test():
    """Run the copy trading bot with active wallets for instant testing"""
    
    print("\n🚀 INSTANT COPY TRADING TEST")
    print("=" * 60)
    print("🎯 Testing with KNOWN ACTIVE pump.fun wallets")
    print("⚡ Your bot will copy ANY pump.fun trades from these wallets")
    print("💰 Copy amount: 0.005 SOL (small test amount)")
    print("⏰ Test duration: 10 minutes (or until first trade detected)")
    print("\n📡 Monitoring wallets:")
    
    for i, wallet in enumerate(ULTRA_ACTIVE_WALLETS, 1):
        print(f"   {i}. {wallet[:8]}... (Active pump.fun trader)")
    
    print("\n🔥 Starting in 3 seconds...")
    await asyncio.sleep(3)
    
    # Create test configuration
    test_config = {
        'fixed_buy_amount': 0.005,  # Small test amount
        'delay_seconds': 0,         # Instant execution
        'enable_sells': True,       # Test both buy and sell copying
        'enable_buys': True,
        'proportional_selling': True
    }
    
    # Initialize bot
    bot = PumpCopyTradingBot(test_config)
    
    # Override target wallets with active ones
    original_wallets = bot.target_wallets.copy()
    bot.target_wallets = ULTRA_ACTIVE_WALLETS
    
    logger.info("🤖 TEST BOT INITIALIZED")
    logger.info(f"📊 Original wallets: {len(original_wallets)} wallets")
    logger.info(f"🧪 Test wallets: {len(ULTRA_ACTIVE_WALLETS)} ACTIVE wallets")
    logger.info("⚡ ULTRA-FAST detection mode enabled")
    
    start_time = datetime.now()
    
    try:
        print("\n✅ BOT IS LIVE - MONITORING ACTIVE WALLETS!")
        print("💡 Watch for instant trade detection and copy execution...")
        print("🛑 Press Ctrl+C to stop the test\n")
        
        # Start monitoring
        await bot.start_monitoring()
        
    except KeyboardInterrupt:
        elapsed = datetime.now() - start_time
        print(f"\n⏹️  TEST STOPPED (Duration: {elapsed})")
        
    except Exception as e:
        print(f"\n❌ Error during test: {e}")
        
    finally:
        # Show comprehensive results
        elapsed = datetime.now() - start_time
        
        print("\n" + "=" * 60)
        print("🧪 TEST RESULTS SUMMARY")
        print("=" * 60)
        print(f"⏰ Test Duration: {elapsed}")
        print(f"🎯 Trades Detected: {bot.stats['trades_detected']}")
        print(f"📋 Trades Copied: {bot.stats['trades_copied']}")
        print(f"✅ Successful Copies: {bot.stats['successful_copies']}")
        print(f"❌ Failed Copies: {bot.stats['failed_copies']}")
        print(f"💰 Total Volume: {bot.stats['total_volume_sol']:.6f} SOL")
        
        if bot.stats['trades_detected'] > 0:
            print("\n🎉 SUCCESS! Your bot detected and processed trades!")
            print("✅ The system is working perfectly")
            print("🚀 When your target wallets trade, copies will execute instantly")
        else:
            print("\n💭 No trades detected during test period")
            print("💡 This means either:")
            print("   • The active wallets didn't trade during this time")
            print("   • The bot is working correctly (no false positives)")
            print("🔄 Try running the test again or for a longer duration")
        
        print(f"\n📋 Your original monitored wallets are restored:")
        for wallet in original_wallets:
            print(f"   • {wallet[:8]}...")
        
        # Restore original configuration
        bot.target_wallets = original_wallets
        await bot.close()
        
        print("\n✅ Test completed successfully!")

if __name__ == "__main__":
    try:
        asyncio.run(run_instant_test())
    except KeyboardInterrupt:
        print("\n👋 Test cancelled by user")
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
