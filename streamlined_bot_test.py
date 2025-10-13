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

class StreamlinedCopyTradingBot:
    """Streamlined bot focused only on WebSocket real-time detection"""
    
    def __init__(self, config: CopyTradeConfig):
        logger.info("STREAMLINED BOT: Initializing...")
        self.config = config
        self.is_running = False
        
        # Essential components only
        self.env_keys = EnvKeys()
        self.ws_url = self.env_keys.HELIUS_Standard_Websocket_URL
        self.target_wallets = config.target_wallets
        
        # WebSocket state
        self.ws_connection = None
        self.subscription_ids = {}
        
        logger.info(f"STREAMLINED BOT: Loaded {len(self.target_wallets)} target wallets")
        logger.info(f"STREAMLINED BOT: WebSocket URL: {self.ws_url}")
        
    async def start_monitoring(self):
        """Streamlined start_monitoring focused on WebSocket only"""
        try:
            logger.info("STREAMLINED BOT: start_monitoring called")
            logger.info("STREAMLINED BOT: Starting WebSocket monitoring...")
            self.is_running = True
            logger.info(f"STREAMLINED BOT: is_running = {self.is_running}")
            
            logger.info("STREAMLINED BOT: About to enter while loop")
            while self.is_running:
                logger.info("STREAMLINED BOT: Inside while loop iteration")
                try:
                    logger.info("STREAMLINED BOT: About to start WebSocket monitoring")
                    
                    # Call WebSocket monitor
                    logger.info("STREAMLINED BOT: Calling _monitor_wallets_via_websocket")
                    await self._monitor_wallets_via_websocket()
                    logger.info("STREAMLINED BOT: _monitor_wallets_via_websocket returned")
                    
                    # Break after one iteration for testing
                    break
                    
                except Exception as e:
                    logger.error(f"STREAMLINED BOT: Monitoring error: {e}")
                    import traceback
                    logger.error(traceback.format_exc())
                    break
                    
            logger.info("STREAMLINED BOT: Exited while loop")
            
        except Exception as e:
            logger.error(f"STREAMLINED BOT: Error in start_monitoring: {e}")
            import traceback
            logger.error(traceback.format_exc())

    async def _monitor_wallets_via_websocket(self):
        """Streamlined WebSocket monitoring"""
        try:
            logger.info("STREAMLINED BOT: _monitor_wallets_via_websocket started")
            
            # Create WebSocket connection with TIMEOUT
            headers = {
                "Content-Type": "application/json",
                "Authorization": f"Bearer {self.env_keys.HELIUS_API_KEY}"
            }
            
            logger.info(f"STREAMLINED BOT: Attempting to connect to WebSocket: {self.ws_url}")
            
            try:
                # Add timeout to prevent hanging
                ws_connection = await asyncio.wait_for(
                    websockets.connect(
                        self.ws_url, 
                        additional_headers=headers  # Use additional_headers instead of extra_headers
                    ),
                    timeout=10.0  # 10 second timeout
                )
                
                async with ws_connection as ws:
                    self.ws_connection = ws
                    logger.info("STREAMLINED BOT: ✅ WebSocket connected successfully!")
                    
                    # Test subscription setup
                    logger.info("STREAMLINED BOT: About to call _setup_subscriptions...")
                    await self._setup_subscriptions(ws)
                    logger.info("STREAMLINED BOT: _setup_subscriptions completed successfully")
                    
                    # Listen for a few messages then exit for testing
                    logger.info("STREAMLINED BOT: Listening for messages (10 second test)...")
                    start_time = time.time()
                    while time.time() - start_time < 10:  # Listen for 10 seconds
                        try:
                            message = await asyncio.wait_for(ws.recv(), timeout=1.0)
                            data = json.loads(message)
                            logger.info(f"STREAMLINED BOT: Received message: {data.get('method', 'unknown')}")
                        except asyncio.TimeoutError:
                            logger.debug("STREAMLINED BOT: No message received (timeout)")
                            continue
                        except json.JSONDecodeError as e:
                            logger.error(f"STREAMLINED BOT: JSON decode error: {e}")
                        except Exception as e:
                            logger.error(f"STREAMLINED BOT: Message processing error: {e}")
                            break
                    
                    logger.info("STREAMLINED BOT: Test listening period completed")
            
            except asyncio.TimeoutError:
                logger.error(f"STREAMLINED BOT: ⏰ WebSocket connection timeout after 10 seconds")
                logger.error(f"STREAMLINED BOT: Failed to connect to: {self.ws_url}")
            except Exception as ws_error:
                logger.error(f"STREAMLINED BOT: ❌ WebSocket connection error: {ws_error}")
                import traceback
                logger.error(traceback.format_exc())
                
        except Exception as e:
            logger.error(f"STREAMLINED BOT: Error in _monitor_wallets_via_websocket: {e}")
            import traceback
            logger.error(traceback.format_exc())

    async def _setup_subscriptions(self, ws):
        """Streamlined subscription setup"""
        logger.info(f"STREAMLINED BOT: Setting up subscriptions for {len(self.target_wallets)} wallets")
        
        if not self.target_wallets:
            logger.error("STREAMLINED BOT: ❌ No target wallets found!")
            return
        
        # Test with just the first wallet for now
        wallet = self.target_wallets[0]
        logger.info(f"STREAMLINED BOT: Testing subscription for wallet: {wallet[:8]}...")
        
        try:
            # Signature subscription
            signature_sub = {
                "jsonrpc": "2.0",
                "id": f"signature_{wallet}_{int(time.time())}",
                "method": "signatureSubscribe",
                "params": [
                    wallet,
                    {
                        "commitment": "processed",
                        "enableReceivedNotification": True
                    }
                ]
            }
            
            logger.info("STREAMLINED BOT: Sending signature subscription...")
            await ws.send(json.dumps(signature_sub))
            
            response = await asyncio.wait_for(ws.recv(), timeout=5.0)
            response_data = json.loads(response)
            
            logger.info(f"STREAMLINED BOT: Subscription response: {response_data}")
            
            if "result" in response_data:
                sub_id = response_data["result"]
                self.subscription_ids[f"signature_{wallet}"] = sub_id
                logger.info(f"STREAMLINED BOT: ✅ Signature subscription successful (ID: {sub_id})")
            else:
                logger.error(f"STREAMLINED BOT: ❌ Signature subscription failed: {response_data}")
                
        except Exception as e:
            logger.error(f"STREAMLINED BOT: Error setting up subscription: {e}")
            import traceback
            logger.error(traceback.format_exc())

async def main():
    try:
        logger.info("STREAMLINED BOT: Starting main()")
        
        # Create config
        config = CopyTradeConfig()
        logger.info("STREAMLINED BOT: Config created")
        
        # Create streamlined bot instance
        bot = StreamlinedCopyTradingBot(config)
        logger.info("STREAMLINED BOT: Bot instance created")
        
        # Start monitoring
        logger.info("STREAMLINED BOT: Calling start_monitoring...")
        await bot.start_monitoring()
        logger.info("STREAMLINED BOT: start_monitoring completed")
        
    except Exception as e:
        logger.error(f"STREAMLINED BOT: Error in main: {e}")
        import traceback
        logger.error(traceback.format_exc())

if __name__ == "__main__":
    asyncio.run(main())
