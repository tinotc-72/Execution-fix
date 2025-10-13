#!/usr/bin/env python3
"""
Quick WebSocket subscription test to debug connection issues
"""

import asyncio
import json
import websockets
import logging
from env_keys import kz

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Test wallets from config
TEST_WALLETS = [
    "suqh5sHtr8HyJ7q8scBimULPkPpA557prMG47xCXXhzj",  # Your target wallet 1
    "DfMxre4cKmvogbLrPigxmibVTTQDuzjdXojWzjCXXhzj",  # Your target wallet 2
]

async def test_websocket_subscriptions():
    """Test WebSocket connection and subscription setup"""
    try:
        # WebSocket URL
        ws_url = f"wss://mainnet.helius-rpc.com/v0?api-key={kz.HELIUS_API_KEY}"
        logger.info(f"🔗 Connecting to: {ws_url[:50]}...")
        
        # Create headers
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {kz.HELIUS_API_KEY}"
        }
        
        # Connect to WebSocket
        async with websockets.connect(ws_url, extra_headers=headers) as ws:
            logger.info("✅ WebSocket connected successfully!")
            
            # Test subscription setup
            subscription_ids = {}
            
            for i, wallet in enumerate(TEST_WALLETS):
                logger.info(f"🎯 [{i+1}/{len(TEST_WALLETS)}] Testing subscription for wallet: {wallet[:8]}...")
                
                # Test logsSubscribe
                logs_sub = {
                    "jsonrpc": "2.0",
                    "id": f"logs_{wallet}",
                    "method": "logsSubscribe",
                    "params": [
                        {
                            "mentions": [wallet]
                        },
                        {
                            "commitment": "processed",
                            "encoding": "jsonParsed"
                        }
                    ]
                }
                
                logger.info(f"📤 Sending logsSubscribe request for {wallet[:8]}...")
                await ws.send(json.dumps(logs_sub))
                
                # Wait for response
                response = await asyncio.wait_for(ws.recv(), timeout=10.0)
                response_data = json.loads(response)
                logger.info(f"📥 Response: {response_data}")
                
                if "result" in response_data:
                    subscription_ids[f"logs_{wallet}"] = response_data["result"]
                    logger.info(f"✅ Successfully subscribed to logs for {wallet[:8]}... (ID: {response_data['result']})")
                else:
                    logger.error(f"❌ Failed to subscribe to logs for {wallet[:8]}...: {response_data}")
                
                # Test accountSubscribe
                account_sub = {
                    "jsonrpc": "2.0",
                    "id": f"account_{wallet}",
                    "method": "accountSubscribe",
                    "params": [
                        wallet,
                        {
                            "commitment": "processed",
                            "encoding": "jsonParsed"
                        }
                    ]
                }
                
                logger.info(f"📤 Sending accountSubscribe request for {wallet[:8]}...")
                await ws.send(json.dumps(account_sub))
                
                # Wait for response
                response = await asyncio.wait_for(ws.recv(), timeout=10.0)
                response_data = json.loads(response)
                logger.info(f"📥 Response: {response_data}")
                
                if "result" in response_data:
                    subscription_ids[f"account_{wallet}"] = response_data["result"]
                    logger.info(f"✅ Successfully subscribed to account for {wallet[:8]}... (ID: {response_data['result']})")
                else:
                    logger.error(f"❌ Failed to subscribe to account for {wallet[:8]}...: {response_data}")
            
            logger.info(f"🎯 ✅ ALL SUBSCRIPTIONS SETUP COMPLETE!")
            logger.info(f"📊 Total subscriptions: {len(subscription_ids)}")
            logger.info(f"🆔 Subscription IDs: {subscription_ids}")
            
            # Listen for messages for 30 seconds
            logger.info("👂 Listening for messages for 30 seconds...")
            message_count = 0
            start_time = asyncio.get_event_loop().time()
            
            while asyncio.get_event_loop().time() - start_time < 30:
                try:
                    message = await asyncio.wait_for(ws.recv(), timeout=5.0)
                    data = json.loads(message)
                    message_count += 1
                    
                    method = data.get("method", "unknown")
                    logger.info(f"📨 [{message_count}] Received: {method}")
                    
                    if method == "logsNotification":
                        params = data.get("params", {})
                        result = params.get("result", {})
                        signature = result.get("signature", "unknown")
                        logs_count = len(result.get("logs", []))
                        logger.info(f"   🎯 LOGS NOTIFICATION: {signature[:8]}... with {logs_count} log messages")
                        
                    elif method == "accountNotification":
                        params = data.get("params", {})
                        result = params.get("result", {})
                        balance = result.get("value", {}).get("lamports", 0)
                        logger.info(f"   🔍 ACCOUNT NOTIFICATION: Balance = {balance/1e9:.6f} SOL")
                    
                except asyncio.TimeoutError:
                    logger.debug("⏰ No message received in last 5 seconds...")
                    continue
                except json.JSONDecodeError as e:
                    logger.error(f"❌ JSON decode error: {e}")
                    continue
            
            logger.info(f"✅ Test completed! Received {message_count} messages in 30 seconds")
            
    except Exception as e:
        logger.error(f"❌ Test failed: {e}")
        import traceback
        logger.error(traceback.format_exc())

if __name__ == "__main__":
    asyncio.run(test_websocket_subscriptions())
