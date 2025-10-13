#!/usr/bin/env python3
"""
Test WebSocket monitoring with official Solana API
"""

import asyncio
import json
from wallet_tx_parser import create_websocket_monitor

async def test_trade_handler(trade_info):
    """Test callback for detected trades"""
    print(f"🚨 TRADE DETECTED!")
    print(f"   👤 Wallet: {trade_info['wallet_address'][:8]}...")
    print(f"   🎬 Action: {trade_info['action'].upper()}")
    print(f"   💎 Token: {trade_info.get('token_mint', 'Unknown')[:8]}...")
    print(f"   🏪 DEX: {trade_info.get('dex', 'Unknown')}")
    print(f"   📝 Signature: {trade_info['signature'][:12]}...")
    print("=" * 50)

async def main():
    """Test the WebSocket monitoring with your target wallets"""
    target_wallets = [
        "suqh5sHtr8HyJ7q8scBimULPkPpA557prMG47xCHQfK",  # Your target wallet 1
        "DfMxre4cKmvogbLrPigxmibVTTQDuzjdXojWzjCXXhzj"   # Your target wallet 2
    ]
    
    print("🔍 Testing WebSocket monitoring with official Solana API...")
    print(f"🎯 Monitoring {len(target_wallets)} wallets:")
    for i, wallet in enumerate(target_wallets, 1):
        print(f"   {i}. {wallet[:8]}...{wallet[-8:]}")
    print("=" * 60)
    
    # Create WebSocket monitor
    monitor = await create_websocket_monitor(target_wallets, test_trade_handler)
    
    try:
        print("🚀 Starting WebSocket monitoring...")
        await monitor.start_monitoring()
    except KeyboardInterrupt:
        print("\n⏹️ Stopping WebSocket monitoring...")
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
    finally:
        monitor.stop_monitoring()
        print("✅ WebSocket monitoring stopped")

if __name__ == "__main__":
    asyncio.run(main())
