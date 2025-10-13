#!/usr/bin/env python3
"""
Simple WebSocket connection test
"""

import asyncio
import websockets
import json
from env_keys import EnvKeys

async def test_websocket_connection():
    """Test basic WebSocket connection to Helius"""
    keys = EnvKeys()
    ws_url = keys.HELIUS_Standard_Websocket_URL
    print(f"🔗 Testing WebSocket connection to: {ws_url}")
    
    try:
        async with websockets.connect(ws_url) as websocket:
            print("✅ WebSocket connected successfully!")
            
            # Test subscription to one wallet
            test_wallet = "suqh5sHtr8HyJ7q8scBimULPkPpA557prMG47xCHQfK"
            
            subscribe_message = {
                "jsonrpc": "2.0",
                "id": 1,
                "method": "logsSubscribe",
                "params": [
                    {
                        "mentions": [test_wallet]
                    },
                    {
                        "commitment": "confirmed"
                    }
                ]
            }
            
            print(f"📡 Subscribing to wallet: {test_wallet[:8]}...")
            await websocket.send(json.dumps(subscribe_message))
            
            # Wait for subscription confirmation
            print("⏳ Waiting for subscription confirmation...")
            message = await asyncio.wait_for(websocket.recv(), timeout=10.0)
            response = json.loads(message)
            
            print(f"📥 Received: {response}")
            
            if "result" in response:
                print("✅ Subscription confirmed!")
                print("🎧 Listening for messages (press Ctrl+C to stop)...")
                
                # Listen for 30 seconds
                timeout = 30
                start_time = asyncio.get_event_loop().time()
                
                while asyncio.get_event_loop().time() - start_time < timeout:
                    try:
                        message = await asyncio.wait_for(websocket.recv(), timeout=5.0)
                        data = json.loads(message)
                        print(f"📨 Message: {data.get('method', 'unknown')} - {len(str(data))} chars")
                    except asyncio.TimeoutError:
                        print("⏰ Timeout (normal) - still listening...")
                        continue
                        
                print(f"✅ Test completed - listened for {timeout} seconds")
                
            else:
                print(f"❌ Subscription failed: {response}")
                
    except Exception as e:
        print(f"❌ WebSocket connection failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_websocket_connection())
