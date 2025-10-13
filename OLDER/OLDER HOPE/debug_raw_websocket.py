#!/usr/bin/env python3
"""
Simple debug: Check if we're receiving any WebSocket messages at all
"""

import asyncio
import json
import logging
import websockets
from env_keys import EnvKeys

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(message)s')
logger = logging.getLogger(__name__)

async def debug_raw_websocket():
    """Debug raw WebSocket connection to see if we receive ANY messages"""
    
    print("\n" + "="*80)
    print("🔍 RAW WEBSOCKET DEBUG")
    print("="*80)
    print("🎯 Testing raw connection to Helius WebSocket")
    print("📊 This will show if we're receiving ANY messages at all")
    print("="*80)
    
    # Your wallet addresses
    target_wallets = [
        'suqh5sHtr8HyJ7q8scBimULPkPpA557prMG47xCHQfK',
        'DfMxre4cKmvogbLrPigxmibVTTQDuzjdXojWzjCXXhzj'
    ]
    
    helius_ws_url = EnvKeys().HELIUS_Standard_Websocket_URL
    print(f"🔗 WebSocket URL: {helius_ws_url[:50]}...")
    
    message_count = 0
    
    try:
        print(f"\n🔄 Connecting to WebSocket...")
        async with websockets.connect(helius_ws_url) as ws:
            print(f"✅ Connected!")
            
            # Subscribe to your wallets
            for i, wallet in enumerate(target_wallets, 1):
                subscription = {
                    "jsonrpc": "2.0",
                    "id": i,
                    "method": "logsSubscribe",
                    "params": [
                        {"mentions": [wallet]},
                        {"commitment": "confirmed"}  # Faster than "finalized"
                    ]
                }
                await ws.send(json.dumps(subscription))
                print(f"📡 Subscribed to wallet {i}: {wallet[:8]}...")
            
            print(f"\n🎯 WAITING FOR MESSAGES...")
            print(f"💡 Make a trade from one of your wallets to test")
            print(f"🛑 Press Ctrl+C to stop")
            print("-" * 80)
            
            # Listen for messages
            while True:
                try:
                    msg = await asyncio.wait_for(ws.recv(), timeout=10.0)
                    message_count += 1
                    
                    print(f"\n🔥 MESSAGE #{message_count} at {asyncio.get_event_loop().time():.1f}")
                    
                    try:
                        data = json.loads(msg)
                        
                        # Check if it's a subscription confirmation
                        if 'result' in data and isinstance(data['result'], int):
                            print(f"   ✅ Subscription confirmed: ID {data['result']}")
                            continue
                        
                        # Check if it's a logs notification
                        if 'method' in data and data['method'] == 'logsNotification':
                            params = data.get('params', {})
                            result = params.get('result', {})
                            value = result.get('value', {})
                            
                            signature = value.get('signature', 'Unknown')
                            logs = value.get('logs', [])
                            
                            print(f"   📋 Transaction: {signature[:16]}...")
                            print(f"   📊 Logs: {len(logs)} entries")
                            
                            # Check for pump activity
                            pump_activity = False
                            for i, log in enumerate(logs[:10]):  # Show first 10 logs
                                print(f"      {i+1:2d}: {log}")
                                if any(pattern in log for pattern in [
                                    'BSfD6SHZigAfDWSjzD5Q41jw8LmKwtmjskPH9XW1mrRW',
                                    'pAMMBay6oceH9fJKBRHGP5D4bD4sWpmSwMn52FMfXEA',
                                    'PumpAmmSwap',
                                    'Instruction: Buy',
                                    'Instruction: Sell'
                                ]):
                                    print(f"         🎯 PUMP ACTIVITY!")
                                    pump_activity = True
                            
                            if len(logs) > 10:
                                print(f"      ... and {len(logs)-10} more logs")
                            
                            if pump_activity:
                                print(f"   🚀 POTENTIAL TRADE DETECTED!")
                            else:
                                print(f"   ℹ️  No pump activity in this transaction")
                        else:
                            print(f"   📄 Other message type: {data.get('method', 'unknown')}")
                    
                    except json.JSONDecodeError:
                        print(f"   ❌ Invalid JSON: {msg[:100]}...")
                    
                    print("-" * 50)
                    
                except asyncio.TimeoutError:
                    print(f"⏳ No messages in 10 seconds... (connection alive)")
                except websockets.exceptions.ConnectionClosed:
                    print(f"❌ WebSocket connection closed")
                    break
                    
    except KeyboardInterrupt:
        print(f"\n\n⏹️  Debug stopped by user")
        print(f"📊 Total messages received: {message_count}")
    except Exception as e:
        print(f"\n❌ Connection error: {e}")
        print(f"📊 Messages received before error: {message_count}")

if __name__ == "__main__":
    asyncio.run(debug_raw_websocket())
