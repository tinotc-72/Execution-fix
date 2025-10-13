#!/usr/bin/env python3
"""
WebSocket Test with Active Wallet - Test if WebSocket subscriptions work at all
"""

import asyncio
import json
import websockets
from datetime import datetime
import env_keys

class ActiveWalletTest:
    def __init__(self):
        self.env = env_keys.EnvKeys()
        # Test with a known very active wallet (Jupiter's main trading wallet)
        self.test_wallet = "D8cy77BBepLMngZx6ZukaTff5hCt1HrWyKk3Hnd9oitf"  # Jupiter DCA program
        self.subscription_id = 1000
        
    async def test_active_wallet(self):
        """Test WebSocket with a known active wallet"""
        print("🧪 TESTING WEBSOCKET WITH KNOWN ACTIVE WALLET")
        print("=" * 60)
        print(f"🎯 Test wallet: {self.test_wallet}")
        print("(This is Jupiter's DCA program - very active)")
        print("")
        
        try:
            async with websockets.connect(
                self.env.HELIUS_Standard_Websocket_URL,
                ping_interval=30,
                ping_timeout=10
            ) as websocket:
                print("✅ Connected to WebSocket")
                
                # Subscribe to logs for the test wallet
                logs_params = {
                    "jsonrpc": "2.0",
                    "id": self.subscription_id,
                    "method": "logsSubscribe",
                    "params": [
                        {"mentions": [self.test_wallet]},
                        {"commitment": "processed"}
                    ]
                }
                
                await websocket.send(json.dumps(logs_params))
                print(f"📡 Subscribed to logs for active test wallet")
                print("")
                print("🔍 Monitoring for 30 seconds...")
                print("(Should see activity if WebSocket is working)")
                print("")
                
                message_count = 0
                notifications = 0
                start_time = asyncio.get_event_loop().time()
                
                while asyncio.get_event_loop().time() - start_time < 30:
                    try:
                        message = await asyncio.wait_for(websocket.recv(), timeout=2.0)
                        message_count += 1
                        
                        data = json.loads(message)
                        
                        # Skip subscription confirmations
                        if "result" in data and isinstance(data["result"], int):
                            print(f"✅ Subscription confirmed: {data['result']}")
                            continue
                        
                        # Count actual notifications
                        if "params" in data and "result" in data["params"]:
                            method = data.get("method", "")
                            if method == "logsNotification":
                                notifications += 1
                                timestamp = datetime.now().strftime("%H:%M:%S")
                                result = data["params"]["result"]["value"]
                                signature = result.get("signature", "")
                                print(f"[{timestamp}] 📋 Activity detected: {signature[:8]}...")
                                
                    except asyncio.TimeoutError:
                        continue
                
                print("")
                print("📊 TEST RESULTS:")
                print(f"   📨 Total messages: {message_count}")
                print(f"   📋 Notifications: {notifications}")
                
                if notifications > 0:
                    print("✅ WebSocket is working correctly!")
                    print("   The issue is that your target wallets are not active")
                    print("   during monitoring periods.")
                else:
                    print("❌ WebSocket may have issues!")
                    print("   Even active wallets show no activity")
                
        except Exception as e:
            print(f"❌ Test failed: {e}")

async def main():
    test = ActiveWalletTest()
    await test.test_active_wallet()
    
    print("")
    print("🔍 NEXT STEPS:")
    print("1. If the test shows activity → Your target wallets are just inactive")
    print("2. If the test shows no activity → WebSocket/RPC endpoint issues")
    print("3. Try running your copy trading bot during your target wallet's active hours")

if __name__ == "__main__":
    asyncio.run(main())
