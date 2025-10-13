#!/usr/bin/env python3
"""
Minimal WebSocket Test - Debug why trades aren't being detected
"""

import asyncio
import websockets
import json
import logging
from env_keys import EnvKeys

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def test_wallet_monitoring():
    """Test if WebSocket is actually receiving notifications from your target wallets"""
    
    # Your target wallets
    target_wallets = [
        "suqh5sHtr8HyJ7q8scBimULPkPpA557prMG47xCHQfK",  # Target wallet 1
        "DfMxre4cKmvogbLrPigxmibVTTQDuzjdXojWzjCXXhzj"   # Target wallet 2
    ]
    
    # Get WebSocket URL
    keys = EnvKeys()
    ws_url = keys.HELIUS_Standard_Websocket_URL
    
    logger.info(f"🔗 Connecting to: {ws_url}")
    logger.info(f"🎯 Monitoring wallets:")
    for i, wallet in enumerate(target_wallets, 1):
        logger.info(f"   {i}. {wallet}")
    
    try:
        async with websockets.connect(ws_url) as websocket:
            logger.info("✅ WebSocket connected!")
            
            # Subscribe to each wallet
            subscription_id = 1
            for wallet in target_wallets:
                subscribe_message = {
                    "jsonrpc": "2.0",
                    "id": subscription_id,
                    "method": "logsSubscribe",
                    "params": [
                        {
                            "mentions": [wallet]
                        },
                        {
                            "commitment": "confirmed"
                        }
                    ]
                }
                
                await websocket.send(json.dumps(subscribe_message))
                logger.info(f"📡 Subscribed to {wallet[:8]}... (ID: {subscription_id})")
                subscription_id += 1
            
            # Wait for subscription confirmations
            logger.info("⏳ Waiting for subscription confirmations...")
            for i in range(len(target_wallets)):
                message = await websocket.recv()
                response = json.loads(message)
                logger.info(f"✅ Subscription {i+1} confirmed: {response}")
            
            logger.info("🎧 Now listening for real-time notifications...")
            logger.info("=" * 60)
            
            # Listen for notifications
            message_count = 0
            while True:
                try:
                    message = await asyncio.wait_for(websocket.recv(), timeout=30.0)
                    data = json.loads(message)
                    message_count += 1
                    
                    method = data.get("method", "unknown")
                    logger.info(f"📨 [{message_count}] Received: {method}")
                    
                    if method == "logsNotification":
                        params = data.get("params", {})
                        result = params.get("result", {})
                        value = result.get("value", {})
                        
                        signature = value.get("signature", "")
                        logs = value.get("logs", [])
                        subscription = params.get("subscription", "")
                        
                        logger.info(f"🚨 LOGS NOTIFICATION!")
                        logger.info(f"   📝 Signature: {signature[:12]}...")
                        logger.info(f"   📊 Logs: {len(logs)} entries")
                        logger.info(f"   🔗 Subscription: {subscription}")
                        
                        # Show first few log entries
                        for i, log in enumerate(logs[:3]):
                            logger.info(f"   [{i+1}] {log}")
                        
                        # Check for trading activity
                        log_text = ' '.join(logs).lower()
                        if any(keyword in log_text for keyword in ['buy', 'sell', 'swap', 'pump', 'jupiter', 'raydium']):
                            logger.info("🔥 POTENTIAL TRADE DETECTED!")
                        
                        logger.info("-" * 40)
                    
                except asyncio.TimeoutError:
                    logger.info(f"⏰ Timeout (30s) - received {message_count} messages so far")
                    continue
                    
    except Exception as e:
        logger.error(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    print("🔍 DEBUGGING: Why are trades not being detected?")
    print("This test will show if WebSocket notifications are being received.")
    print("Leave this running and check if you see notifications when the wallets trade.")
    print("=" * 60)
    
    asyncio.run(test_wallet_monitoring())
