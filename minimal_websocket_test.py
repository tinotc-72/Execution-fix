#!/usr/bin/env python3

import asyncio
import json
import logging
import time
import websockets
from env_keys import EnvKeys
from config import CopyTradeConfig

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class MinimalWebSocketBot:
    def __init__(self, config):
        self.config = config
        self.env_keys = EnvKeys()
        self.ws_url = self.env_keys.HELIUS_Standard_Websocket_URL
        self.target_wallets = config.target_wallets
        self.subscription_ids = {}
        self.is_running = True
        
        logger.info(f"Minimal bot initialized with {len(self.target_wallets)} wallets")
        
    async def start_monitoring(self):
        """Start minimal WebSocket monitoring"""
        try:
            logger.info("Starting minimal WebSocket monitoring...")
            
            headers = {
                "Content-Type": "application/json",
                "Authorization": f"Bearer {self.env_keys.HELIUS_API_KEY}"
            }
            
            logger.info(f"Connecting to: {self.ws_url}")
            
            ws_connection = await asyncio.wait_for(
                websockets.connect(self.ws_url, additional_headers=headers),
                timeout=10.0
            )
            
            async with ws_connection as ws:
                logger.info("✅ WebSocket connected!")
                
                # Setup subscriptions
                logger.info("Setting up subscriptions...")
                await self._setup_subscriptions(ws)
                logger.info("✅ Subscriptions completed!")
                
                # Listen for 3 minutes then exit
                logger.info("Listening for 3 minutes...")
                start_time = time.time()
                message_count = 0
                
                while time.time() - start_time < 180:  # 3 minutes to see full message structure
                    try:
                        message = await asyncio.wait_for(ws.recv(), timeout=2.0)
                        data = json.loads(message)
                        message_count += 1
                        
                        method = data.get('method', 'unknown')
                        if method == "logsNotification":
                            logger.info(f"🚀 INSTANT LOGS NOTIFICATION RECEIVED!")
                            
                            # Print the full message structure to debug
                            logger.info(f"🔍 FULL MESSAGE: {data}")
                            
                            params = data.get("params", {})
                            result = params.get("result", {})
                            subscription = params.get("subscription")
                            signature = result.get("signature", "unknown")
                            logs = result.get("logs", [])
                            
                            logger.info(f"🚀 REAL-TIME TRADE: {signature[:8] if signature != 'unknown' else signature}... with {len(logs)} logs")
                            logger.info(f"📋 Subscription ID: {subscription}")
                            
                            # Show some log content for analysis
                            if logs and len(logs) > 0:
                                log_sample = ' '.join(logs[:3])[:300] + "..." if len(' '.join(logs)) > 300 else ' '.join(logs)
                                logger.info(f"📋 Log sample: {log_sample}")
                            else:
                                logger.warning(f"⚠️ No logs in this notification!")
                        else:
                            logger.info(f"[{message_count}] Received: {method}")
                        
                    except asyncio.TimeoutError:
                        continue
                    except Exception as e:
                        logger.error(f"Message error: {e}")
                        break
                
                logger.info(f"Test complete! Received {message_count} messages")
                
        except Exception as e:
            logger.error(f"Error: {e}")
            import traceback
            logger.error(traceback.format_exc())
    
    async def _setup_subscriptions(self, ws):
        """Setup subscriptions for all target wallets"""
        logger.info(f"Setting up subscriptions for {len(self.target_wallets)} wallets")
        
        if not self.target_wallets:
            logger.error("❌ No target wallets!")
            return
        
        successful_subs = 0
        
        for wallet_idx, wallet in enumerate(self.target_wallets):
            logger.info(f"[{wallet_idx+1}/{len(self.target_wallets)}] Setting up subscription for: {wallet[:8]}...")
            
            try:
                logs_sub = {
                    "jsonrpc": "2.0",
                    "id": f"logs_{wallet}_{int(time.time())}",
                    "method": "logsSubscribe",
                    "params": [
                        {
                            "mentions": [wallet]
                        },
                        {
                            "commitment": "processed"
                        }
                    ]
                }
                
                logger.info(f"Sending subscription for {wallet[:8]}...")
                await ws.send(json.dumps(logs_sub))
                
                logger.info(f"Waiting for response...")
                response = await asyncio.wait_for(ws.recv(), timeout=10.0)
                response_data = json.loads(response)
                
                logger.info(f"Response: {response_data}")
                
                if "result" in response_data:
                    sub_id = response_data["result"]
                    self.subscription_ids[f"logs_{wallet}"] = sub_id
                    successful_subs += 1
                    logger.info(f"✅ Subscription successful (ID: {sub_id})")
                else:
                    logger.error(f"❌ Subscription failed: {response_data}")
                    
            except Exception as e:
                logger.error(f"Error setting up subscription for {wallet[:8]}: {e}")
                import traceback
                logger.error(traceback.format_exc())
        
        logger.info(f"✅ Setup complete! {successful_subs}/{len(self.target_wallets)} subscriptions active")
        
        if successful_subs > 0:
            logger.info("🚀 Ready for real-time detection!")
        else:
            logger.error("❌ No subscriptions active!")

async def main():
    try:
        logger.info("Starting minimal bot test...")
        
        # Create config using default settings
        config = CopyTradeConfig()
        
        bot = MinimalWebSocketBot(config)
        await bot.start_monitoring()
        
    except Exception as e:
        logger.error(f"Error in main: {e}")
        import traceback
        logger.error(traceback.format_exc())

if __name__ == "__main__":
    asyncio.run(main())
