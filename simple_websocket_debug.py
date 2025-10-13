#!/usr/bin/env python3
"""
Simplified WebSocket Bot - Debug Version
This will help us identify where the issue is occurring
"""

import asyncio
import json
import websockets
from env_keys import EnvKeys
from datetime import datetime
import traceback

class SimpleWebSocketBot:
    def __init__(self):
        # Load config
        kz = EnvKeys()
        self.ws_url = kz.HELIUS_Standard_Websocket_URL
        self.target_wallets = [
            "suqh5sHtr8HyJ7q8scBimULPkPpA557prMG47xCHQfK",
            "DfMxre4cKmvogbLrPigxmibVTTQDuzjdXojWzjCXXhzj",
        ]
        self.is_running = True
        self.subscription_ids = {}
        
    async def simple_trade_callback(self, trade_info):
        """Simple callback that just prints what it receives"""
        try:
            print(f"🚨 TRADE DETECTED!")
            print(f"   Wallet: {trade_info.get('wallet_address', 'Unknown')[:8]}...")
            print(f"   Action: {trade_info.get('action', 'Unknown')}")
            print(f"   Token: {trade_info.get('token_mint', 'Unknown')[:8]}...")
            print(f"   DEX: {trade_info.get('dex', 'Unknown')}")
            print(f"   Signature: {trade_info.get('signature', 'Unknown')[:12]}...")
            print("-" * 50)
        except Exception as e:
            print(f"❌ Error in trade callback: {e}")
    
    async def start_monitoring(self):
        """Start monitoring with simple error handling"""
        print(f"🚀 Starting simple WebSocket monitoring...")
        print(f"📡 Connecting to: {self.ws_url[:50]}...")
        print(f"👀 Watching {len(self.target_wallets)} wallets")
        
        retry_count = 0
        max_retries = 3
        
        while self.is_running and retry_count < max_retries:
            try:
                print(f"🔌 Connection attempt {retry_count + 1}/{max_retries}")
                
                async with websockets.connect(
                    self.ws_url,
                    ping_interval=20,
                    ping_timeout=10,
                    close_timeout=10,
                    max_size=10**7,
                ) as websocket:
                    print("✅ Connected to WebSocket!")
                    
                    # Subscribe to wallets
                    subscription_id = 1
                    for wallet in self.target_wallets:
                        print(f"📡 Subscribing to wallet: {wallet[:8]}...")
                        await self.subscribe_to_wallet(websocket, wallet, subscription_id)
                        subscription_id += 1
                    
                    print("✅ All subscriptions sent!")
                    print("👂 Listening for messages...")
                    print("=" * 60)
                    
                    # Reset retry count on successful connection
                    retry_count = 0
                    
                    # Start listening
                    await self.message_loop(websocket)
                    
            except websockets.exceptions.ConnectionClosed as e:
                retry_count += 1
                print(f"❌ WebSocket closed: {e}")
                if retry_count < max_retries:
                    print(f"🔄 Reconnecting in 3 seconds...")
                    await asyncio.sleep(3)
                    
            except Exception as e:
                retry_count += 1
                print(f"❌ WebSocket error: {e}")
                print(f"   Full error: {traceback.format_exc()}")
                if retry_count < max_retries:
                    print(f"🔄 Retrying in 3 seconds...")
                    await asyncio.sleep(3)
                    
        if retry_count >= max_retries:
            print(f"❌ Max retries reached. Stopping.")
    
    async def subscribe_to_wallet(self, websocket, wallet_address, subscription_id):
        """Subscribe to a wallet's transaction logs"""
        subscribe_message = {
            "jsonrpc": "2.0",
            "id": subscription_id,
            "method": "logsSubscribe",
            "params": [
                {"mentions": [wallet_address]},
                {"commitment": "confirmed"}
            ]
        }
        
        await websocket.send(json.dumps(subscribe_message))
        self.subscription_ids[subscription_id] = wallet_address
        print(f"   ✅ Sent subscription for {wallet_address[:8]}...")
    
    async def message_loop(self, websocket):
        """Simple message processing loop"""
        message_count = 0
        last_activity = datetime.now()
        
        try:
            while self.is_running:
                try:
                    # Wait for message with timeout
                    message = await asyncio.wait_for(websocket.recv(), timeout=3.0)
                    message_count += 1
                    current_time = datetime.now()
                    
                    try:
                        data = json.loads(message)
                        
                        # Check if this is a subscription confirmation
                        if "result" in data and "id" in data:
                            subscription_id = data["id"]
                            result = data["result"]
                            wallet = self.subscription_ids.get(subscription_id, "Unknown")
                            print(f"✅ Subscription confirmed for {wallet[:8]}... (ID: {result})")
                            continue
                        
                        # Check if this is a notification
                        if "method" in data and data["method"] == "logsNotification":
                            print(f"📨 [{message_count}] Log notification received!")
                            print(f"   ⏰ Time: {current_time.strftime('%H:%M:%S')}")
                            
                            # Extract basic info
                            params = data.get("params", {})
                            result = params.get("result", {})
                            signature = result.get("signature", "Unknown")
                            
                            print(f"   📝 Signature: {signature[:12]}...")
                            
                            # Process this as a potential trade
                            await self.process_potential_trade(result, signature)
                            
                            last_activity = current_time
                        else:
                            print(f"📨 [{message_count}] Other message: {data.get('method', 'Unknown type')}")
                            
                    except json.JSONDecodeError as e:
                        print(f"⚠️ Invalid JSON: {e}")
                        continue
                        
                except asyncio.TimeoutError:
                    # Timeout is normal - check if we should ping
                    current_time = datetime.now()
                    elapsed = (current_time - last_activity).seconds
                    
                    if elapsed > 30:
                        print(f"💓 Ping ({elapsed}s since last activity)")
                        try:
                            await websocket.ping()
                            last_activity = current_time
                        except Exception as e:
                            print(f"❌ Ping failed: {e}")
                            break
                    continue
                    
                except websockets.exceptions.ConnectionClosed:
                    print("❌ Connection closed during message loop")
                    break
                    
        except Exception as e:
            print(f"❌ Message loop error: {e}")
            print(f"   Full error: {traceback.format_exc()}")
    
    async def process_potential_trade(self, log_result, signature):
        """Simple trade processing"""
        try:
            # Just create a basic trade info structure
            trade_info = {
                "signature": signature,
                "wallet_address": "Unknown",  # We'd need to extract this
                "action": "unknown",  # We'd need to analyze this
                "token_mint": "Unknown",  # We'd need to extract this
                "dex": "Unknown",  # We'd need to detect this
                "timestamp": datetime.now()
            }
            
            # Call our simple callback
            await self.simple_trade_callback(trade_info)
            
        except Exception as e:
            print(f"❌ Error processing trade: {e}")

async def main():
    print("🤖 Simple WebSocket Copy Trading Bot")
    print("=" * 50)
    
    bot = SimpleWebSocketBot()
    
    try:
        await bot.start_monitoring()
    except KeyboardInterrupt:
        print("\n👋 Stopping bot...")
        bot.is_running = False

if __name__ == "__main__":
    asyncio.run(main())
