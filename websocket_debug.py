#!/usr/bin/env python3
"""
WebSocket Debug Test - Find out what's actually happening
This will log EVERYTHING we receive from the WebSocket
"""

import asyncio
import json
import logging
import websockets
from datetime import datetime
from env_keys import EnvKeys

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('websocket_debug.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class WebSocketDebugger:
    def __init__(self):
        self.env_keys = EnvKeys()
        self.ws_url = self.env_keys.HELIUS_Standard_Websocket_URL
        self.target_wallets = [
            "suqh5sHtr8HyJ7q8scBimULPkPpA557prMG47xCHQfK",
            "DfMxre4cKmvogbLrPigxmibVTTQDuzjdXojWzjCXXhzj",
        ]
        self.message_count = 0
        self.subscription_ids = {}

    async def debug_websocket(self):
        """Debug WebSocket connection and log EVERYTHING"""
        try:
            logger.info("🚀 STARTING WEBSOCKET DEBUG")
            logger.info(f"🔗 WebSocket URL: {self.ws_url}")
            logger.info(f"🎯 Target wallets: {self.target_wallets}")
            
            # Create WebSocket connection
            headers = {
                "Content-Type": "application/json",
                "Authorization": f"Bearer {self.env_keys.HELIUS_API_KEY}"
            }
            
            async with websockets.connect(self.ws_url, extra_headers=headers) as ws:
                logger.info("✅ WebSocket connected successfully")
                
                # Subscribe to wallets
                await self._setup_debug_subscriptions(ws)
                
                # Listen for messages
                logger.info("👂 Listening for WebSocket messages...")
                message_timeout = 10.0  # 10 second timeout
                
                while True:
                    try:
                        # Wait for message
                        message = await asyncio.wait_for(ws.recv(), timeout=message_timeout)
                        self.message_count += 1
                        
                        # Log the raw message
                        logger.info(f"📨 MESSAGE #{self.message_count} RECEIVED:")
                        logger.info(f"   📄 Raw: {message}")
                        
                        # Parse and analyze
                        try:
                            data = json.loads(message)
                            await self._analyze_debug_message(data)
                        except json.JSONDecodeError as e:
                            logger.error(f"❌ JSON decode error: {e}")
                            
                    except asyncio.TimeoutError:
                        logger.info(f"⏰ No messages received in {message_timeout} seconds")
                        logger.info(f"📊 Total messages so far: {self.message_count}")
                        
                        # Show current time for reference
                        current_time = datetime.now().strftime("%H:%M:%S")
                        logger.info(f"🕐 Current time: {current_time}")
                        
        except Exception as e:
            logger.error(f"❌ WebSocket debug error: {e}")

    async def _setup_debug_subscriptions(self, ws):
        """Setup subscriptions with detailed logging"""
        for wallet in self.target_wallets:
            logger.info(f"📡 Setting up subscriptions for: {wallet[:8]}...")
            
            # Subscribe to logs with multiple commitment levels
            for commitment in ["processed", "confirmed", "finalized"]:
                logs_sub = {
                    "jsonrpc": "2.0",
                    "id": f"logs_{wallet}_{commitment}",
                    "method": "logsSubscribe",
                    "params": [
                        {"mentions": [wallet]},
                        {"commitment": commitment}
                    ]
                }
                
                logger.info(f"📡 Subscribing to logs ({commitment}) for {wallet[:8]}...")
                await ws.send(json.dumps(logs_sub))
                response = await ws.recv()
                response_data = json.loads(response)
                
                logger.info(f"📡 Subscription response: {response_data}")
                
                if "result" in response_data:
                    self.subscription_ids[f"logs_{wallet}_{commitment}"] = response_data["result"]
                    logger.info(f"✅ Subscribed to logs ({commitment}) for {wallet[:8]}... - ID: {response_data['result']}")
                else:
                    logger.error(f"❌ Failed to subscribe to logs ({commitment}) for {wallet[:8]}...")

    async def _analyze_debug_message(self, data):
        """Analyze each message in detail"""
        logger.info(f"🔍 ANALYZING MESSAGE:")
        logger.info(f"   📋 Keys: {list(data.keys())}")
        
        if "method" in data:
            logger.info(f"   🔧 Method: {data['method']}")
            
        if "params" in data:
            params = data["params"]
            logger.info(f"   📦 Params keys: {list(params.keys())}")
            
            if "result" in params:
                result = params["result"]
                logger.info(f"   📊 Result keys: {list(result.keys()) if isinstance(result, dict) else 'Not a dict'}")
                
                # Check for signatures (transactions)
                if isinstance(result, dict) and "signature" in result:
                    signature = result["signature"]
                    logger.info(f"🚨 TRANSACTION DETECTED!")
                    logger.info(f"   🔗 Signature: {signature}")
                    
                    # Check for logs
                    if "logs" in result:
                        logs = result["logs"]
                        logger.info(f"   📝 Logs count: {len(logs)}")
                        logger.info(f"   📝 First 3 logs: {logs[:3]}")
                        
                        # Look for trading keywords
                        log_text = ' '.join(logs).lower()
                        trading_keywords = ['pump', 'jupiter', 'raydium', 'orca', 'swap', 'buy', 'sell']
                        found_keywords = [kw for kw in trading_keywords if kw in log_text]
                        
                        if found_keywords:
                            logger.info(f"🎯 TRADING KEYWORDS FOUND: {found_keywords}")
                        else:
                            logger.info(f"❌ No trading keywords found in logs")

async def main():
    """Run the WebSocket debugger"""
    debugger = WebSocketDebugger()
    await debugger.debug_websocket()

if __name__ == "__main__":
    asyncio.run(main())
