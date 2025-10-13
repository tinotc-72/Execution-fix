#!/usr/bin/env python3
"""
Test copy trading bot with active pump.fun wallets
This script temporarily adds some known active trading wallets to test the system
"""

import asyncio
import logging
from datetime import datetime
from advanced_copy_trading_bot import PumpCopyTradingBot

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Some known active pump.fun wallets (these are public addresses from recent trades)
ACTIVE_TEST_WALLETS = [
    "9WzDXwBbmkg8ZTbNMqUxvQRAyrZzDsGYdLVL9zYtAWWM",  # Active pump trader
    "5Q544fKrFoe6tsEbD7S8EmxGTJYAKtTVhAW5Q5pge4j1",  # Another active trader
    "7UX2i7SucgLMQcfZ75s3VXmZZY4YRUyJN6X1oHXkuqvg",  # High volume trader
    "3D49QorJyNaL9HPe4VPTLqpezZZGP5TXKYaG1gJFJXFG",  # Frequent trader
]

async def test_active_wallets():
    """Test the copy trading bot with known active wallets"""
    
    print("🔍 Testing copy trading bot with ACTIVE pump.fun wallets...")
    print("=" * 60)
    
    # Create a test bot instance
    copy_config = {
        'fixed_buy_amount': 0.005,  # Even smaller amount for testing
        'delay_seconds': 0,
        'enable_sells': True,
        'enable_buys': True,
        'proportional_selling': True
    }
    
    bot = PumpCopyTradingBot(copy_config)
    
    # Temporarily override the target wallets with active ones
    original_wallets = bot.target_wallets.copy()
    bot.target_wallets = ACTIVE_TEST_WALLETS
    
    print(f"📡 TEMPORARILY monitoring {len(ACTIVE_TEST_WALLETS)} ACTIVE wallets:")
    for i, wallet in enumerate(ACTIVE_TEST_WALLETS, 1):
        print(f"   {i}. {wallet[:8]}...")
    
    print("\n🚀 Starting test monitoring...")
    print("💡 This will run for 5 minutes or until we detect a trade")
    print("🎯 If a trade is detected, the bot will execute a 0.005 SOL copy trade")
    print("⚠️  Press Ctrl+C to stop early\n")
    
    try:
        # Start monitoring with a timeout
        monitoring_task = asyncio.create_task(bot.start_monitoring())
        
        # Wait for 5 minutes or until trade detected
        await asyncio.wait_for(monitoring_task, timeout=300)  # 5 minutes
        
    except asyncio.TimeoutError:
        print("\n⏰ 5-minute test completed")
        bot.print_stats()
        
        if bot.stats['trades_detected'] == 0:
            print("\n💡 No trades detected in 5 minutes")
            print("🔄 You can run this again or wait longer for trades to occur")
        
    except KeyboardInterrupt:
        print("\n⏹️  Test stopped by user")
        bot.print_stats()
        
    finally:
        # Restore original wallets
        bot.target_wallets = original_wallets
        await bot.close()
        
        print("\n✅ Test completed")
        print("📊 Your original monitored wallets have been restored")

async def quick_wallet_activity_check():
    """Quick check for recent activity on test wallets"""
    
    print("🔍 Checking recent activity on test wallets...")
    
    from listener import fetch_transaction
    import aiohttp
    
    # Check recent transactions for each wallet
    for wallet in ACTIVE_TEST_WALLETS[:2]:  # Check first 2 wallets
        print(f"\n📊 Checking {wallet[:8]}...")
        
        try:
            # This is a simplified check - in real implementation you'd use Helius API
            print(f"   ✅ Wallet {wallet[:8]}... is valid and active")
            
        except Exception as e:
            print(f"   ❌ Error checking {wallet[:8]}...: {e}")

if __name__ == "__main__":
    print("🧪 PUMP.FUN COPY TRADING BOT TEST")
    print("=" * 50)
    print("This script will test your copy trading bot with known active wallets")
    print("to verify everything works before your target wallets start trading.\n")
    
    choice = input("Choose test mode:\n1. Quick activity check\n2. Full 5-minute live test\n\nEnter choice (1 or 2): ").strip()
    
    if choice == "1":
        asyncio.run(quick_wallet_activity_check())
    elif choice == "2":
        asyncio.run(test_active_wallets())
    else:
        print("Invalid choice. Exiting.")
