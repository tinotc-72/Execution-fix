#!/usr/bin/env python3
"""
FIXED Copy Trading Test - Using EXACT main.py detection approach
This script uses the identical WebSocket and detection logic as main.py
"""

import asyncio
import json
import logging
import time
import traceback
from datetime import datetime
import websockets

from config import MONITORED_WALLETS
from env_keys import EnvKeys
from advanced_copy_trading_bot import PumpCopyTradingBot

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class FixedCopyTradingTest:
    def __init__(self):
        # Use EXACT same WebSocket URL as main.py
        self.ws_url = EnvKeys().HELIUS_Standard_Websocket_URL
        self.target_wallets = MONITORED_WALLETS
        self.running = False
        
        # Initialize copy trading bot for execution
        copy_config = {
            'fixed_buy_amount': 0.01,     # Test with small amount
            'delay_seconds': 0,           # No delay - execute immediately
            'enable_sells': True,         # Copy sell trades
            'enable_buys': True,          # Copy buy trades
            'proportional_selling': True
        }
        self.bot = PumpCopyTradingBot(copy_config)
        
        # Statistics
        self.messages_received = 0
        self.trades_detected = 0
        self.trades_executed = 0
        
        print("\n🔧 FIXED COPY TRADING TEST")
        print("=" * 50)
        print("🎯 Using EXACT main.py detection logic")
        print(f"📡 Monitoring {len(self.target_wallets)} wallets")
        print("=" * 50)
    
    async def start_fixed_monitoring(self):
        """Start monitoring using EXACT main.py approach"""
        logger.info("🚀 Starting FIXED copy trading test...")
        
        self.running = True
        reconnect_attempts = 0
        max_reconnect_attempts = 3
        
        while self.running:
            try:
                logger.info("Connecting to WebSocket...")
                
                # Use EXACT WebSocket connection as main.py
                async with websockets.connect(
                    self.ws_url,
                    ping_interval=None,
                    ping_timeout=None
                ) as ws:
                    logger.info("✅ WebSocket connected")
                    
                    # Subscribe using EXACT main.py method
                    subscription_ids = {}
                    
                    for i, wallet in enumerate(self.target_wallets):
                        # Use EXACT subscription format from main.py
                        subscribe_msg = {
                            "jsonrpc": "2.0",
                            "id": str(int(time.time() * 1000) + i),
                            "method": "logsSubscribe",
                            "params": [
                                {"mentions": [wallet]},
                                {"commitment": "confirmed"}
                            ]
                        }
                        
                        await ws.send(json.dumps(subscribe_msg))
                        response = await ws.recv()
                        response_data = json.loads(response)
                        
                        if "result" in response_data:
                            subscription_id = response_data["result"]
                            subscription_ids[f"logs_{wallet}"] = subscription_id
                            logger.info(f"✅ Subscribed to {wallet[:8]}... (ID: {subscription_id})")
                        else:
                            logger.error(f"❌ Failed to subscribe to {wallet[:8]}...: {response}")
                    
                    if not subscription_ids:
                        raise Exception("Failed to establish any subscriptions")
                    
                    logger.info(f"📡 All subscriptions active - monitoring for trades...")
                    
                    # Listen for messages using EXACT main.py approach
                    async for message in ws:
                        try:
                            if not message:
                                continue
                            
                            data = json.loads(message)
                            self.messages_received += 1
                            
                            # Use EXACT message processing from main.py
                            if "method" in data and data["method"] == "subscription":
                                params = data.get("params", {})
                                subscription = params.get("subscription")
                                result = params.get("result")
                                
                                if not (subscription and result):
                                    continue
                                
                                # Get logs and signature using main.py approach
                                logs = result.get("logs", [])
                                signature = result.get("signature")
                                
                                if not (logs and signature):
                                    continue
                                
                                logger.info(f"📥 Message {self.messages_received}: {signature[:8]}... ({len(logs)} logs)")
                                
                                # Use EXACT detection logic from main.py
                                pump_logs = [log for log in logs if any(id in log for id in 
                                           ["BSfD6SHZ", "6EF8rrec", "pAMMBay6"])]
                                
                                if pump_logs:
                                    self.trades_detected += 1
                                    logger.info(f"🎯 TRADE DETECTED #{self.trades_detected}: {signature[:8]}...")
                                    logger.info(f"   Matching logs: {pump_logs[:2]}")
                                    
                                    # Find which wallet triggered this
                                    target_wallet = None
                                    for wallet in self.target_wallets:
                                        if subscription_ids.get(f"logs_{wallet}") == subscription:
                                            target_wallet = wallet
                                            break
                                    
                                    if target_wallet:
                                        logger.info(f"   From wallet: {target_wallet[:8]}...")
                                        
                                        # Execute copy trade using the bot
                                        await self.execute_copy_trade(result, target_wallet, signature)
                                
                                # Print status every 50 messages
                                if self.messages_received % 50 == 0:
                                    logger.info(f"📊 Status: {self.messages_received} messages, {self.trades_detected} trades detected, {self.trades_executed} executed")
                        
                        except json.JSONDecodeError as e:
                            logger.warning(f"Invalid JSON message: {str(e)}")
                        except Exception as e:
                            logger.error(f"Error processing message: {str(e)}")
                            continue
                            
            except websockets.exceptions.ConnectionClosed:
                logger.warning("WebSocket connection closed")
            except Exception as e:
                logger.error(f"WebSocket error: {str(e)}")
                logger.error(traceback.format_exc())
                reconnect_attempts += 1
                
                if reconnect_attempts >= max_reconnect_attempts:
                    logger.error("Max reconnection attempts reached. Stopping test.")
                    self.running = False
                    break
                
                # Wait before reconnecting
                await asyncio.sleep(5)
                logger.info(f"Attempting to reconnect... (attempt {reconnect_attempts})")
    
    async def execute_copy_trade(self, tx_result: dict, target_wallet: str, signature: str):
        """Execute copy trade using the bot"""
        try:
            logger.info(f"🚀 EXECUTING COPY TRADE for {signature[:8]}...")
            
            # Show prominent alert
            alert_message = f"""
🚨 🚨 🚨 COPY TRADE EXECUTION! 🚨 🚨 🚨
Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
Signature: {signature}
Target Wallet: {target_wallet[:8]}...
Detection Method: FIXED (main.py approach)
🚨 🚨 🚨 🚨 🚨 🚨 🚨 🚨 🚨 🚨 🚨 🚨
"""
            
            print(alert_message)
            
            # Write to alert log
            with open("FIXED_COPY_TRADE_ALERT.log", "a") as f:
                f.write(f"{datetime.now().isoformat()}: {alert_message}\n")
            
            # Try to make system sound (macOS)
            try:
                import os
                os.system("afplay /System/Library/Sounds/Sosumi.aiff")
            except:
                pass
            
            # Analyze the transaction using the bot's logic
            trade_info = await self.bot.analyze_target_trade(tx_result, target_wallet)
            
            if trade_info:
                logger.info(f"✅ Trade analysis successful:")
                logger.info(f"   Action: {trade_info['action']}")
                logger.info(f"   Token: {trade_info['token_mint'][:8]}...")
                logger.info(f"   Amount: {trade_info['sol_amount']} SOL")
                
                # Execute the copy trade
                if trade_info['action'].value == 'BUY' and self.bot.copy_config['enable_buys']:
                    logger.info(f"🛒 Executing BUY copy trade...")
                    result = await self.bot._execute_copy_buy(trade_info)
                    if result and result.success:
                        self.trades_executed += 1
                        logger.info(f"✅ BUY COPY TRADE SUCCESSFUL!")
                        logger.info(f"   Transaction: {result.signature}")
                    else:
                        logger.error(f"❌ BUY copy trade failed: {result.error if result else 'Unknown error'}")
                
                elif trade_info['action'].value == 'SELL' and self.bot.copy_config['enable_sells']:
                    logger.info(f"💰 Executing SELL copy trade...")
                    result = await self.bot._execute_copy_sell(trade_info)
                    if result and result.success:
                        self.trades_executed += 1
                        logger.info(f"✅ SELL COPY TRADE SUCCESSFUL!")
                        logger.info(f"   Transaction: {result.signature}")
                    else:
                        logger.error(f"❌ SELL copy trade failed: {result.error if result else 'Unknown error'}")
                else:
                    logger.info(f"⏸️ Trade execution disabled for {trade_info['action'].value}")
            else:
                logger.warning(f"⚠️ Could not analyze trade details for {signature[:8]}...")
                
        except Exception as e:
            logger.error(f"Error executing copy trade: {str(e)}")
            logger.error(traceback.format_exc())
    
    def print_final_stats(self):
        """Print final test statistics"""
        print(f"\n📊 FIXED COPY TRADING TEST RESULTS")
        print("=" * 50)
        print(f"📥 Messages Received: {self.messages_received}")
        print(f"🎯 Trades Detected: {self.trades_detected}")
        print(f"🚀 Trades Executed: {self.trades_executed}")
        
        if self.trades_detected > 0:
            detection_rate = (self.trades_detected / max(self.messages_received, 1)) * 100
            print(f"📈 Detection Rate: {detection_rate:.2f}%")
        
        if self.trades_executed > 0:
            execution_rate = (self.trades_executed / max(self.trades_detected, 1)) * 100
            print(f"⚡ Execution Rate: {execution_rate:.2f}%")
            print("✅ SUCCESS: Copy trading is working!")
        else:
            print("❌ No trades were executed")
            if self.trades_detected > 0:
                print("💡 Trades were detected but not executed (check execution logic)")
            else:
                print("💡 No trades detected (may need more active monitoring)")
        
        print("=" * 50)
    
    async def stop(self):
        """Stop the test"""
        logger.info("🛑 Stopping fixed copy trading test...")
        self.running = False
        await self.bot.close()

async def main():
    """Run the fixed copy trading test"""
    test = None
    try:
        test = FixedCopyTradingTest()
        
        print("🚀 Starting fixed copy trading test...")
        print("📋 Instructions:")
        print("   1. This test uses the EXACT same detection logic as main.py")
        print("   2. It will monitor all configured wallets for trades")
        print("   3. When a trade is detected, it will execute a copy trade")
        print("   4. Press Ctrl+C to stop the test")
        print("   5. Check FIXED_COPY_TRADE_ALERT.log for executed trades")
        print()
        
        await test.start_fixed_monitoring()
        
    except KeyboardInterrupt:
        logger.info("👋 Test stopped by user")
    except Exception as e:
        logger.error(f"❌ Test failed: {str(e)}")
        logger.error(traceback.format_exc())
    finally:
        if test:
            test.print_final_stats()
            await test.stop()

if __name__ == "__main__":
    asyncio.run(main())
