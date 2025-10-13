#!/usr/bin/env python3

import asyncio
import json
import logging
import websockets
from env_keys import EnvKeys

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

async def test_websocket():
    """Test WebSocket connection and subscription for the target wallet"""
    try:
        env_keys = EnvKeys()
        ws_url = env_keys.HELIUS_Standard_Websocket_URL
        target_wallet = "suqh5sHtr8HyJ7q8scBimULPkPpA557prMG47xCHQfK"  # The wallet the user mentioned
        
        logger.info(f"Testing WebSocket connection to: {ws_url}")
        logger.info(f"Target wallet: {target_wallet}")
        
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {env_keys.HELIUS_API_KEY}"
        }
        
        async with websockets.connect(ws_url, additional_headers=headers) as ws:
            logger.info("✅ WebSocket connected!")
            
            # Set up logs subscription for the target wallet
            logs_sub = {
                "jsonrpc": "2.0",
                "id": f"logs_{target_wallet}",
                "method": "logsSubscribe",
                "params": [
                    {
                        "mentions": [target_wallet]
                    },
                    {
                        "commitment": "processed"
                    }
                ]
            }
            
            logger.info("Sending subscription request...")
            await ws.send(json.dumps(logs_sub))
            
            logger.info("Waiting for subscription response...")
            response = await asyncio.wait_for(ws.recv(), timeout=10.0)
            response_data = json.loads(response)
            
            logger.info(f"Subscription response: {response_data}")
            
            if "result" in response_data:
                sub_id = response_data["result"]
                logger.info(f"✅ Subscription successful! ID: {sub_id}")
                
                # Listen for messages for 30 seconds
                logger.info("Listening for messages for 30 seconds...")
                start_time = asyncio.get_event_loop().time()
                message_count = 0
                
                while asyncio.get_event_loop().time() - start_time < 30:
                    try:
                        message = await asyncio.wait_for(ws.recv(), timeout=2.0)
                        data = json.loads(message)
                        message_count += 1
                        
                        method = data.get('method', 'unknown')
                        if method == "logsNotification":
                            params = data.get("params", {})
                            result = params.get("result", {})
                            signature = result.get("signature", "unknown")
                            logs = result.get("logs", [])
                            
                            logger.info(f"🚀 MESSAGE {message_count}: logsNotification")
                            logger.info(f"   Signature: {signature[:8] if signature != 'unknown' else 'unknown'}")
                            logger.info(f"   Logs count: {len(logs)}")
                            
                            if logs:
                                log_sample = ' '.join(logs[:2])[:200] + "..." if len(' '.join(logs)) > 200 else ' '.join(logs)
                                logger.info(f"   Log sample: {log_sample}")
                        else:
                            logger.info(f"[{message_count}] Other message type: {method}")
                            
                    except asyncio.TimeoutError:
                        continue
                        
                logger.info(f"Test complete! Received {message_count} messages in 30 seconds")
                
            else:
                logger.error(f"❌ Subscription failed: {response_data}")
            
    except Exception as e:
        logger.error(f"❌ Test failed: {e}")
        import traceback
        logger.error(traceback.format_exc())

if __name__ == "__main__":
    asyncio.run(test_websocket())
