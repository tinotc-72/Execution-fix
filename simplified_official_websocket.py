#!/usr/bin/env python3
"""
SIMPLIFIED OFFICIAL WEBSOCKET IMPLEMENTATION
Based directly on Solana RPC WebSocket documentation
Using .env file for sensitive configuration
"""

import asyncio
import json
import logging
import websockets
from typing import Dict, List, Optional, Any
from datetime import datetime
import aiohttp
from solana.rpc.async_api import AsyncClient
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Setup logging with immediate flush
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler()]
)
logger = logging.getLogger(__name__)

# Force immediate output
import sys
sys.stdout.flush()

class SimplifiedOfficialWebSocket:
    """
    SIMPLIFIED WEBSOCKET - EXACTLY AS PER OFFICIAL SOLANA DOCUMENTATION
    https://solana.com/docs/rpc/websocket/accountsubscribe
    https://solana.com/docs/rpc/websocket/logssubscribe
    """
    
    def __init__(self, target_wallets: List[str]):
        # Get API key and URLs from environment variables
        self.api_key = os.getenv('HELIUS_API_KEY')
        if not self.api_key:
            raise ValueError("HELIUS_API_KEY not found in .env file!")
            
        # Use the correct WebSocket URL from .env
        ws_url_from_env = os.getenv('HELIUS_Standard_Websocket_URL')
        if ws_url_from_env:
            self.ws_url = ws_url_from_env
        else:
            # Fallback to constructing URL with API key
            self.ws_url = f"wss://mainnet.helius-rpc.com?api-key={self.api_key}"
            
        self.target_wallets = target_wallets
        self.subscription_ids = {}
        
        # Use RPC URL from .env
        rpc_url = os.getenv('HELIUS_RPC_URL', f"https://mainnet.helius-rpc.com?api-key={self.api_key}")
        self.client = AsyncClient(rpc_url)
        
        logger.info(f"🔑 Using API key from .env: {self.api_key[:12]}...")
        logger.info(f"🌐 WebSocket URL: {self.ws_url[:50]}...")
        logger.info(f"🔗 RPC URL: {rpc_url[:50]}...")
        
    async def start(self):
        """Start the WebSocket connection and monitoring"""
        logger.info("🚀 Starting SIMPLIFIED OFFICIAL WebSocket...")
        await self._monitor_with_official_websocket()
        
    async def _monitor_with_official_websocket(self):
        """Official WebSocket monitoring exactly as per documentation"""
        while True:
            try:
                logger.info(f"🔗 Connecting to WebSocket: {self.ws_url}")
                
                async with websockets.connect(self.ws_url) as ws:
                    logger.info("✅ WebSocket connected!")
                    
                    # Setup subscriptions exactly as per official docs
                    await self._setup_official_subscriptions(ws)
                    
                    # Listen for messages
                    async for message in ws:
                        try:
                            data = json.loads(message)
                            await self._handle_official_message(data)
                        except json.JSONDecodeError as e:
                            logger.error(f"❌ JSON decode error: {e}")
                        except Exception as e:
                            logger.error(f"❌ Message handling error: {e}")
                            
            except Exception as e:
                logger.error(f"❌ WebSocket error: {e}")
                logger.info("🔄 Reconnecting in 5 seconds...")
                await asyncio.sleep(5)
                
    async def _setup_official_subscriptions(self, ws):
        """Setup subscriptions exactly as per official Solana documentation"""
        request_id = 1
        
        for wallet in self.target_wallets:
            logger.info(f"📡 Setting up official subscriptions for {wallet[:8]}...")
            
            # 1. accountSubscribe - exactly as per docs
            account_sub = {
                "jsonrpc": "2.0",
                "id": request_id,
                "method": "accountSubscribe",
                "params": [
                    wallet,
                    {
                        "encoding": "jsonParsed",
                        "commitment": "processed"  # Use processed for fastest detection
                    }
                ]
            }
            
            await ws.send(json.dumps(account_sub))
            logger.info(f"✅ Sent accountSubscribe for {wallet[:8]}...")
            request_id += 1
            
            # 2. logsSubscribe - exactly as per docs  
            logs_sub = {
                "jsonrpc": "2.0",
                "id": request_id,
                "method": "logsSubscribe",
                "params": [
                    {
                        "mentions": [wallet]  # Official format: mentions array with wallet
                    },
                    {
                        "commitment": "processed"  # Use processed for fastest detection
                    }
                ]
            }
            
            await ws.send(json.dumps(logs_sub))
            logger.info(f"✅ Sent logsSubscribe for {wallet[:8]}...")
            request_id += 1
            
        logger.info("🎯 All official subscriptions sent!")
        
    async def _handle_official_message(self, data: Dict[str, Any]):
        """Handle WebSocket messages exactly as per official documentation"""
        try:
            # Handle subscription confirmations
            if "result" in data and isinstance(data.get("result"), int):
                logger.info(f"✅ Subscription confirmed: ID {data['result']}")
                return
                
            method = data.get("method")
            
            # Official accountNotification - account balance changed
            if method == "accountNotification":
                logger.info("🚨 ACCOUNT NOTIFICATION RECEIVED!")
                params = data.get("params", {})
                result = params.get("result", {})
                context = result.get("context", {})
                value = result.get("value", {})
                
                # Log the raw notification for debugging
                logger.info(f"📊 Account Data: lamports={value.get('lamports', 0)}, slot={context.get('slot', 0)}")
                
                # When account balance changes, fetch recent transactions
                subscription_id = params.get("subscription")
                logger.info(f"🔍 Account changed for subscription {subscription_id} - fetching recent transactions...")
                
                # Find which wallet this is for and analyze recent transactions
                asyncio.create_task(self._analyze_recent_activity_for_subscription(subscription_id))
                
            # Official logsNotification - transaction mentioning wallet
            elif method == "logsNotification":
                logger.info("🚨 LOGS NOTIFICATION RECEIVED!")
                params = data.get("params", {})
                result = params.get("result", {})
                
                signature = result.get("signature")
                logs = result.get("logs", [])
                err = result.get("err")
                
                if err:
                    logger.warning(f"⚠️ Transaction failed: {signature[:12] if signature else 'unknown'}")
                    return
                    
                logger.info(f"🔥 LIVE TRANSACTION: {signature[:12] if signature else 'unknown'}...")
                logger.info(f"📝 Logs ({len(logs)} lines):")
                for i, log in enumerate(logs[:5]):  # Show first 5 logs
                    logger.info(f"   {i+1}: {log}")
                
                # Analyze this live transaction immediately
                if signature:
                    await self._analyze_live_transaction(signature, logs)
                    
            else:
                logger.debug(f"📨 Other message: {method}")
                
        except Exception as e:
            logger.error(f"❌ Error handling message: {e}")
            import traceback
            logger.error(traceback.format_exc())
            
    async def _analyze_recent_activity_for_subscription(self, subscription_id: int):
        """Analyze recent activity when account balance changes"""
        try:
            # In a real implementation, you'd map subscription_id back to wallet
            logger.info(f"🔍 Analyzing recent activity for subscription {subscription_id}")
            
            # For now, just log that we detected activity
            logger.info("💡 Account balance changed - this indicates recent transaction activity!")
            
        except Exception as e:
            logger.error(f"❌ Error analyzing recent activity: {e}")
            
    async def _analyze_live_transaction(self, signature: str, logs: List[str]):
        """Analyze a live transaction from logs notification"""
        try:
            logger.info(f"🔍 ANALYZING LIVE TRANSACTION: {signature[:12]}...")
            
            # Look for trading indicators in logs
            trade_detected = False
            trade_type = "unknown"
            
            # Simple pattern matching on logs
            for log in logs:
                log_lower = log.lower()
                
                # Look for common DEX patterns
                if any(pattern in log_lower for pattern in [
                    'swap', 'buy', 'sell', 'trade', 'raydium', 'jupiter', 'pump'
                ]):
                    trade_detected = True
                    if any(buy_pattern in log_lower for buy_pattern in ['buy', 'swap in']):
                        trade_type = "BUY"
                    elif any(sell_pattern in log_lower for sell_pattern in ['sell', 'swap out']):
                        trade_type = "SELL"
                    break
                    
            if trade_detected:
                logger.info(f"🚀 TRADE DETECTED: {trade_type} - {signature[:12]}...")
                logger.info("💰 This is where you would execute your copy trade!")
            else:
                logger.info(f"ℹ️ Non-trade transaction: {signature[:12]}...")
                
        except Exception as e:
            logger.error(f"❌ Error analyzing live transaction: {e}")

async def main():
    """Test the simplified WebSocket implementation using .env configuration"""
    # Load target wallets from environment or use defaults
    target_wallets = [
        "suqh5sHtr8HyJ7q8scBimULPkPpA557prMG47xCHQfK",
        "DfMxre4cKmvogbLrPigxmibVTTQDuzjdXojWzjCXXhzj"
    ]
    
    print("🚀 Starting SIMPLIFIED OFFICIAL WebSocket with .env configuration...")
    print("📖 Using your actual API key and URLs from .env file")
    print("🎯 No hardcoded credentials!")
    print()
    
    # Create and start the simplified WebSocket (no API key needed - it reads from .env)
    ws_client = SimplifiedOfficialWebSocket(target_wallets)
    await ws_client.start()

if __name__ == "__main__":
    print("🚀 Starting SIMPLIFIED OFFICIAL WebSocket Test...")
    print("📖 Based directly on Solana RPC WebSocket documentation")
    print("🎯 No complex layers - pure official implementation")
    print()
    
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n👋 Shutting down...")
