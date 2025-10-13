#!/usr/bin/env python3
"""
Test WebSocket Monitoring - Check if your bot is actually starting WebSocket monitoring
"""
import asyncio
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from main import CopyTradingBot, CopyTradeConfig
import logging

# Setup logging to see what's happening
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

async def test_websocket_monitoring():
    """Test if WebSocket monitoring starts properly"""
    
    print("🔍 WEBSOCKET MONITORING TEST")
    print("=" * 50)
    
    # Use the exact same configuration as your main()
    config = CopyTradeConfig(
        target_wallets=[
            "suqh5sHtr8HyJ7q8scBimULPkPpA557prMG47xCHQfK",
            "DfMxre4cKmvogbLrPigxmibVTTQDuzjdXojWzjCXXhzj",
        ],
        investment_amount_sol=0.001,
        max_positions=10,
        min_sell_threshold=0.1,
        use_jito=True,
        jito_timeout=10.0,
        enable_dexes={
            "direct_pumpfun": True,
            "pumpfun": True,
            "jupiter": True,
            "raydium": True,
            "cpmm": True,
            "clmm": True,
            "orca": True,
            "phoenix": True
        }
    )
    
    print(f"✅ Configuration created")
    print(f"   Target wallets: {len(config.target_wallets)}")
    print(f"   Wallet 1: {config.target_wallets[0][:8]}...")
    print(f"   Wallet 2: {config.target_wallets[1][:8]}...")
    print("")
    
    # Create bot
    try:
        print("🤖 Creating CopyTradingBot...")
        bot = CopyTradingBot(config)
        print("✅ Bot created successfully")
    except Exception as e:
        print(f"❌ Failed to create bot: {e}")
        return
    
    print("")
    print("🔌 Testing WebSocket connection...")
    print("   This will run for 30 seconds to see if monitoring starts")
    print("   Press Ctrl+C to stop early")
    print("")
    
    # Test WebSocket monitoring for 30 seconds
    try:
        # Start monitoring (this should start WebSocket)
        print("🚀 Starting complete monitoring system...")
        
        # Set a timeout to prevent infinite running
        # Use start_monitoring() instead of start_websocket_monitoring() directly
        # This ensures is_running is set to True properly
        monitor_task = asyncio.create_task(bot.start_monitoring())
        
        # Wait for 30 seconds or until task completes
        try:
            await asyncio.wait_for(monitor_task, timeout=30.0)
        except asyncio.TimeoutError:
            print("")
            print("⏰ 30-second test completed")
            print("🛑 Stopping monitoring...")
            
        # Clean shutdown
        await bot.stop()
        
    except KeyboardInterrupt:
        print("")
        print("⏹️ Stopped by user")
        await bot.stop()
    except Exception as e:
        print(f"❌ Error during monitoring: {e}")
        print(f"   Error type: {type(e).__name__}")
        import traceback
        print(f"   Traceback: {traceback.format_exc()}")
    
    print("")
    print("✅ Test completed")

if __name__ == "__main__":
    print("🧪 WEBSOCKET MONITORING TEST SCRIPT")
    print("This will test if your WebSocket monitoring starts correctly")
    print("=" * 60)
    
    asyncio.run(test_websocket_monitoring())
