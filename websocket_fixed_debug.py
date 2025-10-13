#!/usr/bin/env python3
"""
Fixed WebSocket Debug Script - Using accountSubscribe instead of logsSubscribe
"""

import asyncio
import json
import logging
import websockets
from datetime import datetime
from env_keys import EnvKeys

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class FixedWebSocketDebugger:
    def __init__(self):
        self.env_keys = EnvKeys()
        self.helius_api_key = self.env_keys.HELIUS_API_KEY
        self.websocket_url = f"wss://mainnet.helius-rpc.com/v0?api-key={self.helius_api_key}"
        self.target_wallets = [
            "suqh5sHtr8HyJ7q8scBimULPkPpA557prMG47xCHQfK",
            "DfMxre4cKmvogbLrPigxmibVTTQDuzjdXojWzjCXXhzj"
        ]
        self.message_count = 0
        self.subscription_ids = {}

    async def debug_websocket(self):
        logger.info("🚀 STARTING FIXED WEBSOCKET DEBUG")
        logger.info(f"🔗 WebSocket URL: {self.websocket_url}")
        logger.info(f"🎯 Target wallets: {self.target_wallets}")
        
        try:
            async with websockets.connect(self.websocket_url) as ws:
                logger.info("✅ WebSocket connected successfully")
                
                # Subscribe to account changes for each wallet
                for wallet in self.target_wallets:
                    await self.setup_account_subscriptions(ws, wallet)
                
                logger.info("👂 Listening for WebSocket messages...")
                message_timeout = 10.0
                
                while True:
                    try:
                        message = await asyncio.wait_for(ws.recv(), timeout=message_timeout)
                        await self.process_message(message)
                        
                    except asyncio.TimeoutError:
                        logger.info(f"⏰ No messages received in {message_timeout} seconds")
                        logger.info(f"📊 Total messages so far: {self.message_count}")
                        logger.info(f"🕐 Current time: {datetime.now().strftime('%H:%M:%S')}")
                        continue
                        
        except Exception as e:
            logger.error(f"❌ WebSocket error: {e}")
            
    async def setup_account_subscriptions(self, ws, wallet):
        logger.info(f"📡 Setting up account subscriptions for: {wallet[:8]}...")
        
        # Subscribe to account changes with different commitment levels
        for commitment in ["processed", "confirmed"]:
            account_sub = {
                "jsonrpc": "2.0",
                "id": f"account_{wallet}_{commitment}",
                "method": "accountSubscribe",
                "params": [
                    wallet,
                    {
                        "commitment": commitment,
                        "encoding": "base64"
                    }
                ]
            }
            
            logger.info(f"📡 Subscribing to account changes ({commitment}) for {wallet[:8]}...")
            await ws.send(json.dumps(account_sub))
            response = await ws.recv()
            response_data = json.loads(response)
            
            logger.info(f"📡 Account subscription response: {response_data}")
            
            if "result" in response_data:
                sub_id = response_data["result"]
                self.subscription_ids[sub_id] = {
                    "wallet": wallet,
                    "type": "account",
                    "commitment": commitment
                }
                logger.info(f"✅ Subscribed to account changes ({commitment}) for {wallet[:8]} - ID: {sub_id}")
        
        # ALSO subscribe to signature notifications for this wallet
        signature_sub = {
            "jsonrpc": "2.0",
            "id": f"signature_{wallet}",
            "method": "signatureSubscribe",
            "params": [
                wallet,
                {"commitment": "processed"}
            ]
        }
        
        logger.info(f"📡 Subscribing to signatures for {wallet[:8]}...")
        await ws.send(json.dumps(signature_sub))
        response = await ws.recv()
        response_data = json.loads(response)
        
        logger.info(f"📡 Signature subscription response: {response_data}")

    async def process_message(self, message_str):
        self.message_count += 1
        logger.info(f"📨 MESSAGE #{self.message_count} RECEIVED:")
        
        try:
            message = json.loads(message_str)
            logger.info(f"   📄 Raw: {message_str[:500]}{'...' if len(message_str) > 500 else ''}")
            
            # Analyze message structure
            logger.info("🔍 ANALYZING MESSAGE:")
            logger.info(f"   📋 Keys: {list(message.keys())}")
            
            if "method" in message:
                logger.info(f"   🔧 Method: {message['method']}")
                
                if "params" in message:
                    params = message["params"]
                    logger.info(f"   📦 Params keys: {list(params.keys())}")
                    
                    # Check subscription ID to identify which wallet
                    if "subscription" in params:
                        sub_id = params["subscription"]
                        if sub_id in self.subscription_ids:
                            sub_info = self.subscription_ids[sub_id]
                            logger.info(f"   🎯 WALLET ACTIVITY DETECTED: {sub_info['wallet'][:8]} ({sub_info['type']}, {sub_info['commitment']})")
                        
                        if "result" in params:
                            result = params["result"]
                            logger.info(f"   📊 Result keys: {list(result.keys())}")
                            
                            # Look for account changes (balance changes indicate transactions)
                            if "value" in result:
                                value = result["value"]
                                if isinstance(value, dict):
                                    logger.info(f"   💰 Account data changed - this indicates a transaction!")
                                    if "lamports" in value:
                                        logger.info(f"   🔥 SOL BALANCE CHANGE: {value['lamports']} lamports")
                                    
                                    # This is likely a real transaction by our target wallet
                                    logger.info("   🚨 POTENTIAL TARGET WALLET TRANSACTION DETECTED!")
                            
            elif "result" in message:
                # This is a subscription confirmation
                logger.info("   ✅ Subscription confirmation received")
                
        except json.JSONDecodeError as e:
            logger.error(f"❌ Failed to parse message: {e}")
        except Exception as e:
            logger.error(f"❌ Error processing message: {e}")

async def main():
    debugger = FixedWebSocketDebugger()
    await debugger.debug_websocket()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("👋 Debug session ended by user")
