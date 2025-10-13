#!/usr/bin/env python3
"""Quick WebSocket Test - Check if monitoring actually works"""

import asyncio
import logging
from datetime import datetime

# Configure logging to see WebSocket activity
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

async def test_websocket_monitoring():
    """Test if WebSocket monitoring actually detects trades"""
    print("🔍 TESTING WEBSOCKET MONITORING...")
    print("=" * 50)
    
    try:
        from wallet_tx_parser import create_websocket_monitor
        
        # Target wallets (your actual ones)
        target_wallets = [
            "suqh5sHtr8HyJ7q8scBimULPkPpA557prMG47xCHQfK",
            "DfMxre4cKmvogbLrPigxmibVTTQDuzjdXojWzjCXXhzj",
        ]
        
        # Test callback that prints everything
        def test_callback(trade_info):
            print(f"🚨 TRADE DETECTED!")
            print(f"   Time: {datetime.now()}")
            print(f"   Data: {trade_info}")
            print("-" * 30)
        
        print(f"📡 Creating WebSocket monitor for {len(target_wallets)} wallets...")
        monitor = await create_websocket_monitor(target_wallets, test_callback)
        
        print(f"✅ Monitor created, starting monitoring...")
        print(f"⏰ Will monitor for 30 seconds...")
        print(f"🎯 Watching wallets:")
        for wallet in target_wallets:
            print(f"   - {wallet}")
        
        # Start monitoring for 30 seconds
        monitoring_task = asyncio.create_task(monitor.start_monitoring())
        
        # Wait 30 seconds
        await asyncio.sleep(30)
        
        print(f"⏹️ Stopping monitor...")
        monitor.stop_monitoring()
        
        print(f"✅ Test completed")
        print(f"💡 If you saw any 'TRADE DETECTED' messages, WebSocket is working")
        print(f"💡 If no messages, either:")
        print(f"   1. No trades happened in the last 30 seconds")
        print(f"   2. WebSocket connection failed")
        print(f"   3. Trade detection logic has issues")
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        print(f"Traceback: {traceback.format_exc()}")

if __name__ == "__main__":
    asyncio.run(test_websocket_monitoring())
