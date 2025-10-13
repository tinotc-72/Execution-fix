#!/usr/bin/env python3

import asyncio
import json
import logging
import time
import websockets
from env_keys import EnvKeys

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

async def test_subscription_setup():
    """Test just the subscription setup in isolation"""
    try:
        # Get environment
        env_keys = EnvKeys()
        ws_url = env_keys.HELIUS_Standard_Websocket_URL
        
        # Use actual wallet from main config
        test_wallet = "suqh5sHtr8HyJ7q8scBimULPkPpA557prMG47xCHQfK"
        
        logger.info(f"Testing subscription setup for: {test_wallet[:8]}...")
        logger.info(f"WebSocket URL: {ws_url}")
        
        # Headers
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {env_keys.HELIUS_API_KEY}"
        }
        
        logger.info("Connecting to WebSocket...")
        
        # Connect with timeout
        ws_connection = await asyncio.wait_for(
            websockets.connect(ws_url, additional_headers=headers),
            timeout=10.0
        )
        
        async with ws_connection as ws:
            logger.info("✅ WebSocket connected!")
            
            # Test subscription
            logger.info("Setting up test subscription...")
            
            logs_sub = {
                "jsonrpc": "2.0",
                "id": f"logs_{test_wallet}_{int(time.time())}",
                "method": "logsSubscribe", 
                "params": [
                    {
                        "mentions": [test_wallet]
                    },
                    {
                        "commitment": "processed"
                    }
                ]
            }
            
            logger.info("Sending subscription request...")
            await ws.send(json.dumps(logs_sub))
            logger.info("Subscription request sent!")
            
            logger.info("Waiting for subscription response...")
            response = await asyncio.wait_for(ws.recv(), timeout=15.0)
            logger.info("Response received!")
            
            response_data = json.loads(response)
            logger.info(f"Response data: {response_data}")
            
            if "result" in response_data:
                sub_id = response_data["result"]
                logger.info(f"✅ Subscription successful! ID: {sub_id}")
                
                # Listen for a few messages to test
                logger.info("Listening for messages for 30 seconds...")
                start_time = time.time()
                message_count = 0
                
                while time.time() - start_time < 30:
                    try:
                        message = await asyncio.wait_for(ws.recv(), timeout=2.0)
                        data = json.loads(message)
                        message_count += 1
                        
                        method = data.get('method', 'unknown')
                        logger.info(f"[{message_count}] Received: {method}")
                        
                    except asyncio.TimeoutError:
                        logger.debug("No message (timeout)")
                        continue
                    except Exception as e:
                        logger.error(f"Message error: {e}")
                        break
                
                logger.info(f"Test complete! Received {message_count} messages")
                
            else:
                logger.error(f"❌ Subscription failed: {response_data}")
                
    except Exception as e:
        logger.error(f"❌ Test failed: {e}")
        import traceback
        logger.error(traceback.format_exc())

if __name__ == "__main__":
    asyncio.run(test_subscription_setup())
