#!/usr/bin/env python3
"""
LIVE COPY TRADE TEST - Maximum Detection Setup
This will run your bot with the highest chance of detecting and copying a real trade
"""

import asyncio
import logging
from datetime import datetime
import signal
import sys

# Enhanced logging for maximum visibility
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('LIVE_COPY_TEST.log', mode='w')  # Fresh log file
    ]
)
logger = logging.getLogger(__name__)

# Import your bot
from advanced_copy_trading_bot import PumpCopyTradingBot

# Global bot instance for cleanup
bot_instance = None

def signal_handler(sig, frame):
    """Handle Ctrl+C gracefully"""
    print('\n\n🛑 TEST STOPPED BY USER')
    if bot_instance:
        try:
            # Print final stats
            bot_instance.print_stats()
            print('\n📋 RESULTS SUMMARY:')
            if bot_instance.stats['trades_detected'] > 0:
                print('✅ SUCCESS! Your bot detected trades!')
                print('🎯 Check the logs above for copy execution details')
            else:
                print('⏰ No trades detected during this session')
                print('🔄 Try running for longer or during peak trading hours')
        except:
            pass
    
    print('\n👋 Exiting...')
    sys.exit(0)

async def run_live_copy_test():
    """Run live copy trading test with maximum detection probability"""
    global bot_instance
    
    print("🚀 LIVE COPY TRADE TEST")
    print("=" * 60)
    print("🎯 GOAL: Detect and copy a REAL pump.fun trade")
    print("💰 Copy amount: 0.01 SOL per trade")
    print("📡 Monitoring 7 wallets (2 yours + 5 active traders)")
    print("⚡ Ultra-fast detection enabled")
    print("🔥 Will run until trade detected or stopped with Ctrl+C")
    print()
    
    # Setup signal handler for graceful exit
    signal.signal(signal.SIGINT, signal_handler)
    
    # Create bot with testing configuration
    test_config = {
        'fixed_buy_amount': 0.01,    # Your desired test amount
        'delay_seconds': 0,          # Instant execution
        'enable_sells': True,        # Copy both buys and sells
        'enable_buys': True,
        'proportional_selling': True
    }
    
    bot_instance = PumpCopyTradingBot(test_config)
    
    logger.info("🤖 LIVE COPY TRADING BOT INITIALIZED")
    logger.info(f"📊 Monitoring {len(bot_instance.target_wallets)} wallets:")
    
    for i, wallet in enumerate(bot_instance.target_wallets, 1):
        if i <= 2:
            logger.info(f"   {i}. {wallet[:8]}... (Your original wallet)")
        else:
            logger.info(f"   {i}. {wallet[:8]}... (Active test wallet)")
    
    logger.info("⚡ ULTRA-FAST DETECTION: Enabled")
    logger.info("🎯 COPY EXECUTION: Ready")
    logger.info("💰 COPY AMOUNT: 0.01 SOL per trade")
    
    print("\n🔥 STARTING LIVE MONITORING...")
    print("💡 The bot will:")
    print("   • Monitor all 7 wallets simultaneously")
    print("   • Instantly detect any pump.fun trades") 
    print("   • Execute copy trades in YOUR wallet")
    print("   • Show complete execution logs")
    print()
    print("⏰ Keep this running - pump.fun trades happen throughout the day")
    print("🎯 Press Ctrl+C when you want to stop and see results")
    print("=" * 60)
    print()
    
    start_time = datetime.now()
    
    try:
        # Start the monitoring loop
        await bot_instance.start_monitoring()
        
    except KeyboardInterrupt:
        # This should be handled by signal_handler
        pass
    except Exception as e:
        logger.error(f"❌ Error during monitoring: {e}")
        import traceback
        traceback.print_exc()
    finally:
        elapsed = datetime.now() - start_time
        print(f"\n⏱️ Test Duration: {elapsed}")
        
        # Final cleanup
        try:
            await bot_instance.close()
        except:
            pass

if __name__ == "__main__":
    print("🧪 LIVE PUMP.FUN COPY TRADING TEST")
    print("🎯 This will monitor active traders and copy their trades to YOUR wallet")
    print()
    
    # Confirm before starting
    confirm = input("✅ Ready to start live monitoring? (y/n): ").strip().lower()
    if confirm != 'y':
        print("❌ Test cancelled")
        sys.exit(0)
    
    print("\n🚀 Starting live test...")
    
    try:
        asyncio.run(run_live_copy_test())
    except KeyboardInterrupt:
        print("\n👋 Test stopped")
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
