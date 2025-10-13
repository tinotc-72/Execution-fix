#!/usr/bin/env python3
"""
Enhanced WebSocket Monitor for Copy Trading
==========================================

Uses multiple official Solana WebSocket subscription methods:
1. logsSubscribe - Monitor transaction logs for trade indicators
2. accountSubscribe - Monitor wallet balance changes directly
3. programSubscribe - Monitor DEX program calls for precise trade detection

Based on official Solana RPC WebSocket documentation:
- https://docs.solana.com/api/websocket/logssubscribe
- https://docs.solana.com/api/websocket/accountsubscribe  
- https://docs.solana.com/api/websocket/programsubscribe
"""

import asyncio
import json
import logging
import websockets
from datetime import datetime
from typing import Dict, List, Optional, Any, Set
from dataclasses import dataclass

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("enhanced_websocket")

@dataclass
class SubscriptionConfig:
    """WebSocket subscription configuration"""
    target_wallet: str
    websocket_url: str
    use_account_subscribe: bool = True
    use_program_subscribe: bool = True
    use_logs_subscribe: bool = True
    commitment: str = "processed"  # processed, confirmed, finalized

class EnhancedWebSocketMonitor:
    """
    Enhanced WebSocket monitor using multiple subscription types
    for more precise trade detection
    """
    
    def __init__(self, config: SubscriptionConfig):
        self.config = config
        self.ws_connection = None
        self.subscriptions: Dict[str, int] = {}  # subscription_type -> subscription_id
        self.is_running = False
        
        # DEX program IDs to monitor
        self.dex_programs = {
            "JUP6LkbZbjS1jKKwapdHNy74zcZ3tLUZoi5QNyVTaV4": "Jupiter V6",
            "JUP4Fb2cqiRUcaTHdrPC8h2gNsA2ETXiPDD33WcGuJB": "Jupiter V4", 
            "675kPX9MHTjS2zt1qfr1NYHuzeLXfQM9H24wFSUt1Mp8": "Raydium V4",
            "CAMMCzo5YL8w4VFF8KVHrK22GGUsp5VTaW7grrKgrWqK": "Raydium CPMM",
            "whirLbMiicVdio4qvUfM5KAg6Ct8VwpYzGff3uctyCc": "Orca Whirlpool",
            "9WzDXwBbmkg8ZTbNMqUxvQRAyrZzDsGYdLVL9zYtAWWM": "Orca",
            "6EF8rrecthR5Dkzon8Nwu78hRvfCKubJ14M5uBEwF6P": "Pump.fun",
            "AxiomxSitiyXyPjKgJ9XSrdhsydtZsskZTEDam3PxKcC": "Axiom DEX"
        }
        
        logger.info(f"🚀 Enhanced WebSocket Monitor initialized")
        logger.info(f"   Target Wallet: {config.target_wallet}")
        logger.info(f"   WebSocket URL: {config.websocket_url}")
        logger.info(f"   Monitoring DEX Programs: {len(self.dex_programs)}")
    
    async def start_monitoring(self):
        """Start enhanced WebSocket monitoring"""
        try:
            self.is_running = True
            logger.info("🔌 Starting enhanced WebSocket monitoring...")
            
            async with websockets.connect(self.config.websocket_url) as websocket:
                self.ws_connection = websocket
                
                # Send all subscriptions
                await self.setup_subscriptions()
                
                # Listen for messages
                while self.is_running:
                    try:
                        message = await asyncio.wait_for(websocket.recv(), timeout=1.0)
                        await self.process_message(message)
                    except asyncio.TimeoutError:
                        continue
                    except Exception as e:
                        logger.error(f"❌ WebSocket error: {e}")
                        break
                        
        except Exception as e:
            logger.error(f"❌ WebSocket connection error: {e}")
    
    async def setup_subscriptions(self):
        """Setup all WebSocket subscriptions"""
        subscription_id = 1
        
        # 1. Logs subscription (what we currently use)
        if self.config.use_logs_subscribe:
            logs_params = {
                "jsonrpc": "2.0",
                "id": subscription_id,
                "method": "logsSubscribe",
                "params": [
                    {
                        "mentions": [self.config.target_wallet]
                    },
                    {
                        "commitment": self.config.commitment
                    }
                ]
            }
            await self.ws_connection.send(json.dumps(logs_params))
            logger.info(f"📡 Subscribed to logs for wallet: {self.config.target_wallet}")
            subscription_id += 1
        
        # 2. Account subscription (monitor balance changes directly)
        if self.config.use_account_subscribe:
            account_params = {
                "jsonrpc": "2.0",
                "id": subscription_id,
                "method": "accountSubscribe",
                "params": [
                    self.config.target_wallet,
                    {
                        "encoding": "jsonParsed",
                        "commitment": self.config.commitment
                    }
                ]
            }
            await self.ws_connection.send(json.dumps(account_params))
            logger.info(f"💰 Subscribed to account balance changes: {self.config.target_wallet}")
            subscription_id += 1
        
        # 3. Program subscriptions (monitor DEX program calls)
        if self.config.use_program_subscribe:
            for program_id, program_name in self.dex_programs.items():
                program_params = {
                    "jsonrpc": "2.0",
                    "id": subscription_id,
                    "method": "programSubscribe",
                    "params": [
                        program_id,
                        {
                            "encoding": "jsonParsed",
                            "commitment": self.config.commitment,
                            "filters": [
                                {
                                    "memcmp": {
                                        "offset": 0,
                                        "bytes": self.config.target_wallet
                                    }
                                }
                            ]
                        }
                    ]
                }
                await self.ws_connection.send(json.dumps(program_params))
                logger.info(f"🎯 Subscribed to {program_name} program: {program_id}")
                subscription_id += 1
    
    async def process_message(self, message: str):
        """Process incoming WebSocket messages"""
        try:
            data = json.loads(message)
            
            # Handle subscription confirmations
            if "result" in data and isinstance(data["result"], int):
                subscription_id = data["result"]
                logger.info(f"✅ WebSocket subscription confirmed: {subscription_id}")
                return
            
            # Handle notifications
            if "params" in data and "result" in data["params"]:
                method = data.get("method", "")
                
                if method == "logsNotification":
                    await self.handle_logs_notification(data["params"]["result"])
                elif method == "accountNotification":
                    await self.handle_account_notification(data["params"]["result"])
                elif method == "programNotification":
                    await self.handle_program_notification(data["params"]["result"])
                else:
                    logger.debug(f"🤷 Unknown notification method: {method}")
            
        except Exception as e:
            logger.error(f"❌ Error processing message: {e}")
            logger.debug(f"Message content: {message[:200]}...")
    
    async def handle_logs_notification(self, result: Dict[str, Any]):
        """Handle transaction logs notifications"""
        try:
            context = result.get("context", {})
            value = result.get("value", {})
            
            signature = value.get("signature", "")
            logs = value.get("logs", [])
            error = value.get("err")
            
            if error:
                logger.debug(f"❌ Transaction failed: {signature}")
                return
            
            logger.info(f"📋 LOGS: New transaction: {signature}")
            
            # Check if logs indicate trading activity
            if self.is_trade_transaction(logs):
                logger.info(f"🔥 TRADE DETECTED via LOGS: {signature}")
                logger.info(f"   🎯 Sample logs: {logs[:2]}...")
                
                # This would trigger your copy trading logic
                await self.trigger_copy_trade_analysis(signature, "logs")
            
        except Exception as e:
            logger.error(f"❌ Error handling logs notification: {e}")
    
    async def handle_account_notification(self, result: Dict[str, Any]):
        """Handle account balance change notifications"""
        try:
            context = result.get("context", {})
            value = result.get("value", {})
            
            slot = context.get("slot", 0)
            lamports = value.get("lamports", 0)
            sol_balance = lamports / 1e9
            
            logger.info(f"💰 ACCOUNT: Balance change detected at slot {slot}")
            logger.info(f"   💎 New SOL balance: {sol_balance:.6f} SOL")
            
            # Significant balance changes might indicate trades
            # You would need to track previous balance to detect change amount
            # For now, just log the change
            logger.info(f"🔔 Account balance update - could indicate trade activity")
            
        except Exception as e:
            logger.error(f"❌ Error handling account notification: {e}")
    
    async def handle_program_notification(self, result: Dict[str, Any]):
        """Handle DEX program notifications"""
        try:
            context = result.get("context", {})
            value = result.get("value", {})
            
            slot = context.get("slot", 0)
            pubkey = value.get("pubkey", "")
            account = value.get("account", {})
            
            logger.info(f"🎯 PROGRAM: DEX program interaction detected at slot {slot}")
            logger.info(f"   📍 Account: {pubkey}")
            logger.info(f"   💼 Account data updated - likely trade activity")
            
            # This is a strong indicator of DEX activity
            logger.info(f"🚨 STRONG TRADE SIGNAL from DEX program interaction!")
            
            # This would trigger immediate copy trade analysis
            await self.trigger_copy_trade_analysis(pubkey, "program")
            
        except Exception as e:
            logger.error(f"❌ Error handling program notification: {e}")
    
    def is_trade_transaction(self, logs: List[str]) -> bool:
        """Check if transaction logs indicate trading activity"""
        if not logs:
            return False
        
        all_logs = " ".join(logs).lower()
        
        # Strong trade indicators
        strong_indicators = [
            "swap", "jupiter", "raydium", "pump", "orca", "axiom", "buy", "sell"
        ]
        
        for indicator in strong_indicators:
            if indicator in all_logs:
                return True
        
        return False
    
    async def trigger_copy_trade_analysis(self, identifier: str, source: str):
        """Trigger copy trade analysis"""
        logger.info(f"🎯 TRIGGERING COPY TRADE ANALYSIS")
        logger.info(f"   📊 Source: {source.upper()}")
        logger.info(f"   🔗 Identifier: {identifier}")
        logger.info(f"   ⏰ Timestamp: {datetime.now().isoformat()}")
        
        # Here you would call your existing copy trading logic
        # await self.bot.analyze_transaction(signature, wallet_address)
    
    async def stop(self):
        """Stop the WebSocket monitor"""
        self.is_running = False
        if self.ws_connection:
            await self.ws_connection.close()
        logger.info("🛑 Enhanced WebSocket monitor stopped")

async def test_enhanced_monitor():
    """Test the enhanced WebSocket monitor"""
    
    # Configuration
    config = SubscriptionConfig(
        target_wallet="suqh5sHtr8HyJ7q8scBimULPkPpA557prMG47xCHQfK",
        websocket_url="wss://mainnet.helius-rpc.com/v0?api-key=7277139c-ff2c-4257-ad06-2db6aa16c315",
        use_account_subscribe=True,
        use_program_subscribe=True,
        use_logs_subscribe=True,
        commitment="processed"
    )
    
    # Create and start monitor
    monitor = EnhancedWebSocketMonitor(config)
    
    try:
        logger.info("🚀 Starting Enhanced WebSocket Monitor Test...")
        logger.info("=" * 60)
        logger.info("This will monitor the target wallet using:")
        logger.info("✅ Log subscriptions (current method)")
        logger.info("✅ Account balance subscriptions (direct balance monitoring)")
        logger.info("✅ DEX program subscriptions (Jupiter, Raydium, Pump.fun, etc.)")
        logger.info("=" * 60)
        
        await monitor.start_monitoring()
        
    except KeyboardInterrupt:
        logger.info("\n👋 Stopping enhanced monitor...")
        await monitor.stop()
    except Exception as e:
        logger.error(f"❌ Monitor error: {e}")
        await monitor.stop()

if __name__ == "__main__":
    # Test the enhanced WebSocket monitor
    asyncio.run(test_enhanced_monitor())
