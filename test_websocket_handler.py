#!/usr/bin/env python3
"""
Test script for the new WebSocket handler
This script tests the modular WebSocket functionality without running the full bot
"""

import asyncio
import logging
from typing import Dict, Any

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def test_trade_callback(trade_info: Dict[str, Any]):
    """Test callback function for WebSocket trade detection"""
    print(f"🎯 TEST CALLBACK RECEIVED:")
    print(f"   Detection Method: {trade_info.get('detection_method', 'Unknown')}")
    print(f"   Signature: {trade_info.get('signature', 'N/A')}")
    print(f"   Wallet: {trade_info.get('wallet_address', 'N/A')}")
    print(f"   Requires Analysis: {trade_info.get('requires_analysis', False)}")
    print(f"   Timestamp: {trade_info.get('timestamp', 'N/A')}")
    print(f"   Full Info: {trade_info}")

async def test_websocket_handler():
    """Test the WebSocket handler functionality"""
    try:
        # Import the WebSocket handler
        from websocket_handler import create_websocket_handler
        
        # Test configuration
        target_wallets = ["suqh5sHtr8HyJ7q8scBimULPkPpA557prMG47xCHQfK"]  # Example wallet
        
        # You'll need to add your actual Helius API key here
        helius_ws_url = "wss://mainnet.helius-rpc.com/?api-key=YOUR_HELIUS_KEY"
        helius_rpc_url = "https://mainnet.helius-rpc.com/?api-key=YOUR_HELIUS_KEY"
        
        print("🚀 Testing WebSocket Handler...")
        print(f"   Target Wallets: {len(target_wallets)}")
        print(f"   WebSocket URL: {helius_ws_url[:50]}...")
        
        # Create WebSocket handler
        handler = await create_websocket_handler(
            target_wallets=target_wallets,
            helius_ws_url=helius_ws_url,
            helius_rpc_url=helius_rpc_url,
            trade_callback=test_trade_callback,
            max_retries=3,  # Reduced for testing
            reconnect_delay=1.0  # Faster reconnect for testing
        )
        
        print("✅ WebSocket handler created successfully!")
        
        # Test for 30 seconds
        print("📡 Starting monitoring for 30 seconds...")
        
        try:
            await asyncio.wait_for(
                handler.start_monitoring(),
                timeout=30.0
            )
        except asyncio.TimeoutError:
            print("⏰ Test timeout reached")
        
        # Stop the handler
        await handler.stop()
        
        # Show stats
        stats = handler.get_stats()
        print(f"📊 Final Stats:")
        print(f"   Uptime: {stats['uptime_seconds']:.1f}s")
        print(f"   Messages: {stats['messages_received']}")
        print(f"   Trades: {stats['trades_detected']}")
        print(f"   Subscriptions: {stats['subscriptions']}")
        
        print("✅ WebSocket handler test completed!")
        
    except ImportError as e:
        print(f"❌ Import error: {e}")
        print("Make sure websocket_handler.py is in the same directory")
    except Exception as e:
        print(f"❌ Test error: {e}")
        import traceback
        print(f"Traceback: {traceback.format_exc()}")

if __name__ == "__main__":
    print("🧪 WebSocket Handler Test")
    print("=" * 50)
    
    # Note for the user
    print("⚠️  NOTE: You need to add your Helius API key to test this properly")
    print("    Edit this file and replace YOUR_HELIUS_KEY with your actual key")
    print("")
    
    # Run the test
    asyncio.run(test_websocket_handler())
