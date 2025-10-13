#!/usr/bin/env python3

import asyncio
import logging
import json
import time
import websockets
from config import CopyTradeConfig
from env_keys import EnvKeys

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class WorkingWebSocketBot:
    """Working WebSocket bot with proper subscription setup"""
    
    def __init__(self, config: CopyTradeConfig):
        logger.info("WORKING BOT: Initializing...")
        self.config = config
        self.is_running = False
        
        # Essential components only
        self.env_keys = EnvKeys()
        self.ws_url = self.env_keys.HELIUS_Standard_Websocket_URL
        self.target_wallets = config.target_wallets
        
        # WebSocket state
        self.ws_connection = None
        self.subscription_ids = {}
        
        logger.info(f"WORKING BOT: Loaded {len(self.target_wallets)} target wallets")
        logger.info(f"WORKING BOT: WebSocket URL: {self.ws_url}")
        
    async def start_monitoring(self):
        """Working start_monitoring that actually completes subscription setup"""
        try:
            logger.info("WORKING BOT: start_monitoring called")
            logger.info("WORKING BOT: Starting WebSocket monitoring...")
            self.is_running = True
            
            while self.is_running:
                try:
                    logger.info("WORKING BOT: About to start WebSocket monitoring")
                    await self._monitor_wallets_via_websocket()
                    logger.info("WORKING BOT: _monitor_wallets_via_websocket returned")
                    break  # Exit after one successful run for testing
                    
                except Exception as e:
                    logger.error(f"WORKING BOT: Monitoring error: {e}")
                    import traceback
                    logger.error(traceback.format_exc())
                    break
                    
            logger.info("WORKING BOT: Exited monitoring loop")
            
        except Exception as e:
            logger.error(f"WORKING BOT: Error in start_monitoring: {e}")
            import traceback
            logger.error(traceback.format_exc())

    async def _monitor_wallets_via_websocket(self):
        """Working WebSocket monitoring with proper subscription setup"""
        try:
            logger.info("WORKING BOT: _monitor_wallets_via_websocket started")
            
            # Create WebSocket connection with timeout
            headers = {
                "Content-Type": "application/json",
                "Authorization": f"Bearer {self.env_keys.HELIUS_API_KEY}"
            }
            
            logger.info(f"WORKING BOT: Attempting to connect to WebSocket: {self.ws_url}")
            
            try:
                ws_connection = await asyncio.wait_for(
                    websockets.connect(
                        self.ws_url, 
                        additional_headers=headers
                    ),
                    timeout=10.0
                )
                
                async with ws_connection as ws:
                    self.ws_connection = ws
                    logger.info("WORKING BOT: ✅ WebSocket connected successfully!")
                    
                    # Setup subscriptions
                    logger.info("WORKING BOT: About to call _setup_subscriptions...")
                    await self._setup_subscriptions(ws)
                    logger.info("WORKING BOT: _setup_subscriptions completed successfully")
                    
                    # Listen for messages for 30 seconds then exit for testing
                    logger.info("WORKING BOT: Listening for messages (30 second test)...")
                    start_time = time.time()
                    message_count = 0
                    
                    while time.time() - start_time < 30:  # Listen for 30 seconds
                        try:
                            message = await asyncio.wait_for(ws.recv(), timeout=2.0)
                            data = json.loads(message)
                            message_count += 1
                            
                            method = data.get('method', 'unknown')
                            logger.info(f"WORKING BOT: [{message_count}] Received: {method}")
                            
                            if method == "logsNotification":
                                logger.info("🚀 REAL-TIME LOGS NOTIFICATION RECEIVED!")
                                params = data.get("params", {})
                                result = params.get("result", {})
                                signature = result.get("signature", "unknown")
                                logs = result.get("logs", [])
                                logger.info(f"🚀 INSTANT DETECTION: {signature[:8]}... with {len(logs)} logs")
                                
                        except asyncio.TimeoutError:
                            logger.debug("WORKING BOT: No message received (timeout)")
                            continue
                        except json.JSONDecodeError as e:
                            logger.error(f"WORKING BOT: JSON decode error: {e}")
                        except Exception as e:
                            logger.error(f"WORKING BOT: Message processing error: {e}")
                            break
                    
                    logger.info(f"WORKING BOT: Test completed - received {message_count} messages")
            
            except asyncio.TimeoutError:
                logger.error(f"WORKING BOT: ⏰ WebSocket connection timeout after 10 seconds")
            except Exception as ws_error:
                logger.error(f"WORKING BOT: ❌ WebSocket connection error: {ws_error}")
                import traceback
                logger.error(traceback.format_exc())
                
        except Exception as e:
            logger.error(f"WORKING BOT: Error in _monitor_wallets_via_websocket: {e}")
            import traceback
            logger.error(traceback.format_exc())

    async def _setup_subscriptions(self, ws):
        """Working subscription setup using only logsSubscribe"""
        logger.info(f"WORKING BOT: Setting up subscriptions for {len(self.target_wallets)} wallets")
        
        if not self.target_wallets:
            logger.error("WORKING BOT: ❌ No target wallets found!")
            return
        
        successful_subs = 0
        
        for wallet_idx, wallet in enumerate(self.target_wallets):
            logger.info(f"WORKING BOT: [{wallet_idx+1}/{len(self.target_wallets)}] Setting up subscription for: {wallet[:8]}...")
            
            try:
                # Use logsSubscribe which is most reliable
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
                
                logger.info("WORKING BOT: Sending logs subscription...")
                await ws.send(json.dumps(logs_sub))
                
                logger.info("WORKING BOT: Waiting for subscription response...")
                response = await asyncio.wait_for(ws.recv(), timeout=10.0)
                response_data = json.loads(response)
                
                logger.info(f"WORKING BOT: Subscription response: {response_data}")
                
                if "result" in response_data:
                    sub_id = response_data["result"]
                    self.subscription_ids[f"logs_{wallet}"] = sub_id
                    successful_subs += 1
                    logger.info(f"WORKING BOT: ✅ Subscription successful (ID: {sub_id})")
                else:
                    logger.error(f"WORKING BOT: ❌ Subscription failed: {response_data}")
                    
            except Exception as e:
                logger.error(f"WORKING BOT: Error setting up subscription: {e}")
                import traceback
                logger.error(traceback.format_exc())
        
        logger.info(f"WORKING BOT: ✅ Setup complete! {successful_subs}/{len(self.target_wallets)} subscriptions active")
        
        if successful_subs > 0:
            logger.info("🚀 WORKING BOT: Ready for real-time detection!")
        else:
            logger.error("❌ WORKING BOT: No subscriptions active!")

async def main():
    try:
        logger.info("WORKING BOT: Starting main()")
        
        # Create config
        config = CopyTradeConfig()
        logger.info("WORKING BOT: Config created")
        
        # Create working bot instance
        bot = WorkingWebSocketBot(config)
        logger.info("WORKING BOT: Bot instance created")
        
        # Start monitoring
        logger.info("WORKING BOT: Calling start_monitoring...")
        await bot.start_monitoring()
        logger.info("WORKING BOT: start_monitoring completed")
        
    except Exception as e:
        logger.error(f"WORKING BOT: Error in main: {e}")
        import traceback
        logger.error(traceback.format_exc())

if __name__ == "__main__":
    asyncio.run(main())
