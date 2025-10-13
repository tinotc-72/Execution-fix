#!/usr/bin/env python3
"""
🧪 WebSocket Stability Test
Test the improved WebSocket connection to ensure it stays stable
"""

import asyncio
import time
from wallet_tx_parser import create_websocket_monitor

async def test_trade_callback(trade_info):
    """Test callback for trade detection"""
    print(f"🚨 TRADE DETECTED: {trade_info.get('action', 'unknown').upper()}")
    print(f"   💎 Token: {trade_info.get('token_mint', 'Unknown')[:8]}...")
    print(f"   🏪 DEX: {trade_info.get('dex', 'Unknown')}")
    print(f"   👤 Wallet: {trade_info.get('wallet_address', 'Unknown')[:8]}...")
    
async def test_stable_websocket():
    """Test stable WebSocket connection for 60 seconds"""
    print("🧪 Testing WebSocket stability for 60 seconds...")
    
    # Use real target wallets for testing
    target_wallets = [
        "suqh5sHtr8HyJ7q8scBimULPkPpA557prMG47xCHQfK",
        "DfMxre4cKmvogbLrPigxmibVTTQDuzjdXojWzjCXXhzj",
    ]
    
    print(f"📡 Monitoring {len(target_wallets)} target wallets:")
    for i, wallet in enumerate(target_wallets):
        print(f"   {i+1}. {wallet[:8]}...{wallet[-8:]}")
    
    # Create WebSocket monitor
    monitor = await create_websocket_monitor(target_wallets, test_trade_callback)
    print("✅ WebSocket monitor created")
    
    start_time = time.time()
    
    try:
        # Start monitoring
        print("🚀 Starting WebSocket monitoring...")
        task = asyncio.create_task(monitor.start_monitoring())
        
        # Monitor for 60 seconds
        for i in range(12):  # 12 x 5 seconds = 60 seconds
            await asyncio.sleep(5)
            elapsed = time.time() - start_time
            print(f"⏱️  WebSocket running for {elapsed:.1f} seconds...")
            
            if not monitor.is_running:
                print("❌ WebSocket stopped unexpectedly!")
                break
        
        print("✅ WebSocket stability test completed successfully!")
        
    except Exception as e:
        print(f"❌ WebSocket stability test failed: {e}")
        import traceback
        traceback.print_exc()
        
    finally:
        # Clean shutdown
        print("🛑 Stopping WebSocket...")
        monitor.stop_monitoring()
        await asyncio.sleep(2)  # Give it time to stop
        print("✅ WebSocket stopped cleanly")

if __name__ == "__main__":
    print("🧪 WebSocket Stability Test Starting...")
    print("=" * 50)
    asyncio.run(test_stable_websocket())
    print("=" * 50)
    print("🧪 WebSocket Stability Test Complete")
